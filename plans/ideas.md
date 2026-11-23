# Ideas

Future ideas and research notes. Post-1.0 unless moved into `roadmap.md`.

## Syntax & Content

- **Inline fields** (`key:: value` — Dataview compatibility)
- **Configurable markdown preset** (commonmark, gfm-like, custom plugins)
- **Build-time mermaid rendering** — render mermaid diagrams to SVG at build time instead of client-side JS (via mermaid CLI `mmdc`)

- **Audience profiles**: build one vault for different audiences (e.g. GM vs players, internal vs public). A build-time profile drops pages by frontmatter or folder, strips audience-restricted blocks inside pages, and renders links to dropped pages as broken without leaking titles. Needs design before roadmap: syntax for restricted blocks, how profiles are declared and selected, interaction with search index, nav, backlinks, and tags.

## UI & Navigation

- **Reading time** — estimated reading time per page (word count / ~230 WPM)

## Extensibility

- **Python plugins** — implementation. Design is in `roadmap.md` Phase 1; see `features/plugins.md`.
- **Installable templates** — theme/plugin install from git URL or local directory via CLI
- **Theme/plugin dependency resolution** — themes/plugins declare dependencies, installer offers to also install them
- **Theme manifest collection defaults** — `theme.toml` declaring per-collection defaults
- **`rockgarden theme info` CLI command** — display theme options from `theme.toml` manifest

## Infrastructure

- **Theme config update** — `set_theme_name_in_config` uses regex; swap for `tomlkit` for proper TOML writing
- **User asset subdirectory support** — `_styles/` and `_scripts/` only discover top-level files; support nested dirs
- **Extract icon handling** — move icon resolution into a standalone package

