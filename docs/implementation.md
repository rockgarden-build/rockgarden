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

## Phase 2: Content Models

### 2.1 Model Definition
Config file (`rockgarden.toml`) defining models:

```toml
[models.Character]
paths = ["/characters/"]
fields = ["name", "description"]

[models.NPC]
extends = "Character"
paths = ["/characters/npcs/"]
fields = ["location", "faction"]
```

### 2.2 Model Matching
- Files match models based on path
- A file can match multiple models (NPC is also Character)
- More specific paths take precedence for "primary" type
- API: `get_content_by_type("NPC")`, `content.types` returns all matching types

### 2.3 Model-Specific Templates
- Optional templates per model type
- Falls back to default content template

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
- [ ] Callout conversion
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
