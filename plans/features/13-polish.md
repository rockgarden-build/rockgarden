# Feature 13: Polish

Dark mode, responsive design, sitemap, and other finishing touches.

## Status: Not Started

## Components

### Dark Mode ✅ (via DaisyUI)

Already supported via DaisyUI theme toggle. Users can:
- Set default theme in config: `[theme] daisyui = "dark"`
- Toggle via theme switch in UI
- System preference detection

### Responsive Design ✅ (via Tailwind)

Current templates use Tailwind responsive utilities:
- Mobile: Drawer nav hidden, hamburger menu
- Desktop: Sidebar visible

### Sitemap

Generate `sitemap.xml` for search engines:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/page/</loc>
    <lastmod>2024-01-15</lastmod>
  </url>
</urlset>
```

Implementation:
```python
def generate_sitemap(pages: list[Page], base_url: str) -> str:
    urls = []
    for page in pages:
        urls.append({
            "loc": f"{base_url}{page.url}",
            "lastmod": page.source_path.stat().st_mtime,
        })
    return render_sitemap_xml(urls)
```

### Table of Contents

Auto-generate TOC from page headings:

```python
def extract_toc(html: str) -> list[TocEntry]:
    """Extract h2-h4 headings for TOC."""
```

Display in sidebar or at top of long pages.

### Build Info Footer

Show build timestamp and git commit:

```html
<footer>
  Built {{ build_time }} | {{ git_commit[:7] }}
</footer>
```

### 404 Page

Generate custom 404 page from `404.md` if present, otherwise use default template.

## Configuration

```toml
[polish]
sitemap = true
toc = true
build_info = true
```

## Key Files to Create/Modify

- `output/sitemap.py` - Sitemap generation
- `output/toc.py` - Table of contents extraction
- `templates/components/toc.html` - TOC template
- `templates/components/footer.html` - Build info footer
- `templates/404.html` - Default 404 page
