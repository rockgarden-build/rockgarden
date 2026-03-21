# Rockgarden MCP — Approach

## Overview

Expose Rockgarden site content via MCP (Model Context Protocol). Two components:

1. **Content export** (rockgarden core) — post-build pass that extracts rendered content from HTML pages, converts to markdown, and writes per-page JSON files to `.rockgarden/content/`
2. **MCP server** (separate Python package) — Streamable HTTP server that reads exported content, serves it via MCP tools/resources, and provides search

## Design Principles

- **Single language.** Everything is Python. One ecosystem, one CI pipeline.
- **Rendered content is canonical.** Source formats vary (markdown, TOML, JSON, YAML) and templates may transform content. The rendered HTML — converted back to markdown — is the universal output the MCP server serves.
- **Content export is a core feature, MCP server is separate.** The `.rockgarden/content/` export is useful to hooks and other tools, not just MCP. The MCP server is a separate package that consumes it.
- **Optional by default.** Content export is off unless enabled in config. MCP server is a separate install.

## Part 1: Content Export (Rockgarden Core Changes)

### Configuration

```toml
[export]
content = true          # enable per-page content export (default: false)
selector = "main"       # CSS selector for content extraction (default: "main")

[export.collections.api-docs]
selector = ".api-content"   # per-collection selector override
```

### Build Pipeline

1. Build site as normal (all source formats → HTML via templates)
2. Always export `content.json` during build (remove hooks-only guard)
3. When `export.content = true`: post-build pass extracts content from rendered HTML
   - For each page: parse rendered HTML, extract content region via configured CSS selector, convert to markdown using `markdownify`
   - Write per-page JSON to `.rockgarden/content/`
4. Add `content_path` field to page entries in `content.json` pointing to the per-page file

### Output Structure

```
.rockgarden/
├── content.json                    # Metadata index (as today, plus content_path references)
└── content/
    ├── pages/
    │   └── {slug}.json             # Per-page content
    └── collections/
        └── {name}/
            └── {slug}.json         # Per-collection-entry content
```

### Per-Page JSON Format

```json
{
  "slug": "engineering/auth-migration",
  "title": "Auth Migration Plan",
  "url": "/engineering/auth-migration/",
  "tags": ["auth", "migration"],
  "frontmatter": {},
  "modified": "2026-03-15T10:00:00",
  "source_path": "content/engineering/auth-migration.md",
  "content": "# Auth Migration Plan\n\nWe are migrating from..."
}
```

Metadata is duplicated from `content.json` so each file is self-contained — the MCP server can answer a `get_page` request from a single file read.

### Implementation Changes

- `src/rockgarden/output/builder.py`: remove hooks-only guard on `content.json` export, add `content_path` to serialized entries
- New module for content extraction: parse HTML with beautifulsoup4, extract via selector, convert with markdownify
- Post-build step: iterate rendered pages, extract and write per-page JSON
- New dependencies: `beautifulsoup4`, `markdownify`
- Config additions in the export section

## Part 2: MCP Server (Separate Package — `rockgarden-mcp`)

### Architecture

Python MCP server using Streamable HTTP transport. Loads content at startup, builds search index in memory, serves MCP tools and resources over HTTP.

Deployable as a container (primary) or a direct process.

### Multi-Site Support

A single server instance can serve content from multiple rockgarden sites. Each site is a separate namespace with its own content directory.

```toml
# rockgarden-mcp.toml
[sites.engineering]
content_path = "/data/engineering/.rockgarden"

[sites.product]
content_path = "/data/product/.rockgarden"

[sites.roadmap]
content_path = "/data/roadmap/.rockgarden"
```

Tools and resources are scoped by site — e.g., `search(query, site="engineering")`, `get_page(slug, site="engineering")`.

### Authentication

OIDC-based auth via standard protocol, not provider-specific. Initial targets: GitHub and Entra ID. The server validates tokens against configured OIDC discovery endpoints.

