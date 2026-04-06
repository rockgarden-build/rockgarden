# Ideas

Future ideas and research notes. Not currently planned.

## Syntax & Content

- **Block references** (`[[page#^block]]`)
- **Inline fields** (`key:: value` — Dataview compatibility)

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

