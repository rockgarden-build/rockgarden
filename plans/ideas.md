# Ideas

Future ideas and research notes. Not currently planned.

## Syntax & Content

- **Inline math** (`$...$`) and block math (`$$...$$`)
- **Highlights** (`==text==`)
- **Comment stripping** (`%% comment %%`)
- **Block references** (`[[page#^block]]`)
- **Inline fields** (`key:: value` — Dataview compatibility)
- **Inline tags** (`#tag`, `#parent/child`)
- **Configurable markdown preset** (commonmark, gfm-like, custom plugins)

## Build & Performance

- **Incremental builds** — file-mtime dirty checking, partial rebuilds
- **Dev mode** — file watching with automatic partial rebuilds and local server with live reload
- **ASCII-only slugs** — strip Unicode/accents from URLs. NFD normalization (no deps) handles European languages; `python-slugify` for full transliteration. See research notes below.
- **Configurable URL casing** — option to preserve original filename casing instead of slugifying

## UI & Navigation

- **Hover previews** — popover preview of linked page on hover
- **Graph visualization** — interactive graph view of page links (see `features/graph-view.md`)
- **Reading time** — estimated reading time per page (word count / ~230 WPM)

## Extensibility

- **Python plugins** — project-local behavioral extensions in `_plugins/<name>/`. Can register build hooks, Jinja2 filters, markdown-it-py extensions, CLI subcommands.
- **Installable templates** — theme/plugin install from git URL or local directory via CLI
- **Theme/plugin dependency resolution** — themes/plugins declare dependencies, installer offers to also install them
- **Theme manifest collection defaults** — `theme.toml` declaring per-collection defaults (`template`, `url_pattern`, `model`) so sites only need to provide `source`
- **`rgdn theme info` CLI command** — display theme options from `theme.toml` manifest. Show name, description, and available config keys with types, defaults, and descriptions. For the active theme (or a named theme via `--name`). Builds on the existing `load_theme_manifest()` in `validation.py`. The manifest format should be extended to support `type`, `default`, and `description` fields on config entries. Validation should also use the manifest to type-check values (not just check for unknown/required keys).

## Configuration

- **Configurable reserved directory names** — `_templates/`, `_themes/`, `_styles/`, `_scripts/` currently hardcoded; make configurable
- **Tag URL prefix configurable** — `/tags/` is hardcoded; should be configurable to avoid conflicts with content pages
- **Convention directories configurable** — same as reserved directory names

## Infrastructure

- **Unified logging/output** — currently a mix of `print()`, `typer.echo()`, and stderr. Introduce consistent logging with verbosity control.
- **Theme config update** — `set_theme_name_in_config` uses regex; swap for `tomlkit` for proper TOML writing
- **User asset subdirectory support** — `_styles/` and `_scripts/` only discover top-level files; support nested dirs
- **Date field defaults research** — validate default frontmatter field names for dates against real-world Obsidian plugins and other SSGs
- **Extract icon handling** — move icon resolution into a standalone package
- **Merge `./site` and `./docs`** — consolidate demo site and docs site

---

## ASCII-only Slugs Research

**Problem**: Unicode in URLs causes encoding issues, server compatibility problems, and SEO challenges.

**Approaches**:

1. **Strip accents (NFD normalization)** — no dependencies, works for European languages. "Café" → "Cafe". Doesn't handle Cyrillic/CJK.
2. **python-slugify** — comprehensive transliteration including Cyrillic, Greek, CJK. Adds ~500KB dependency.

**Implementation location**: `src/rockgarden/urls.py` — `generate_slug()` function.

**Recommendation**: NFD strip approach (no deps) with optional python-slugify for advanced cases. Breaking change — URLs would change, but acceptable pre-1.0.
