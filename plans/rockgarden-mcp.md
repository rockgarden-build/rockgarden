# Rockgarden MCP — Approach

## Goal

Enable non-technical stakeholders (C-suite, VP, product) to explore and query internal documentation — product specs, engineering docs, component descriptions — via Claude. The primary interface is Claude.ai web, with Claude Desktop and Claude Code as secondary clients.

Content lives in Obsidian repos maintained by engineering/product teams. It is largely static, with requirements details refined or added weekly.

## Overview

Expose Rockgarden site content via MCP (Model Context Protocol). Two components:

1. **Content export** (rockgarden core) — post-build pass that extracts rendered content from HTML pages, converts to markdown, and writes per-page JSON files to `.rockgarden/content/`
2. **MCP server** (separate Python package) — Streamable HTTP server that reads exported content, serves it via MCP tools/resources, and provides search

The MCP server is deployed as a remote server and connected to Claude.ai as a custom integration. Users add it once via Claude's integrations UI (OAuth flow) and it's available in all their conversations — same experience as the Atlassian or Slack integrations. Users may optionally use Claude Projects for additional framing/instructions but don't need to.

## Design Principles

- **Single language.** Everything is Python. One ecosystem, one CI pipeline.
- **Rendered content is canonical.** Source formats vary (markdown, TOML, JSON, YAML) and templates may transform content. The rendered HTML — converted back to markdown — is the universal output the MCP server serves. Templates can be transformative (not just layout chrome), so the HTML round-trip is necessary.
- **Content export is a core feature, MCP server is separate.** The `_export/` output is useful to hooks and other tools, not just MCP. The MCP server is a separate package that consumes it. This also limits risk — the MCP server is experimental and may not survive, so it shouldn't bloat the core package.
- **Optional by default.** Content export is off unless enabled in config. MCP server is a separate install.

## Part 1: Content Export (Rockgarden Core Changes)

### Configuration

```toml
[export]
enabled = true          # enable content export (default: false)
output = "_export"      # export directory (default: adjacent to site output)
selector = "main"       # CSS selector for content extraction (default: "main")

[export.collections.api-docs]
selector = ".api-content"   # per-collection selector override
```

### Build Pipeline

Content export happens inline during the main build loop, not as a post-build pass. After each page's HTML is rendered via its template, the export step:

1. Extracts the content region from the rendered HTML via the configured CSS selector
2. Converts it back to markdown using `markdownify`
3. Writes a `.md` file with YAML frontmatter containing the page metadata

`content.json` (the metadata index) is also written to `_export/` when export is enabled, replacing the current `.rockgarden/content.json` location.

### Output Structure

```
_export/
├── content.json                    # Metadata index
├── pages/
│   └── engineering/
│       └── auth-migration.md       # Per-page content w/ YAML frontmatter
└── collections/
    └── api-docs/
        └── users.md                # Per-collection-entry content
```

### Per-Page File Format

```markdown
---
slug: engineering/auth-migration
title: Auth Migration Plan
url: /engineering/auth-migration/
tags:
  - auth
  - migration
modified: 2026-03-15T10:00:00
source_path: content/engineering/auth-migration.md
---

# Auth Migration Plan

We are migrating from...
```

Metadata is duplicated from `content.json` so each file is self-contained — the MCP server can answer a `get_page` request from a single file read + frontmatter parse.

### Implementation Changes

- `src/rockgarden/output/builder.py`: add inline export step to the page rendering loop; write `content.json` and per-page `.md` files to `_export/`
- New module for content extraction: parse HTML with beautifulsoup4, extract via selector, convert with markdownify
- New dependencies: `beautifulsoup4`, `markdownify`
- Config: new `ExportConfig` section
- Migrate existing `.rockgarden/content.json` usage (hooks env var) to point at `_export/content.json`
- Update gitignore warning to cover `_export/` instead of `.rockgarden/`

## Part 2: MCP Server (Separate Package — `rockgarden-mcp`)

### Architecture

