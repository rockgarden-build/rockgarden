# Demo Site

## Status: Planned

## Goal

Flesh out `site/` as a comprehensive feature showcase and deploy to Cloudflare Pages. Separate from the docs site.

## Pre-work

- Rename `site/` → `demo/`
- Update `rockgarden.toml` source path: `source = "./demo"`
- Update `.gitignore` if it references `site/`
- Update `justfile` references (e.g., `just build` recipe)
- Update `AGENTS.md` directory structure reference
- Update any other references to `site/` or `./site`

## Current State

`demo/` (currently `site/`) has basic pages: index, Getting Started, Configuration, Navigation, Future, plus `examples/markdown/` and `examples/obsidian/` with formatting, images, linking, and embeds. Missing most features added since initial creation.

## Content Plan

### Update existing pages

- `index.md` — update feature list (math, mermaid, inline tags, dev mode, etc.)
- `Getting Started.md` — update quick start (mention `rockgarden dev`)
- `Configuration.md` — new options (ascii_urls, stopwords, math_cdn/mermaid_cdn auto)
- `Future.md` — update or remove (most items done)
- `Navigation.md` — ensure nav ordering examples work

### New showcase pages

- `examples/markdown/math.md` — inline `$...$`, block `$$...$$`, fenced ` ```math `
- `examples/markdown/footnotes.md` — footnote syntax
- `examples/obsidian/callouts.md` — all callout types, collapsible variants
- `examples/obsidian/tags.md` — frontmatter tags, inline `#tags`, nested `#parent/child`
- `examples/obsidian/transclusions.md` — `![[note]]` embedding
- `examples/diagrams.md` — mermaid flowchart, sequence, class diagram
- `examples/icons.md` — inline Lucide icons
- `examples/highlights.md` — `==highlighted text==`

### Deployment

- `.github/workflows/demo.yml` (new) — mirrors `docs.yml`:
  - Triggers on push to main + PRs + workflow_dispatch
  - Builds `site/` → `_demo/`
  - Deploys to Cloudflare Pages as separate project (e.g., `rockgarden-demo`)
  - PR preview URL comments

## Verification

- `just build` — builds cleanly
- `just serve` — all pages render correctly
- All features visually confirmed: math, mermaid, callouts, tags, embeds, highlights, icons, syntax highlighting, search
