# Architecture

## Build Pipeline

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Content Sources │ ──▶ │  Content Store  │ ──▶ │     Output      │
│ (MD/YAML/JSON)  │     │  (Collections)  │     │  (HTML/Assets)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         ↑                       ↑                       ↑
     pre_build              post_collect             post_build
       hooks                  hooks                    hooks
```

Each build is a full rebuild. The build pipeline is:

1. Load content files → parse frontmatter, extract content
2. Build content store → backlinks index, nav tree, media index
3. For each page: process Obsidian syntax → render markdown → apply template
4. Write HTML + copy assets → generate search index, sitemap, 404

**Current implementation:** markdown files only; in-memory store; no hooks. The diagram reflects the target architecture — see [Collections (Feature 14)](../plans/features/14-collections.md) and [Build Hooks (Feature 15)](../plans/features/15-build-hooks.md) for the planned extensions.

## Design Principles

- **Works with Obsidian vaults as-is.** Point rockgarden at any vault and get a working site. No special folder structure required.
- **Everything is a collection.** Without config, all content is in an implicit default collection. Named collections carve out directory subsets with progressively configurable behavior (schema, non-markdown formats, custom templates, page generation).
- **Custom behavior is additive.** Site-specific customizations are layered on top, not patched into the core.
- **Pre-1.0:** No backwards compatibility guarantees. Breaking changes are acceptable.

## Project Structure

```
rockgarden/
├── src/rockgarden/
│   ├── cli.py              # typer CLI (build, serve)
│   ├── config.py           # rockgarden.toml loading
│   ├── assets.py           # Media index + asset copying
│   ├── urls.py             # URL/slug generation
│   ├── links.py            # Markdown link transformation
│   ├── icons.py            # Icon resolution
│   ├── content/
│   │   ├── store.py        # ContentStore (in-memory)
│   │   ├── loader.py       # File discovery + frontmatter parsing
│   │   └── models.py       # Page dataclass
│   ├── nav/
│   │   ├── tree.py         # Navigation tree builder
│   │   ├── breadcrumbs.py  # Breadcrumb generation
│   │   ├── folder_index.py # Folder index generation
│   │   └── toc.py          # Table of contents extraction
│   ├── obsidian/
│   │   ├── wikilinks.py    # [[link]] processing
│   │   ├── embeds.py       # ![[media]] processing
│   │   ├── transclusions.py # ![[note]] processing
│   │   └── callouts.py     # Callout block conversion
│   ├── render/
│   │   ├── engine.py       # Jinja2 environment + ChoiceLoader
│   │   └── markdown.py     # markdown-it-py setup
│   ├── output/
│   │   ├── builder.py      # Build orchestration
│   │   ├── build_info.py   # Build timestamp + git info
│   │   ├── search.py       # Search index generation
│   │   └── sitemap.py      # Sitemap XML generation
│   ├── templates/          # Default theme templates
│   └── static/             # Default theme CSS + JS (compiled)
├── static-src/input.css    # Tailwind + custom CSS source
└── tailwind.config.js
```

## Core vs. Default Theme

### What the core generator provides

These are always present regardless of theme:

- **Content ingestion** — markdown loading, frontmatter parsing, Obsidian syntax (wikilinks, embeds, transclusions, callouts)
- **Content store** — in-memory store, navigation tree, backlinks index, TOC extraction, search index generation, sitemap
- **Build pipeline** — template rendering, asset copying, 404 generation, CLI
- **Template infrastructure** — Jinja2 environment, ChoiceLoader (3-tier resolution), template context

The core provides no visible output on its own — it depends on a theme to supply templates and styles.

### What the default theme provides

Shipped bundled in the package, active with zero config:

- **Templates** — `base.html`, `page.html`, `folder_index.html`, `404.html`, component templates
- **Layout** — drawer/sidebar layout with mobile hamburger nav
- **CSS** — compiled Tailwind + DaisyUI + callout/link/search styles (`rockgarden.css`)
- **Search UI** — lunr.js + search component + client-side JavaScript
- **Theme switching** — DaisyUI color palette toggle

### Configuration boundary

Config options in `[theme]` are display/rendering concerns — a custom theme may not honour all of them. Config options in `[site]`, `[build]`, `[nav]`, `[toc]`, `[search]`, and `[dates]` are core generator concerns that apply regardless of theme.

```toml
# Core: applies regardless of theme
[site]          # title, source, output, clean_urls, base_url
[build]         # ignore_patterns, icons_dir
[nav]           # hide, labels, sort, link_auto_index
[toc]           # max_depth
[search]        # include_content
[dates]         # date field names

