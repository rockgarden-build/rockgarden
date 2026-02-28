# Feature 10: Progressive Customization

Enable customization from zero-config to fully custom site generation.

## Status: In Progress (Phase A complete, Phase B planned)

## Customization Levels

| Level | What | How |
|-------|------|-----|
| 0 | Zero-config vault publishing | `rockgarden build` — default theme, no config |
| 1 | Color scheme | `[theme] daisyui_default = "dark"` — swap DaisyUI palette |
| 2 | Patch a component | `_templates/components/nav.html` — override one file |
| 3 | Add content blocks | Extend `page.html` named blocks (`after_heading`, `after_body`, etc.) |
| 4 | Custom page layouts | `_templates/layouts/speaker.html` + frontmatter `layout: speaker` |
| 5 | Custom theme | `_themes/pyohio/` — own base, own CSS, own components |
| 6 | Export default theme | `rockgarden theme export` → copy default theme as starting point |

## Core vs. Default Theme

See `docs/architecture.md` for the full boundary. In summary:

- **Core** provides content ingestion, the content store, template infrastructure, and the build pipeline. It has no visible output without a theme.
- **Default theme** provides all templates, the sidebar/drawer layout, DaisyUI + Tailwind CSS, and the search UI. It ships bundled and is active with zero config.

## Template Resolution

Templates are resolved by `render/engine.py` using a 3-tier ChoiceLoader:

1. `_templates/` — site-level overrides (highest priority)
2. `_themes/<name>/` — active when `[theme] name` is set
3. Built-in package templates — always the fallback

A custom theme set with `theme.name = "pyohio"` loads templates from `_themes/pyohio/`. Any templates not present in the theme directory fall through to the built-in defaults.

## Configuration Boundary

Theme-related settings live under `[theme]`:

```toml
[theme]
name = ""                        # theme directory; empty = built-in default
toc = true                       # show TOC panel (theme-general)
backlinks = true                 # show backlinks panel (theme-general)
search = true                    # show search UI (theme-general)
daisyui_default = "light"        # DaisyUI palette (default theme)
daisyui_themes = []              # available palettes for switcher (default theme)
nav_default_state = "collapsed"  # sidebar nav state (default theme)
show_build_info = true           # footer build info (default theme)
show_build_commit = false        # footer git commit (default theme)
```

## Named Blocks in page.html

`page.html` exposes Jinja2 blocks as extension points. A site can extend `page.html` and override only the blocks it needs, using `{{ super() }}` to preserve default content:

```jinja2
{# _templates/page.html #}
{% extends "page.html" %}

{% block after_heading %}
{{ super() }}
{% if page.frontmatter.beyondUrl %}
<a href="{{ page.frontmatter.beyondUrl }}">{{ page.title }} on D&D Beyond</a>
{% endif %}
{% endblock %}
```

Available blocks:

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

## Phase A: Complete ✅

- [x] DaisyUI theme selection via `[theme] daisyui_default`
- [x] Named blocks in `page.html` and `folder_index.html`
- [x] Template override via `_templates/` (ChoiceLoader)
- [x] Named theme via `_themes/<name>/` (ChoiceLoader)
- [x] Config separation: display/rendering settings moved to `[theme]`

## Phase B: Layout System

### Problem

`base.html` currently hardcodes the drawer/sidebar layout. A custom theme must replace `base.html` entirely for a different outer structure. There is no per-page layout variation.

### Design

**`base.html` → minimal HTML skeleton** (head, body wrapper, script injection only — no layout structure)

**`layouts/` directory** in default theme:
- `layouts/docs.html` — current sidebar/drawer layout (extracted from current `base.html`)
- `layouts/page.html` — simple full-width, no sidebar

**Per-page layout via frontmatter:**
```yaml
---
layout: talk   # resolves to layouts/talk.html
---
```

**`resolve_layout(page, config, env)` in `render/engine.py`:**
1. `page.frontmatter.get("layout")` → `layouts/<name>.html`
2. Collection default layout (planned with collections feature)
3. `config.theme.default_layout` → `layouts/<name>.html`
4. Default: `layouts/docs.html`

**`page.html` and `folder_index.html`** extend `layout_template` (a variable) rather than `base.html`:
```jinja2
{% extends layout_template %}
```

The `layout_template` string is injected into the render context by `render_page()`.

### Tasks

- [ ] Refactor `base.html` to minimal skeleton
- [ ] Create `layouts/docs.html` (current sidebar layout extracted from `base.html`)
- [ ] Add `resolve_layout()` to `render/engine.py`
- [ ] Update `render_page()` to inject `layout_template`
- [ ] Update `page.html` and `folder_index.html` to extend `layout_template`
- [ ] Add `theme.default_layout` config field (already added to `ThemeConfig`)

## Phase B: Theme Export CLI

**`rockgarden theme export`** copies the bundled default theme to `_themes/default/` in the site root and sets `theme.name = "default"` in `rockgarden.toml`. This gives users a complete, editable starting point.

The `theme` CLI group may grow over time (e.g., `rockgarden theme list`, `rockgarden theme install`).

### Tasks

- [ ] Add `theme` command group to `cli.py`
- [ ] Implement `rockgarden theme export` subcommand
- [ ] Document the exported directory structure

## Phase C: Documentation

- [ ] Full template override guide in `docs/`
- [ ] Custom theme creation guide (with PyOhio as the worked example)
- [ ] Available blocks + context variables reference
