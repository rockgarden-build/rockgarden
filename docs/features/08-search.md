# Feature 08: Search

Client-side full-text search using a generated JSON index.

## Status: Not Started

## Goal

```
uv run rockgarden build
```

Produces:
- `_site/search-index.json` - Searchable content index
- Search UI in header/sidebar

## Implementation Plan

### 1. Generate Search Index

```python
def build_search_index(pages: list[Page]) -> list[dict]:
    return [
        {
            "slug": page.slug,
            "title": page.title,
            "content": strip_html(page.html),  # Plain text
            "tags": page.frontmatter.get("tags", []),
        }
        for page in pages
    ]
```

### 2. Client-Side Search Library

Options:
- **Fuse.js** - Fuzzy search, small footprint
- **Lunr.js** - Full-text search with stemming
- **MiniSearch** - Lightweight, good defaults

### 3. Search UI

```html
<div class="search">
  <input type="search" placeholder="Search..." id="search-input">
  <div class="search-results" id="search-results"></div>
</div>
```

### 4. Search Script

```javascript
// Load index
const index = await fetch('/search-index.json').then(r => r.json());
const fuse = new Fuse(index, { keys: ['title', 'content', 'tags'] });

// Handle input
searchInput.addEventListener('input', (e) => {
  const results = fuse.search(e.target.value);
  renderResults(results);
});
```

## Configuration

```toml
[search]
enabled = true
include_content = true  # Index full content vs. just titles
```

## Key Files to Create/Modify

- `output/search.py` - New module for index generation
- `templates/components/search.html` - Search UI
- `templates/base.html` - Include search in header
- `output/builder.py` - Generate search index during build