# Theme: display/rendering concerns
[theme]
name = ""                      # theme name (empty = built-in default)
toc = true                     # show TOC panel
backlinks = true               # show backlinks panel
search = true                  # show search UI
daisyui_default = "light"      # DaisyUI color palette (default theme)
daisyui_themes = []            # available palettes for switcher (default theme)
nav_default_state = "collapsed"  # sidebar nav state (default theme)
show_build_info = true         # footer build timestamp (default theme)
show_build_commit = false      # footer git commit info (default theme)
```

## Customization

### Customization levels

| Level | What | How |
|-------|------|-----|
| 0 | Zero-config vault publishing | `rockgarden build` — default theme, no config |
| 1 | Color scheme | `[theme] daisyui_default = "dark"` — swap DaisyUI palette |
| 2 | Patch a component | `_templates/components/nav.html` — override one file |
| 3 | Add content blocks | Extend `page.html` named blocks (`after_heading`, `after_body`, etc.) |
| 4 | Custom page layouts | `_templates/layouts/speaker.html` + frontmatter `layout: speaker` |
| 5 | Custom theme | `_themes/pyohio/` — own base, own CSS, own components |
| 6 | Export default theme | `rockgarden theme export` → copy default theme as starting point |

### Template resolution (ChoiceLoader)

Templates are resolved in this order (first match wins):

1. **Site templates** (`_templates/`) — override individual files
2. **Named theme** (`_themes/<name>/`) — active when `theme.name` is set
3. **Built-in default** — bundled with the package

This allows overriding a single component without touching anything else, or replacing the entire template set with a custom theme.

### Named blocks in page.html

`page.html` exposes Jinja2 blocks as extension points. Empty blocks are hooks with no default output:

| Block | Default content |
|-------|----------------|
| `before_heading` | *(empty hook)* |
| `heading` | `<h1>{{ page.title }}</h1>` |
| `after_heading` | Created/modified dates, tags |
| `body` | `{{ page.html \| safe }}` |
| `after_body` | *(empty hook)* |
| `right_sidebar` | TOC + backlinks |
| `toc` | Table of contents |
| `backlinks` | Backlinks panel |

Use `{{ super() }}` to extend a block rather than replace it.

### Layout system (Phase B)

The current `base.html` hardcodes the drawer/sidebar layout. Phase B will extract this into a `layouts/` directory, enabling per-page layout selection:

```yaml
---
layout: talk   # resolves to layouts/talk.html
---
```

Resolution order: frontmatter `layout` → collection default → `[theme] default_layout` → `layouts/docs.html`.

### Theme export

`rockgarden theme export` (planned, Phase B) copies the bundled default theme templates and CSS source to `_themes/default/` in the site root, making it editable as a starting point for a custom theme.

## Template Context

Variables available in all templates:

| Variable | Type | Description |
|----------|------|-------------|
| `page` | `Page` | Current page (source_path, slug, title, content, html, frontmatter, modified, created, tags) |
| `site` | `dict` | Site config (title, nav, search_enabled, build_info, cache_hash, daisyui_theme, …) |
| `breadcrumbs` | `list[Breadcrumb]` | Navigation trail |
| `toc` | `list[TocEntry] \| None` | Table of contents entries |
| `backlinks` | `NavNode \| None` | Pages that link to the current page |

## Dependencies

- `typer` — CLI
- `markdown-it-py` — Markdown parsing (CommonMark + GFM-like preset)
- `jinja2` — Templates
- `python-frontmatter` — YAML frontmatter
- `tomllib` (stdlib) — Config parsing
- `beautifulsoup4` — HTML parsing for TOC extraction

## Key Decisions

- **Config format:** TOML (`rockgarden.toml`)
- **Package manager:** uv
- **Markdown parser:** markdown-it-py with "gfm-like" preset; Obsidian syntax handled via regex preprocessing
- **CSS:** Tailwind + DaisyUI, compiled via Tailwind CLI. Custom themes must manage their own CSS.
- **Formatting/Linting:** ruff
- **Testing:** pytest
- **Version bumping:** commitizen (conventional commits)
