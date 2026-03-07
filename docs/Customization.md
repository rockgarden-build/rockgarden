---
tags: [guide]
---

# Customization

Rockgarden supports progressive customization — start with zero config and add layers as needed.

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

This resolves to `layouts/talk.html`. Resolution order: frontmatter `layout` → collection default → `[theme] default_layout` → `layouts/docs.html`.

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

## Build Hooks

Run shell commands at build lifecycle stages:

```toml
[hooks]
pre_build = ["python scripts/fetch_data.py"]
post_collect = ["python scripts/generate_og.py"]
post_build = ["echo 'Build complete'"]
```

See [[Build Hooks]] for details.
