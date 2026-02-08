# PyOhio Feature Gap Analysis & Rockgarden Roadmap

## Context

Rockgarden's vision is progressive customization: zero-config for Obsidian vaults / plain markdown folders, scaling up to a general-purpose SSG. The PyOhio conference website (Astro + Python pre-processing) serves as the benchmark for that upper end. This document catalogs every capability the PyOhio site uses, maps each against rockgarden, and proposes roadmap items.

## PyOhio Site Summary

A multi-section conference website:
- **Data pipeline**: Python scripts fetch talks/speakers/sponsors from PreTalx + PyOhio APIs → YAML files
- **Typed collections**: 66 talks, 44 speakers, sponsors (tiered), individual sponsors — all YAML with schemas
- **Dynamic routes**: One page per talk, one per speaker, generated from collections
- **Aggregate pages**: Schedule grid (talks + rooms + times), sponsor index (grouped by tier)
- **3 layouts**: Default, Print (room signs), Markdown
- **Components**: Hero, feature cards, sponsor cards, structured data, nav dropdowns
- **Styling**: Tailwind + SCSS, dark/light mode via CSS custom properties
- **Subpath deployment**: `/2025/`
- **SEO**: Sitemaps, Open Graph, Twitter Cards, JSON-LD (Event, Person, VideoObject)
- **Accessibility**: WCAG 2.1 AA, skip links, ARIA, keyboard nav, focus indicators

---

## Feature Mapping

### Already Covered

| PyOhio Capability | Rockgarden |
|---|---|
| Markdown content pages | ✅ Feature 02 |
| Frontmatter metadata | ✅ Content loader |
| Navigation (sidebar/breadcrumbs) | ✅ Feature 06 |
| Dark/light mode toggle | ✅ DaisyUI theme toggle |
| Responsive design | ✅ Tailwind CDN |
| Template overrides | ✅ Feature 10 (ChoiceLoader) |
| Clean URLs | ✅ Config option |
| Asset copying (images, media) | ✅ Feature 04 |

### Already Planned (Existing Feature Docs)

| PyOhio Capability | Rockgarden Feature | Status |
|---|---|---|
| Multiple layouts | Feature 10 Phase B - Layout System | Not started |
| Reusable components | Feature 09 - Macros | Not started |
| Subpath deployment (`/2025/`) | Feature 12 - Base Path Prefix | Not started |
| Sitemap, 404 page | Feature 13 - Polish | Not started |
| Client-side search | Feature 08 - Search | Not started |
| RSS/Atom feed | Feature 11 - RSS Feed | Not started |

### New Capabilities Needed

#### N1. Collections

**Problem**: Rockgarden only discovers `.md` files. PyOhio needs YAML/JSON content (talks, speakers, sponsors) that also becomes pages. Hooks need structured access to collected data for derived asset generation (OG images, etc.). Obsidian vaults have directory-based content types (characters, locations) that benefit from type-specific behavior.

**Everything is a collection.** Without config, all content lives in an implicit **default collection** — current behavior, unchanged. Defining a named collection in config carves out a directory into a separate namespace. Content claimed by a named collection is removed from the default collection.

**Collections are progressively configurable:**

```
Just a name + source  → namespace/grouping only, renders markdown pages normally
  + model             → schema/field expectations
  + formats           → load YAML/JSON/TOML in addition to markdown
  + template/url      → custom page generation
  + pages = false     → data-only, queryable but no output
  + nav = true        → appears in sidebar
```

**Collections can nest.** Content in a nested collection belongs to all parent collections:
```toml
# Obsidian vault use case
[[collections]]
name = "characters"
source = "characters"

[[collections]]
name = "pcs"
source = "characters/pcs"
model = "pc"

[[collections]]
name = "npcs"
source = "characters/npcs"
model = "npc"

# Conference site use case
[[collections]]
name = "speakers"
source = "_data/speakers"
template = "speaker.html"
url_pattern = "/speakers/{slug}/"

[[collections]]
name = "schedule"
source = "_data/schedule"
pages = false            # data-only, queryable but no pages
```

- `collections.characters` returns ALL content in characters/ (including pcs/ and npcs/)
- `collections.pcs` returns only content in characters/pcs/
- A PC entry is in both `collections.pcs` AND `collections.characters`
- This gives "NPC extends Character" behavior without explicit inheritance — it falls out of nesting

**Non-markdown files** are ignored unless a collection config enables other formats for that collection.

