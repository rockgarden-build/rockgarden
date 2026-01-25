# Feature 12: Base Path Prefix

Support deploying to subdirectories (e.g., `example.com/docs/`).

## Status: Not Started

## Goal

```toml
[site]
base_url = "https://example.com/docs/"
```

All generated URLs include the base path prefix.

## Use Cases

- GitHub Pages project sites: `username.github.io/project-name/`
- Hosting docs under a subdirectory: `example.com/docs/`
- Multiple sites on same domain

## Implementation Plan

### 1. Add Configuration

```python
@dataclass
class SiteConfig:
    title: str = "My Site"
    base_url: str = "/"  # New field
    # ...
```

### 2. URL Generation

Update all URL generation to include base path:

```python
def get_url(slug: str, base_url: str, clean_urls: bool = True) -> str:
    path = get_path(slug, clean_urls)
    return urljoin(base_url, path)
```

### 3. Template Updates

Pass `base_url` to templates:

```html
<a href="{{ site.base_url }}{{ page.url }}">Link</a>
<!-- or with a filter -->
<a href="{{ page.url | absolute_url }}">Link</a>
```

### 4. Asset URLs

Static assets also need the prefix:

```html
<link href="{{ site.base_url }}static/style.css" rel="stylesheet">
<script src="{{ site.base_url }}static/main.js"></script>
```

## Affected Areas

- Wiki-link resolution
- Navigation links
- Breadcrumb links
- Asset paths (CSS, JS, images)
- Search index URLs
- RSS feed links

## Key Files to Modify

- `config.py` - Add `base_url` field
- `urls.py` - Update URL generation functions
- `content/store.py` - Update `resolve_link()`
- `templates/*.html` - Use base_url for all links
- `render/engine.py` - Add `absolute_url` filter
