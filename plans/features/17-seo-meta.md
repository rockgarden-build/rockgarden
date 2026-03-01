# Feature 17: SEO & Meta Tags

Frontmatter-driven meta tags and Open Graph support.

## Status: Complete ✅

## Goal

Pages can define SEO metadata in frontmatter. Default templates render basic `<meta>`, Open Graph, and Twitter Card tags. Structured data (JSON-LD) is left to custom templates/macros.

## Frontmatter Fields

```yaml
---
title: My Talk
description: A talk about Python performance
og_image: /img/talk-banner.png
keywords: python, performance, optimization
---
```

All fields optional. `title` already supported. New fields: `description`, `og_image`, `keywords`.

## Template Output

Default `base.html` would include:

```html
<meta name="description" content="{{ page.description }}">
<meta name="keywords" content="{{ page.keywords }}">

<meta property="og:title" content="{{ page.title }}">
<meta property="og:description" content="{{ page.description }}">
<meta property="og:image" content="{{ page.og_image }}">
<meta property="og:url" content="{{ page.url }}">
<meta property="og:type" content="article">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{ page.title }}">
<meta name="twitter:description" content="{{ page.description }}">
<meta name="twitter:image" content="{{ page.og_image }}">
```

Tags only rendered when the corresponding frontmatter field is present.

## Site-level Defaults

```toml
[site]
title = "My Site"
description = "Site description used as fallback"
og_image = "/img/default-og.png"
```

Page frontmatter overrides site-level defaults.

## Implementation Plan

### 1. Config

Add optional `description` and `og_image` to `SiteConfig`.

### 2. Page Model

Surface `description`, `og_image`, `keywords` from frontmatter in the `Page` dataclass (or access directly from `page.frontmatter`).

### 3. Template Component

Create `templates/components/meta.html` with conditional meta tag rendering. Include in `base.html`.

## Key Files to Create/Modify

- `config.py` — Add site-level SEO defaults
- `templates/components/meta.html` — New meta tag component
- `templates/base.html` — Include meta component in `<head>`
