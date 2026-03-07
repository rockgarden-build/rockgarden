# Implementation Plan

## Phase A: Zero-Config Release ✅

Core SSG with Obsidian compatibility. All items complete.

### Core Pipeline
- [x] Project scaffold (uv, CLI, config loading)
- [x] Markdown file discovery and frontmatter parsing
- [x] Content store (in-memory, `get_content()`, `list_content()`, `get_backlinks()`)
- [x] Jinja2 templates, page rendering, folder index generation

### Obsidian Processing
- [x] Wiki-links (`[[Page]]`, `[[Page|Text]]`, `[[Page#Section]]`)
- [x] Image embeds with alt text and sizing
- [x] Note transclusions (`![[note]]`) with cycle detection
- [x] Callouts (all types, nested content)
- [x] Asset copying and reference updating
- [x] Broken link handling (warnings + visual indication)

### Navigation & Discovery
- [x] Sidebar explorer, breadcrumbs
- [x] Table of contents (h2-h6, nested)
- [x] Backlinks
- [x] Search (build-time index + client-side UI)

### Polish
- [x] Newline handling (single newline → `<br>`)
- [x] Modified date display
- [x] Tag display on pages
- [x] Audio/video/PDF embeds
- [x] Accessibility (skip link, ARIA, focus styles)
- [x] Template decomposition (named blocks for customization)
- [x] Sitemap generation
- [x] 404 page
- [x] Build timing in CLI output

---

## Phase B: General SSG / PyOhio ✅

One feature per PR. All items complete.

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

#### Feature 12: Base Path Prefix ✅
- [x] Confirm `base_url` handling in `SiteConfig` (already used for sitemap)
- [x] Update URL generation helpers to include base path
- [x] Update all templates to use `base_url` for asset and internal link references
- [x] Update search index URL generation
- [x] Verify wiki-link resolution is unaffected

### Batch 3 — Theming Foundation

#### Feature 10B: Layout System ✅
- [x] Refactor `base.html` to minimal HTML skeleton (head, body wrapper, script injection only)
- [x] Create `layouts/default.html` (extract current sidebar/drawer layout from `base.html`)
- [x] Add `resolve_layout()` to `render/engine.py`
- [x] Update `render_page()` to inject `layout_template` into render context
- [x] Update `page.html` and `folder_index.html` to `{% extends layout_template %}`
- [x] Add `theme.default_layout` config field

#### Feature 16: Static Assets (CSS & JS) ✅
- [x] Discover files in `_styles/` and `_scripts/` at build time
- [x] Copy to `_site/styles/` and `_site/scripts/`
- [x] Inject `<link>` and `<script>` tags in `base.html` / `layouts/default.html`

#### Feature 10C: Theme Export CLI ✅
- [x] Add `theme` command group to `cli.py`
- [x] Implement `rockgarden theme export` — copies bundled theme to `_themes/default/`

### Batch 4 — Build Pipeline

#### Feature 15: Build Hooks ✅
- [x] Add `[hooks]` section to config (`pre_build`, `post_collect`, `post_build`)
- [x] Export content store to `.rockgarden/content.json` after collection
- [x] Execute hook shell commands at each stage with error handling

#### Feature 14: Collections ✅

##### 14A: Markdown Collections + Template Context
- [x] `content/collection.py` with `Collection` dataclass and `partition_collections()`
- [x] Collection-aware `ContentStore` (`get_collection()`, `list_collection()`)
- [x] `collections.<name>` available as Jinja2 template global
- [x] Nested collection support (content in `a/b/` belongs to both `b` and `a`)
- [x] JSON export updated to structured `{pages, collections}` format

##### 14B: Non-Markdown Format Loading
- [x] `content/format_loader.py` — load YAML, JSON, TOML data files
- [x] Slug from filename stem or explicit `slug` field
- [x] Builder loads data files per collection and appends to entries
- [x] `pyyaml` added as direct dependency

##### 14C: Content Models
- [x] `content/models_loader.py` — `resolve_model()` and `validate_entry()`
- [x] Model cascade: `_models/<name>.py` → `_themes/<theme>/_models/<name>.py`
- [x] Pydantic validation with coercion and defaults merged back
- [x] Builder validates entries for collections with `model` config

##### 14D: Collection Page Generation + Nav Integration
- [x] `generate_collection_url()` — `{field}` placeholder substitution
- [x] `build_collection_pages()` — generates HTML for collections with `pages=true` + `template` + `url_pattern`
- [x] Main render loop skips pages in collections with custom templates or `pages=false`
- [x] Nav integration: `nav=true` collections add folder nodes to nav tree
- [x] Collection pages included in search index

### Anytime: N11 Config Validation

#### Feature N11: Config Validation ✅
- [x] New `validation.py` with `validate_config()` and `load_theme_manifest()`
- [x] `rockgarden validate` CLI command (exits 1 on errors, 0 on warnings)
- [x] Known-key validation derived from Pydantic model fields
- [x] Theme manifest (`_themes/<name>/theme.toml`) loading and required-key check

---

## Phase C: Enhanced Features

- [x] **Feature 09: Macros** — User-defined Jinja2 macros
- [x] **Feature 11: Atom Feed** — Atom feed generation

## Future / Deferred

- [ ] **Graph View**: Interactive visualization of page connections — requirements TBD
- [ ] **Tag Index in Nav**: Decide based on usage
