# Feature 07: Backlinks

Track and display pages that link to the current page.

## Status: Not Started

## Goal

Each page shows a "Backlinks" section listing all pages that reference it via wiki-links.

## Implementation Plan

### 1. Build Backlink Index

During content processing, track outgoing links:

```python
@dataclass
class LinkIndex:
    outgoing: dict[str, set[str]]  # page_slug -> set of linked slugs
    incoming: dict[str, set[str]]  # page_slug -> set of pages linking to it

def build_link_index(pages: list[Page], store: ContentStore) -> LinkIndex:
    # Parse wiki-links from each page
    # Resolve targets
    # Build bidirectional index
```

### 2. Pass Backlinks to Templates

```python
backlinks = link_index.incoming.get(page.slug, set())
backlink_pages = [store.get_by_slug(slug) for slug in backlinks]
```

### 3. Render Backlinks Section

```html
{% if backlinks %}
<section class="backlinks">
  <h2>Backlinks</h2>
  <ul>
    {% for link in backlinks %}
    <li><a href="{{ link.url }}">{{ link.title }}</a></li>
    {% endfor %}
  </ul>
</section>
{% endif %}
```

## Configuration

```toml
[backlinks]
enabled = true
position = "bottom"  # or "sidebar"
```

## Key Files to Create/Modify

- `content/links.py` - New module for link index
- `templates/components/backlinks.html` - Backlinks template
- `templates/page.html` - Include backlinks section
- `output/builder.py` - Build link index during build
