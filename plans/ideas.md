# Ideas

Future ideas and research notes. Not currently planned.

## Pre-v1 Candidates

- **ASCII-only slugs** — strip Unicode/accents from URLs. Breaking change (URLs change), best done before v1 locks them. NFD normalization (no deps) handles European languages; `python-slugify` for full transliteration. See research notes below.
- **Configurable URL casing** — option to preserve original filename casing instead of slugifying

## Syntax & Content

- **Block references** (`[[page#^block]]`)
- **Inline fields** (`key:: value` — Dataview compatibility)
- **Inline tags** (`#tag`, `#parent/child`)
- **Configurable markdown preset** (commonmark, gfm-like, custom plugins)
- **Build-time mermaid rendering** — render mermaid diagrams to SVG at build time instead of client-side JS (via mermaid CLI `mmdc`)

## UI & Navigation

- **Hover previews** — popover preview of linked page on hover
- **Graph visualization** — interactive graph view of page links (see `features/graph-view.md`)
- **Reading time** — estimated reading time per page (word count / ~230 WPM)
- **Social links** — configurable list of social/external links with icons (e.g. GitHub, Mastodon, Bluesky) displayed in nav or footer

## Extensibility

- **Python plugins** — project-local behavioral extensions in `_plugins/<name>/`. See `features/plugins.md`.
- **Installable templates** — theme/plugin install from git URL or local directory via CLI
- **Theme/plugin dependency resolution** — themes/plugins declare dependencies, installer offers to also install them
- **Theme manifest collection defaults** — `theme.toml` declaring per-collection defaults
- **`rockgarden theme info` CLI command** — display theme options from `theme.toml` manifest

## Configuration

- **Configurable reserved directory names** — `_templates/`, `_themes/`, `_styles/`, `_scripts/` currently hardcoded
- **Tag URL prefix configurable** — `/tags/` is hardcoded; should be configurable

## Infrastructure

- **Unified logging/output** — currently a mix of `print()`, `typer.echo()`, and stderr. Introduce consistent logging with verbosity control.
- **Theme config update** — `set_theme_name_in_config` uses regex; swap for `tomlkit` for proper TOML writing
- **User asset subdirectory support** — `_styles/` and `_scripts/` only discover top-level files; support nested dirs
- **Extract icon handling** — move icon resolution into a standalone package
- **Merge `./site` and `./docs`** — consolidate demo site and docs site

---

## ASCII-only Slugs Research

**Problem**: Unicode in URLs causes encoding issues, server compatibility problems, and SEO challenges.

**Approaches**:

1. **Strip accents (NFD normalization)** — no dependencies, works for European languages. "Café" → "Cafe". Doesn't handle Cyrillic/CJK.
2. **python-slugify** — comprehensive transliteration including Cyrillic, Greek, CJK. Adds ~500KB dependency.

**Implementation location**: `src/rockgarden/urls.py` — `generate_slug()` function.

**Recommendation**: NFD strip approach (no deps) with optional python-slugify for advanced cases. Breaking change — URLs would change, but acceptable pre-v1.