```toml
[auth]
issuer = "https://login.microsoftonline.com/{tenant}/v2.0"
audience = "rockgarden-mcp"
# or for GitHub:
# issuer = "https://token.actions.githubusercontent.com"
```

### MCP Capabilities

**Tools:**
- `search(query, site?, collection?, tags?)` — keyword search across content
- `get_page(slug, site?)` — retrieve a page's content
- `list_pages(site?, tag?, collection?, limit?, offset?)` — list/filter pages
- `list_collections(site?)` — list collections with entry counts
- `get_site_structure(site?)` — site overview, nav tree

**Resources:**
- `page://{site}/{slug}` — page content
- `collection://{site}/{name}/{slug}` — collection entry

### Search

In-memory search index built at startup from the per-page content files. Options to evaluate:

- **Whoosh** — pure Python, good relevance ranking, battle-tested
- **Simple TF-IDF** — lightweight, no extra dependency, adequate for small-medium sites
- **tantivy-py** — Rust-backed, fast, but adds a native dependency

Decision deferred to implementation. Whoosh is the likely default for v1.

### Project Structure

```
rockgarden-mcp/
├── src/rockgarden_mcp/
│   ├── __init__.py
│   ├── cli.py              # CLI entry point
│   ├── server.py           # MCP server setup + Streamable HTTP
│   ├── auth.py             # OIDC token validation
│   ├── content.py          # Load and index content from .rockgarden/
│   ├── search.py           # Search engine
│   ├── tools.py            # MCP tool definitions
│   └── resources.py        # MCP resource definitions
├── pyproject.toml
├── Dockerfile
└── tests/
```

### Deployment

**Container (primary):** Dockerfile ships the server. CI builds a rockgarden site, copies `.rockgarden/` into the image (or mounts it as a volume), deploys.

**Direct process:** `rockgarden-mcp serve --config rockgarden-mcp.toml` for users who want to run it directly.

**Rebuild flow (v1):** CI builds site → pushes new container image → redeploy. No hot reload in v1.

### Client Setup

**Claude Desktop:**
```json
{
  "mcpServers": {
    "rockgarden": {
      "url": "https://mcp.internal.example.com",
      "headers": {
        "Authorization": "Bearer <token>"
      }
    }
  }
}
```

**Claude Code:** Similar config via MCP settings.

## Open Questions

- **MCP SDK choice** — `mcp` SDK vs FastMCP. TBD based on evaluation.
- **Search engine** — Whoosh vs TF-IDF vs tantivy. Prototype and benchmark with realistic content sizes.
- **Content selector defaults** — Is `main` a good enough default, or should rockgarden's own templates mark the content region with a specific class?
- **Multi-site resource URIs** — How should site namespacing work in MCP resource URIs? `page://engineering/auth-migration` vs `engineering://page/auth-migration`.
- **Token management for non-technical users** — How does the CEO get a token? OIDC browser flow, or a managed token provisioned by IT?

## Future Considerations

- Hot reload: watch for content changes, rebuild index without restart
- Embedding-based semantic search
- Prompt templates (e.g., `answer_from_docs(question)` that searches and synthesizes)
- Collection-aware tools with typed parameters from Pydantic schemas
- Custom tool definitions via config
- Edge deployment (Cloudflare Workers) if latency/scale demands it
- Per-site or per-collection access control

## Verification

1. Enable `export.content = true`, build a rockgarden site, confirm per-page JSON files in `.rockgarden/content/`
2. Verify `content.json` includes `content_path` references
3. Verify content extraction handles different templates/selectors correctly
4. Start the MCP server, connect via MCP inspector
5. Test `search`, `get_page`, `list_pages`, `list_collections` across multiple sites
6. Test OIDC auth flow with GitHub and Entra tokens
7. Deploy as container, verify same behavior
8. Test with Claude Desktop and Claude Code as MCP clients
