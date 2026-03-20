# Rockgarden MCP Server Generator — Approach

## Context

Generate an MCP server automatically from Rockgarden site content. Separate package (`rockgarden-mcp`). Zero-config defaults, progressive customization. Content loaded once on start (no file watching for now).

## Content Pipeline

The MCP server needs rich content (full markdown bodies + frontmatter + metadata). Two options for getting it there:

### Option A: Enriched content.json

Expand Rockgarden's existing `.rockgarden/content.json` export to include full markdown content (currently metadata-only). The MCP server reads this file — no direct dependency on rockgarden.

- Add a `[build] export_content = true` config option (or always export when `.rockgarden/` exists)
- Include `content` (raw markdown) and optionally `html` fields in the export
- `rockgarden-mcp` only needs to read JSON — very lightweight

### Option B: Dedicated compile step

`rockgarden-mcp compile` imports rockgarden's content loader and writes its own optimized data file (e.g. `.rockgarden/mcp-content.json`).

- More control over the output format
- Adds rockgarden as a build-time dependency (not runtime)

**Recommendation: Option A** — enrich content.json during `rockgarden build`. Simpler, single source of truth, and the MCP server stays dependency-light. The content.json format already has the right shape, just needs the body fields added.

This means a small change to rockgarden core: always export content.json (not just when hooks exist), and include markdown content in the export.

## Zero-Config Default

```bash
# After building the rockgarden site
rockgarden-mcp serve /path/to/project
```

Auto-generates these MCP capabilities:

### Tools
- **`search(query, collection?, tags?)`** — keyword search across all pages and collections
- **`get_page(slug)`** — retrieve page by slug (markdown + frontmatter + metadata)
- **`list_pages(tag?, collection?, limit?, offset?)`** — list/filter pages
- **`list_collections()`** — list available collections with entry counts
- **`get_collection_entries(collection, limit?, offset?)`** — list entries in a collection
- **`get_site_structure()`** — site title, nav tree, collections overview

### Resources
- `page://{slug}` — each page as a resource (markdown + frontmatter)
- `collection://{name}/{slug}` — collection entries as resources

### Prompts
- **`answer_from_content(question)`** — searches content and constructs a prompt to answer from it

## Progressive Customization

### Level 1: Config file (`rockgarden-mcp.toml`)

```toml
[server]
name = "my-site"  # MCP server name

[content]
include_collections = ["docs", "products"]  # default: all
exclude_patterns = ["_drafts/**"]

[search]
fields = ["title", "content", "tags"]  # what's searchable
```

### Level 2: Collection-aware tools

Collections with defined schemas (Pydantic models in rockgarden) get typed tool parameters auto-generated from model fields:

```toml
[collections.products]
searchable_fields = ["name", "category", "price"]
# Auto-generates: search_products(name?, category?, price_max?)
```

### Level 3: Custom tool definitions

```toml
[[tools]]
name = "find_recipe"
description = "Find recipes by ingredient or cuisine"
collection = "recipes"
filters = ["ingredients", "cuisine", "difficulty"]
```

### Level 4: Python extensions

```python
# _mcp/tools.py — auto-discovered
from rockgarden_mcp import tool

@tool
def recommend_related(slug: str, content_store) -> list[dict]:
    """Find pages related to the given page."""
    ...
```

## Package Architecture

```
rockgarden-mcp/
├── src/rockgarden_mcp/
│   ├── __init__.py
│   ├── cli.py              # Typer CLI: rockgarden-mcp serve
│   ├── config.py           # MCP config (Pydantic, reads rockgarden-mcp.toml)
│   ├── server.py           # FastMCP server setup, tool/resource registration
│   ├── content.py          # Load + index content.json
│   ├── search.py           # Keyword search implementation
│   ├── tools.py            # Built-in tool definitions
│   ├── resources.py        # Resource provider
│   ├── prompts.py          # Built-in prompt templates
│   └── extensions.py       # Custom tool loader (_mcp/*.py)
├── pyproject.toml
└── tests/
```

**Dependencies**: FastMCP, Pydantic, Typer. No dependency on rockgarden at runtime.

## Usage

```bash
# Install
uv add rockgarden-mcp

# Serve (reads .rockgarden/content.json from project dir)
rockgarden-mcp serve
rockgarden-mcp serve /path/to/project

# Typical workflow
rockgarden build && rockgarden-mcp serve
```

Claude Desktop / claude_desktop_config.json:
```json
{
  "mcpServers": {
    "my-site": {
      "command": "rockgarden-mcp",
      "args": ["serve", "/path/to/site"]
    }
  }
}
```

## Changes to Rockgarden Core

1. **Always export content.json** during build (not just when hooks are configured)
2. **Add markdown content to export** — include `content` field (raw markdown body) in page entries
3. **Optional**: add `html` field for pre-rendered HTML

These are small, backward-compatible changes to `src/rockgarden/output/builder.py` and the content export function.

## Future Considerations (not for v1)

- File watching / auto-reload (`--watch` flag)
- Smarter search (TF-IDF or embedding-based)
- Resource templates for dynamic queries
- Auth/access control for multi-user scenarios

## Verification

1. Build a sample rockgarden site, confirm enriched content.json is exported
2. Run `rockgarden-mcp serve`, connect via MCP inspector
3. Test each auto-generated tool with zero config
4. Add a `rockgarden-mcp.toml`, verify customization works
5. Test with Claude Desktop as the MCP client
