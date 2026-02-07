# Implementation Plan

## Phase 1: Core SSG (Simple Case)

### 1.1 Project Setup
- Python package with uv
- CLI entry point
- Minimal config (source dir, output dir)

### 1.2 Content Ingestion
- Recursively read markdown files
- Parse YAML frontmatter (preserve all fields)
- Extract title from: frontmatter `title` → first H1 → filename
- Track file metadata (path, modified date, etc.)

### 1.3 Obsidian Compatibility
- **Wiki-links:** Convert `[[Page Name]]` and `[[Page Name|Display Text]]` to HTML links ✅
- **Image embeds:** Handle `![[image.png]]` with alt text and sizing ✅
- **Note transclusions:** Handle `![[note]]` embeds
- **Callouts:** Convert Obsidian callout syntax to styled HTML
- **Assets:** Copy images/files, update references ✅

### 1.4 Data Store & API
- In-memory store during build
- Simple API: `get_content(path)`, `list_content(dir)`, `get_backlinks(path)`, etc.
- All content is "Content" type by default

### 1.5 HTML Generation
- Jinja2 templates
- Default theme (can reference Quartz styling as inspiration)
- Core templates: page, index, folder listing

### 1.6 Navigation Features
- Directory-based explorer/sidebar
- Breadcrumbs
- Table of contents (per-page, from headings)
- Backlinks section

### 1.7 Search
- Build search index at build time (JSON)
- Client-side full-text search

## Phase 2: Collections

Supersedes the original "Content Models" design. See [Feature 14](features/14-collections.md) for full spec.

### 2.1 Collection-Aware Content Store
Extend `ContentStore` to be collection-aware. Without config, all content is in an implicit default collection (current behavior). Named collections carve out directory subsets — content claimed by a named collection is removed from the default.

### 2.2 Collections
Named subsets of content scoped by directory path. Config-driven, progressively configurable:

```toml
[[collections]]
name = "characters"
source = "characters"

[[collections]]
name = "pcs"
source = "characters/pcs"
model = "pc"
```

Collections can nest — content in `characters/pcs/` belongs to both `pcs` and `characters`.

At minimum a collection is just a namespace. Optionally add: model (schema), non-markdown formats, custom template, URL pattern, page generation controls, nav integration.

### 2.3 Models
Optional field schemas attached to collections:

```toml
[models.pc]
fields = ["name", "class", "level", "race"]
```

### 2.4 Non-Markdown Content
YAML/JSON/TOML files loaded when a collection config enables other formats. Page generation, URL patterns, and templates configurable per collection.

### 2.5 Build Hooks
See [Feature 15](features/15-build-hooks.md). Shell commands at `pre_build`, `post_collect`, `post_build` stages. Content exported to JSON at `.rockgarden/content.json` after collection for hook script access.

---

## Step-by-Step Checklist

### Step 1: Project Scaffold
- [x] Initialize uv project (`rockgarden`)
- [x] Set up package structure
- [x] CLI with `build` and `serve` commands
- [x] Config loading from `rockgarden.toml`

### Step 2: Content Reading
- [x] Markdown file discovery
- [x] Frontmatter parsing
- [x] Content store class

### Step 3: Obsidian Processing
- [x] Wiki-link parser/converter
- [x] Image embed handling (alt text, sizing)
- [ ] Note transclusion embeds
- [ ] **Callout conversion (NEXT STEP - see docs/features/05-callouts.md)**
- [x] Asset copying

### Step 4: HTML Output
- [x] Jinja2 environment setup
- [x] Base templates
- [x] Page rendering
- [x] Folder index generation

### Step 5: Navigation
- [x] Explorer data structure
- [x] Breadcrumb generation
- [ ] TOC extraction
- [ ] Backlink tracking

### Step 6: Search
- [ ] Build-time index generation
- [ ] Client-side search JS

---

## Verification

After each step, verify incrementally:

**Step 1:** `rockgarden --help` works, shows build/serve commands

**Step 2:** `rockgarden build` reads markdown files, prints discovered content

**Step 3:** Wiki-links in output HTML resolve to correct paths

**Step 4:** `rockgarden build` produces HTML files in output directory

**Step 5:** Generated pages include breadcrumbs, TOC, backlinks

**Step 6:** Search index JSON is generated, client search works

**End-to-end:** Run against D&D Obsidian vaults, compare to Quartz output
