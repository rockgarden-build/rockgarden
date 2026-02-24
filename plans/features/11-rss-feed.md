# Feature 11: RSS Feed

Generate RSS/Atom feed for content updates.

## Status: Not Started

## Goal

```
uv run rockgarden build
```

Produces `_site/feed.xml` (or `/rss.xml`, `/atom.xml`).

## Implementation Plan

### 1. Collect Feed Items

```python
def get_feed_items(pages: list[Page], config: FeedConfig) -> list[Page]:
    """Get pages for feed, sorted by date."""
    items = [p for p in pages if should_include(p, config)]
    items.sort(key=lambda p: p.frontmatter.get("date", ""), reverse=True)
    return items[:config.limit]
```

### 2. Generate Feed XML

Using `feedgen` library:

```python
from feedgen.feed import FeedGenerator

def generate_feed(items: list[Page], config: Config) -> str:
    fg = FeedGenerator()
    fg.title(config.site.title)
    fg.link(href=config.site.base_url)
    fg.description(config.feed.description)

    for page in items:
        fe = fg.add_entry()
        fe.title(page.title)
        fe.link(href=f"{config.site.base_url}{page.url}")
        fe.published(page.frontmatter.get("date"))
        fe.content(page.html, type="html")

    return fg.atom_str(pretty=True)  # or fg.rss_str()
```

## Configuration

```toml
[feed]
enabled = true
format = "atom"  # or "rss"
path = "/feed.xml"
limit = 20
description = "Recent updates"

# Optional: only include certain content
include_paths = ["/blog/", "/posts/"]
```

## Frontmatter Requirements

Pages need `date` field for proper ordering:

```yaml
---
title: My Post
date: 2024-01-15
---
```

## Key Files to Create/Modify

- `output/feed.py` - New module for feed generation
- `config.py` - Add `FeedConfig` dataclass
- `output/builder.py` - Generate feed during build

## Dependencies

```toml
dependencies = [
    "feedgen>=1.0.0",
]
```
