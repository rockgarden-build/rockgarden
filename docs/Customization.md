---
tags: [guide]
---

# Customization

Rockgarden supports progressive customization — start with zero config and add layers as needed.

## Static Files

Place files in `_static/` at your site root to have them copied as-is to the output root during build. Useful for deployment platform files (`_redirects`, `_headers`), favicons, `robots.txt`, and verification files.

Files in `_static/` are copied late in the build and overwrite any generated output at the same path.

## Custom CSS and JavaScript

Drop files in `_styles/` and `_scripts/` at your site root. They are automatically copied to the output directory and injected as `<link>` / `<script>` tags.

## Template Overrides

Place template files in `_templates/` to override individual components without replacing the entire theme. For example, `_templates/components/nav.html` overrides just the navigation component.

Templates are resolved in order: site `_templates/` → named theme → built-in default. First match wins.

## Named Blocks

`page.html` exposes Jinja2 blocks as extension points:

| Block            | Default content              |
| ---------------- | ---------------------------- |
| `before_heading` | _(empty hook)_               |
| `heading`        | `<h1>{{ page.title }}</h1>`  |
| `after_heading`  | Created/modified dates, tags |
| `body`           | `{{ page.html \| safe }}`    |
| `after_body`     | _(empty hook)_               |
| `right_sidebar`  | TOC + backlinks              |

Use `{% extends "page.html" %}` and override specific blocks. Use `{{ super() }}` to extend a block rather than replace it.

## Layout System

Layouts define page structure. The default layout is `layouts/default.html` (sidebar navigation with content area).

Select a layout per page via frontmatter:

```yaml
---
layout: talk
---
```

This resolves to `layouts/talk.html`. Resolution order: frontmatter `layout` → collection default → `[theme] default_layout` → `layouts/default.html`.

## Theme Export

To fully customize the default theme, export it as a starting point:

```bash
rockgarden theme export
```

This copies all default templates and CSS source to `_themes/default/` and sets `theme.name = "default"` in your config.

## Custom Themes

Place a complete theme in `_themes/<name>/` and set `theme.name` in config:

```toml
[theme]
name = "mytheme"
```

A theme provides its own templates, styles, and scripts.

## Collections

Collections partition content into named subsets scoped by directory. Each collection can have its own templates, URL patterns, data formats (YAML, JSON, TOML), and Pydantic model validation.

```toml
[[collections]]
name = "speakers"
source = "speakers"
template = "speaker.html"
url_pattern = "/speakers/{slug}/"
```

See [[Configuration]] for full collection options.

## Icons

Rockgarden bundles the full [Lucide](https://lucide.dev) icon set. Icons are available in both templates and markdown content.

### In Templates

Use the `icon` global function or filter to render inline SVG:

```jinja2
{{ icon("map-pin") }}
{{ "github" | icon }}
```

Missing icons render as empty strings and log a warning.

### In Markdown

Use `:lucide-name:` syntax to insert icons inline:

```markdown
Click :lucide-settings: to configure.
Find us at :lucide-map-pin: 123 Main St.
```

Only icons that resolve successfully are replaced — unrecognized patterns are left as literal text, so the syntax degrades gracefully in other markdown renderers. Additional icon libraries may be supported in the future.

Icons inside code blocks (fenced or inline) are never processed.

To disable inline icon processing, set `inline_icons = false` in `[build]`:

```toml
[build]
inline_icons = false
```

### Custom Icons

Place custom SVG files in an icons directory and set `build.icons_dir`:

```toml
[build]
icons_dir = "_icons"
```

Custom icons at `_icons/lucide/<name>.svg` override the bundled version of that icon.

## Build Hooks

Run shell commands at build lifecycle stages:

```toml
[hooks]
pre_build = ["python scripts/fetch_data.py"]
post_collect = ["python scripts/generate_og.py"]
post_build = ["echo 'Build complete'"]
```

See [[Build Hooks]] for details.
