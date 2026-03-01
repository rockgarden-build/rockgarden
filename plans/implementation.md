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
- [x] Section links (`[[Page#Section]]`)
- [x] Media file links (`[[image.png]]`)
- [x] Image embed handling (alt text, sizing)
- [ ] Note transclusion embeds
- [x] Callout conversion
- [x] Asset copying
- [x] Broken link handling (warnings + visual indication)

### Step 4: HTML Output
- [x] Jinja2 environment setup
- [x] Base templates
- [x] Page rendering
- [x] Folder index generation

### Step 5: Navigation
- [x] Explorer data structure
- [x] Breadcrumb generation
- [x] TOC extraction
- [x] Backlink tracking

### Step 6: Search
- [x] Build-time index generation
- [x] Client-side search UI
- [x] Search integration in template

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

---

## Current TODOs (Phase A - Zero-Config Release)

### Completed
- [x] **Callout Nested Content Bug**: Nested markdown inside callouts is now rendered
- [x] **Newline Handling**: Enable Obsidian-style single newline → `<br>` rendering

### Priority Order
- [x] **Table of Contents (Feature 13)**: Extract heading structure per-page
  - Parse rendered HTML to extract h2-h6 headings with IDs
  - Generate nested TOC structure
  - Add template support for TOC display

- [x] **Modified Date Display**: Show last-modified date on content pages
  - `Page.modified` populated from file mtime during loading
  - Displayed in `after_heading` template block

- [x] **Tag Display (N7)**: Show frontmatter tags on content pages
  - Tags rendered in `after_heading` block with `#` prefix normalized
  - Uses same badge styling as folder index tables

- [x] **Audio/Video Embeds (Feature 04)**: Extend media embed support
  - Audio, video, and PDF embeds implemented in `obsidian/embeds.py`

- [x] **Accessibility (Feature 18)**: Basic a11y improvements
  - Skip-to-content link, ARIA landmarks and labels
  - Focus-visible styles for keyboard navigation
  - Table scope attributes, search input label

- [x] **Template Decomposition (N9)**: Named Jinja2 blocks in `page.html` and `folder_index.html`
  - `before_heading`, `heading`, `after_heading`, `body`, `after_body` in main content area
  - `toc`, `backlinks` in right sidebar (`right_sidebar` parent block)
  - `after_heading` populated with modified date and tags by default

- [x] **Note Transclusions (Feature 04)**: Embed content from other notes via `![[note.md]]`
  - Cycle detection via visited set
  - Heading refs stripped for lookup (full note inlined); section-level extraction deferred

- [x] **Sitemap (Feature 13)**: XML sitemap generation (requires `site.base_url` config)

- [x] **Polish (Feature 13)**: Production readiness
  - [x] 404 page template (always generated; override via `_templates/404.html`)
  - [x] Build timing in CLI output (`Built N pages in X.Xs → /path`)
  - Detailed error validation and per-phase metrics deferred to future improvement

---

## Phase B: General SSG / PyOhio (0.9 Prerelease)

Work in batches, one feature per PR.

### Batch 1 — Independent Quick Wins

#### N8: Tag Index Pages ✅
- [x] Generate `/tags/<tag>/` listing pages for all unique tags
- [x] Link tag badges on pages to their index page
- [x] Generate tag index root page (`/tags/`) listing all tags

#### Feature 17: SEO & Meta Tags ✅
- [x] Add `description` and `og_image` to `SiteConfig`
- [x] Create `templates/components/meta.html` with conditional meta tag rendering
- [x] Include meta component in `base.html` `<head>`

### Batch 2 — Base Path Prefix

#### Feature 12: Base Path Prefix
- [ ] Confirm `base_url` handling in `SiteConfig` (already used for sitemap)
- [ ] Update URL generation helpers to include base path
- [ ] Update all templates to use `base_url` for asset and internal link references
- [ ] Update search index URL generation
- [ ] Verify wiki-link resolution is unaffected

### Batch 3 — Theming Foundation

#### Feature 10B: Layout System ✅
- [x] Refactor `base.html` to minimal HTML skeleton (head, body wrapper, script injection only)
- [x] Create `layouts/default.html` (extract current sidebar/drawer layout from `base.html`)
- [x] Add `resolve_layout()` to `render/engine.py`
- [x] Update `render_page()` to inject `layout_template` into render context
- [x] Update `page.html` and `folder_index.html` to `{% extends layout_template %}`
- [x] Add `theme.default_layout` config field

#### Feature 16: Static Assets (CSS & JS)
- [ ] Discover files in `_styles/` and `_scripts/` at build time
- [ ] Copy to `_site/styles/` and `_site/scripts/`
- [ ] Inject `<link>` and `<script>` tags in `base.html`

#### Feature 10C: Theme Export CLI
- [ ] Add `theme` command group to `cli.py`
- [ ] Implement `rockgarden theme export` — copies bundled theme to `_themes/default/`

### Batch 4 — Build Pipeline

#### Feature 15: Build Hooks
- [ ] Add `[hooks]` section to config (`pre_build`, `post_collect`, `post_build`)
- [ ] Export content store to `.rockgarden/content.json` after collection
- [ ] Execute hook shell commands at each stage with error handling

#### Feature 14: Collections
- [ ] Collection-aware `ContentStore` (`list_content("name")`, `get_content("name", slug=...)`)
- [ ] Config: `[[collections]]` with `name` and `source` fields
- [ ] Named collection carves its directory out of the default collection
- [ ] Nested collection support (content in `a/b/` belongs to both `b` and `a`)
- [ ] Optional model/schema (`[models.x]` with `fields`)
- [ ] Non-markdown format loading (YAML/JSON/TOML) when collection config enables it
- [ ] Custom template and URL pattern per collection
- [ ] Collection page generation controls (`pages = false`, `nav = true`)

### Anytime: N11 Config Validation

#### Feature N11: Config Validation
- [ ] New `validation.py` with `validate_config()` and `load_theme_manifest()`
- [ ] `rockgarden validate` CLI command (exits 1 on errors, 0 on warnings)
- [ ] Known-key validation derived from dataclass field names
- [ ] Theme manifest (`_themes/<name>/theme.toml`) loading and required-key check

### Future / Deferred

- [ ] **Graph View**: Interactive visualization of page connections — requirements TBD
- [ ] **Tag Index in Nav**: Defer to after N8 is done, decide based on usage