**Models** = optional schema attached to a collection:
```toml
[models.pc]
fields = ["name", "class", "level", "race"]

[models.npc]
fields = ["name", "location", "faction"]
```
Models define expected fields — useful for validation, template rendering, and type-specific behavior. A collection without a model is just a namespace.

**Data layer — in-memory ContentStore:**

The existing `ContentStore` stays in-memory (Python dicts/dataclasses). No SQLite required. The store is collection-aware:

```python
store.list_content()                              # default collection
store.list_content("speakers", sort_by="name")    # named collection
store.get_content("speakers", slug="dave")
```

For hook scripts that need access to collected data, the store is serialized to JSON at `.rockgarden/content.json` after collection. This enables:
- OG image generation: hook reads content JSON, generates images
- JSON API export: hook transforms content JSON
- Search index: hook builds index from content data
- Any derived asset that needs access to collected data

#### N2. Build Hooks

PyOhio runs Python scripts to fetch API data before build. Derived asset generation (OG images) needs access to collected data. Rockgarden has no lifecycle hooks.

**Approach**: Shell commands in config, run at defined stages:

```toml
[hooks]
pre_build = ["python scripts/fetch_data.py"]
post_collect = ["python scripts/generate_og_images.py"]
post_build = ["npx tailwindcss -o _site/css/styles.css --minify"]
```

| Stage | When | Content Data Available | Use Cases |
|---|---|---|---|
| `pre_build` | Before content loading | No | Data fetching, file generation |
| `post_collect` | After content collected, before render | Yes (JSON export) | Derived assets (OG images), search index, data transforms |
| `post_build` | After all output written | Yes (JSON export) | Asset compilation, optimization, validation |

The `post_collect` stage is critical — it runs after content is collected and exported to `.rockgarden/content.json`, so hook scripts can read and query content data to generate derived assets.

#### N3. Static Assets (Custom CSS & JS)

PyOhio uses SCSS + Tailwind. Rockgarden has no custom CSS/JS support.

**Approach**: Convention-based. Files in `_styles/` and `_scripts/` are copied to output and injected into templates. No compilation by default — just plain CSS and JS. Users who want SCSS, Tailwind JIT, or bundling use build hooks (N2) to compile, and custom templates to reference the output.

Default templates would include any files found in these directories. Custom templates can reference whatever they want.

#### N4. SEO & Meta Tags

PyOhio has per-page meta tags, Open Graph, Twitter Cards, JSON-LD structured data.

**Approach**: Frontmatter fields (`description`, `og_image`, `keywords`) surfaced in template context. Default templates include basic `<meta>` tags. Structured data (JSON-LD) is left to custom templates / macros since it's highly site-specific.

```yaml
---
title: My Talk
description: A talk about Python
og_image: /img/talk-banner.png
---
```

#### N6. Broken Link Handling

Neither Obsidian Publish nor Quartz handles this well. Publish renders broken links as normal clickable links leading to 404. Quartz optionally renders them as faded, non-clickable text but with no build-time feedback.

**Approach**: Better than both — visual indication in output AND build-time reporting.

**Output rendering:**
- Broken links render as `<a class="internal-link broken">` with no `href` (not clickable)
- Styled faded/muted (reduced opacity, secondary color) to visually distinguish from working links
- Similar to Quartz's `.broken` treatment but always enabled

**Build-time feedback:**
- Log a warning per broken link during build (page, link target)
- Print a summary at build end: "Built 42 pages. 3 broken links found:" followed by the list
- Non-fatal — build completes, just reports the issues

#### N5. Accessibility Defaults

PyOhio targets WCAG 2.1 AA. Rockgarden's default templates lack skip links, ARIA landmarks, focus indicators.

**Approach**: Improve the built-in templates. No new feature system — just better HTML:
- Skip-to-content link
- ARIA landmark roles (`<nav>`, `<main>`, `<aside>`)
- Focus-visible styles
- Semantic heading hierarchy

---

## Proposed Roadmap

Two-phase approach: ship the zero-config Obsidian vault experience first, then build toward general-purpose SSG (PyOhio benchmark) as the 0.9 prerelease target.

### Phase A: Zero-Config Release

Complete the Obsidian vault experience. These are what zero-config users will notice.