Python MCP server using Streamable HTTP transport. Loads content at startup, builds search index in memory, serves MCP tools and resources over HTTP.

Deployable as a container (primary) or a direct process.

### Multi-Site Support

A single server instance can serve content from multiple rockgarden sites. Each site is a separate namespace with its own content directory.

```toml
# rockgarden-mcp.toml
[sites.engineering]
content_path = "/data/engineering/_export"

[sites.product]
content_path = "/data/product/_export"

[sites.roadmap]
content_path = "/data/roadmap/_export"
```

Tools and resources are scoped by site — e.g., `search(query, site="engineering")`, `get_page(slug, site="engineering")`.

### Authentication

OAuth 2.0 authorization flow backed by upstream OIDC providers (Entra ID, GitHub, etc.). Claude.ai's custom integration connector initiates a standard OAuth flow — users authenticate via their existing IdP, no manual token management required.

The server implements the OAuth server endpoints that Claude.ai expects and validates tokens against configured OIDC discovery endpoints.

```toml
[auth]
provider = "oidc"
issuer = "https://login.microsoftonline.com/{tenant}/v2.0"
audience = "rockgarden-mcp"
client_id = "..."
# or for GitHub:
# issuer = "https://github.com/login/oauth"
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

**Container (primary):** Dockerfile ships the server. CI builds a rockgarden site, copies `_export/` into the image (or mounts it as a volume), deploys.

**Direct process:** `rockgarden-mcp serve --config rockgarden-mcp.toml` for users who want to run it directly.

**Rebuild flow (v1):** CI builds site → pushes new container image → redeploy. No hot reload in v1.

### Client Setup

**Claude.ai web (primary):** Add as a custom integration via Settings → Integrations. Users authenticate once via OAuth and the integration is available in all conversations.

**Claude Desktop:** Add as a remote MCP server in settings:
```json
{
  "mcpServers": {
    "rockgarden": {
      "url": "https://mcp.internal.example.com"
    }
  }
}
```

**Claude Code:** Similar config via MCP settings.

## Open Questions

- **MCP SDK choice** — `mcp` SDK vs FastMCP. TBD based on evaluation.
- **Search engine** — Whoosh vs TF-IDF vs tantivy. Prototype and benchmark with realistic content sizes.
- **Content selector defaults** — Is `main` a good enough default, or should rockgarden's own templates mark the content region with a specific class?
- **llms-full.txt content source** — `llms-full.txt` (see `plans/llms-full-txt.md`) currently uses `page.html` (pre-template content HTML) for v1. When selector-based extraction lands here, revisit switching `llms-full.txt` to use extracted content instead, for consistency and to support transformative custom templates.
- **Multi-site resource URIs** — How should site namespacing work in MCP resource URIs? `page://engineering/auth-migration` vs `engineering://page/auth-migration`.
- **Claude.ai OAuth contract** — What exactly does Claude.ai expect from a custom integration's OAuth endpoints? Need to verify the required flow (authorization code grant, callback URLs, token format).

## Future Considerations

- Hot reload: watch for content changes, rebuild index without restart
- Embedding-based semantic search
- Prompt templates (e.g., `answer_from_docs(question)` that searches and synthesizes)
- Collection-aware tools with typed parameters from Pydantic schemas
- Custom tool definitions via config
- Edge deployment (Cloudflare Workers) if latency/scale demands it
- Per-site or per-collection access control

## Verification

1. Enable `export.enabled = true`, build a rockgarden site, confirm per-page `.md` files in `_export/`
2. Verify `content.json` is written to `_export/` with correct metadata
3. Verify content extraction handles different templates/selectors correctly
4. Start the MCP server, connect via MCP inspector
5. Test `search`, `get_page`, `list_pages`, `list_collections` across multiple sites
6. Test OAuth flow end-to-end with Entra ID and GitHub as upstream providers
7. Deploy as container, verify same behavior
8. Connect as custom integration in Claude.ai web, verify tools work in conversation
9. Test with Claude Desktop and Claude Code as secondary clients
