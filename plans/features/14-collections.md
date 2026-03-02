# Feature 14: Collections

Unified content model with progressive customization. Everything is a collection.

## Status: Complete

## Goal

Without config, all content lives in an implicit **default collection** — current behavior, unchanged. Defining a named collection in config carves out a directory into a separate namespace. Content claimed by a named collection is removed from the default collection.

Collections are progressively configurable:

```
Just a name + source  → namespace/grouping only, renders markdown pages normally
  + formats           → load YAML/JSON/TOML in addition to markdown
  + template/url      → custom page generation
  + pages = false     → data-only, queryable but no output
  + nav = true        → appears in sidebar
  + model             → typed entry validation via Pydantic BaseModel
```

## Use Cases

- Conference site: talks, speakers, sponsors as YAML, each generating a page
- Data-only collections: schedule slots queryable from templates but not generating pages
- Aggregate pages: schedule template queries talks + rooms to build a grid
- Cross-references: speaker page lists their talks, talk page links to speakers
- Obsidian vault: characters/ as a collection, characters/pcs/ as a nested collection with a model
- Hook scripts: read `.rockgarden/content.json` to generate OG images, search indexes, or JSON exports

## Configuration

```toml
# Obsidian vault use case — nested collections
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
pages = false
```

Models are defined as Python files, not in TOML — see [Content Models](#content-models) below.

## Nesting Behavior

Collections can nest. Content in a nested collection belongs to all parent collections:

- `collections.characters` returns ALL content in characters/ (including pcs/ and npcs/)
- `collections.pcs` returns only content in characters/pcs/
- A PC entry is in both `collections.pcs` AND `collections.characters`

This gives "NPC extends Character" behavior without explicit inheritance — it falls out of directory nesting.

## Collection Config Fields

| Field | Required | Default | Description |
|---|---|---|---|
| `name` | yes | — | Collection name, used as `collections.<name>` in templates |
| `source` | yes | — | Directory containing collection files (relative to source root) |
| `template` | no | — | Template to render each entry |
| `url_pattern` | no | — | URL pattern with `{field}` placeholders |
| `pages` | no | `true` | Whether to generate pages (requires template + url_pattern) |
| `nav` | no | `false` | Whether generated pages appear in sidebar nav |
| `model` | no | — | Model name — resolved to a Pydantic BaseModel via cascade (see below) |

## Content Models

Models are optional Python files containing a Pydantic `BaseModel` subclass. When a collection has `model = "speaker"`, rockgarden looks for a `Speaker` class using this cascade (first match wins):

1. `_models/speaker.py` — site-level (highest priority)
2. `_themes/<active-theme>/_models/speaker.py` — theme-provided

Class name is the title-cased filename (`speaker.py` → `Speaker`).

Example:

```python
# _models/speaker.py
from pydantic import BaseModel

class Speaker(BaseModel):
    name: str
    bio: str = ""
    photo: str | None = None
```

Without a model, collection entries are plain dicts. With a model, entries are validated and coerced on load — missing required fields produce a build error.

## Data Layer

The `ContentStore` stays in-memory and becomes collection-aware. No external database required.

```python
store.list_content()                              # default collection
store.list_content("speakers", sort_by="name")    # named collection
store.get_content("speakers", slug="dave")
```

For hook scripts that need access to collected data, content is exported to JSON at `.rockgarden/content.json` after collection. Templates use Jinja2's built-in filters for querying:

```jinja
{# Speaker page: list their talks #}
{% set speaker_talks = collections.talks | selectattr("speaker_slug", "equalto", entry.slug) | list %}

{# Schedule page: group by time slot #}
{% for time, talks in collections.talks | groupby("start_time") %}
```

## Implementation Plan

### 1. Config

```python
class CollectionConfig(BaseModel):
    name: str
    source: str
    template: str | None = None
    url_pattern: str | None = None
    pages: bool = True
    nav: bool = False
    model: str | None = None
```

Added to the root `Config` model:
```python
collections: list[CollectionConfig] = Field(default_factory=list)
```

### 2. Model Resolution

A `resolve_model(name, config, theme_dir)` function that walks the cascade and returns the Pydantic BaseModel class (or `None` if no model file is found).

### 3. Collection-Aware ContentStore

Extend `ContentStore` to track collection membership. Without config, all content is in the default collection. Named collections carve out subsets.

```python
class ContentStore:
    def __init__(self, pages: list[Page], clean_urls: bool = True): ...
    def add_collection(self, name: str, entries: list[dict]): ...
    def list_content(self, collection: str | None = None, **filters) -> list[dict]: ...
    def get_content(self, collection: str, slug: str) -> dict | None: ...
    def export_json(self, path: Path) -> None:
        """Export all collections to JSON for hook scripts."""
```

### 4. Collection Loader

Load files from collection source directories. Supported formats:
- `.yaml` / `.yml` — parsed as dict of fields
- `.json` — parsed as dict of fields
- `.toml` — parsed as dict of fields
- `.md` — frontmatter as fields, body rendered as HTML and available as `content`

Each entry gets a `slug` derived from filename (or overridden by a `slug` field). If a model is configured, entries are validated through it on load.

### 5. Template Context

All collections available in every template as `collections.<name>` (list of dicts or model instances serialized to dict). Jinja2's built-in filters handle querying.

### 6. Page Generation

For collections with `pages = true` and a `template` + `url_pattern`:
- Generate one page per entry
- URL from `url_pattern` with `{field}` replaced by entry fields
- Render using specified template with entry data in context

### 7. Nav Integration

For collections with `nav = true`:
- Add generated pages to nav tree
- Grouped under a section named after the collection

## Key Files to Create/Modify

- `content/store.py` — Extend with collection awareness and JSON export
- `content/collection.py` — New module: collection loading, format parsing, model resolution
- `config.py` — Add `CollectionConfig` Pydantic BaseModel; add `collections` field to `Config`
- `output/builder.py` — Load collections, generate pages, pass to templates
- `render/engine.py` — Add collections to template context

## Dependencies

- `pydantic>=2.0` (added for config migration)
- `pyyaml` (already used by python-frontmatter)
- `tomllib` (stdlib in 3.11+)
- `json` (stdlib)