| ID | Feature | Complexity | Notes |
|---|---|---|---|
| **05** | Callouts | Low | Obsidian callout syntax. High visibility for vault users. |
| **07** | Backlinks | Low | Pages that link to current page. Core Obsidian/Quartz feature. |
| **N6** | Broken Link Handling | Low-Med | Visual indication + build warnings + summary report. |
| **13** | Polish (sitemap, 404, TOC) | Medium | Already planned. |
| **N5** | Accessibility Defaults | Low | Template improvements only. |
| **08** | Search | Medium | Client-side index. Expected by Quartz users. |

### Phase B: General SSG / PyOhio (0.9 Prerelease)

Collections, hooks, and the features needed to rebuild PyOhio in rockgarden.

| ID | Feature | Complexity | Notes |
|---|---|---|---|
| **10B** | Layout System | Medium | Already planned. Per-page layout via frontmatter. Prerequisite for different page types. |
| **N1** | Collections | High | Unified content model. Progressive: namespace → schema → templates → page generation. |
| **N2** | Build Hooks | Low-Med | Shell commands at pre/post-build + post-collect. Enables data pipelines, derived assets. |
| **12** | Base Path Prefix | Low | Already planned. Required for subpath deployment (`/2025/`). |
| **N3** | Static Assets (CSS/JS) | Low | `_styles/` and `_scripts/` conventions. Quick win. |
| **N4** | SEO & Meta Tags | Medium | Frontmatter-driven meta, OG tags. Default template updates. |

### Phase C: Enhanced Features

Nice-to-haves, not required for either release target.

| ID | Feature | Complexity | Notes |
|---|---|---|---|
| **09** | Macros | Medium | Already planned. Jinja2 component reuse. |
| **11** | RSS Feed | Low | Already planned. |
| **N7** | Config Validator | Low | Validate config file on load, warn about unknown fields, deprecated locations. UX improvement. |

---

## External Data Lifecycle

Collections can be sourced from external APIs (e.g., PyOhio fetching speaker/talk/schedule data from a CFP site). The fetch-and-transform step is **separate from the build pipeline** — not a build hook.

### Workflow

1. **Refresh**: `rockgarden refresh` (or similar) runs configured fetch scripts, transforms API data, and writes local files into collection directories. These are marked as externally-sourced.
2. **Build/serve**: Reads those local files like any other collection content. No re-fetching. Watch mode rebuilds on site content changes but doesn't trigger refresh.
3. **Archive**: Remove the external source config. The local files become regular collection content. No API dependency.

### Refresh/TTL Policy

Each external source can define a refresh policy:
- Always re-fetch on `refresh`
- Only re-fetch if data is older than a configured TTL (e.g., speaker bios change rarely, schedule changes frequently)

### Why Not Build Hooks

- Hooks run every build. API fetches during `serve` watch loops are wasteful and slow.
- Separating refresh from build means watch mode works naturally — it watches local files only.
- The "archive" transition is just a config change since the files are already local.

### Collection Config Sketch

```toml
[[collections]]
name = "speakers"
source = "_data/speakers"
external = "scripts/fetch_speakers.py"
refresh = "1h"    # TTL — only re-fetch if older than 1 hour

[[collections]]
name = "schedule"
source = "_data/schedule"
external = "scripts/fetch_schedule.py"
refresh = "always" # re-fetch every time
```

---

## Design Decisions

1. **Everything is a collection**: Without config, all content is in an implicit default collection. Named collections carve out subsets. Content claimed by a named collection is removed from the default.

2. **In-memory content store**: ContentStore uses Python dicts/dataclasses, not SQLite. Content is exported to JSON for hook script access. SQLite can be added later behind the same API if needed.

3. **Non-markdown file handling**: Non-markdown files (YAML/JSON/TOML) are ignored unless a collection config enables other formats. Without config, only markdown is loaded.

4. **Hook stages**: Three stages: `pre_build` (before loading), `post_collect` (after content collected, before render), `post_build` (after output written). The `post_collect` stage is needed for derived asset generation that requires content data.

5. **Nav integration for collections**: Collection-generated pages do NOT appear in sidebar nav by default. Per-collection config to opt in.

6. **Content Models vs Collections**: Models are optional schema info attached to a collection. The inheritance concept (`NPC extends Character`) is replaced by nested collections — content in `characters/npcs/` belongs to both the `npcs` and `characters` collections.

7. **External data is separate from build**: Fetching data from APIs is a `refresh` command, not a build hook. Build only reads local files. This keeps watch/serve fast and enables archiving by removing the external source config.
