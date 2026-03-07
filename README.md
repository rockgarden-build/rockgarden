# rockgarden

A Python static site generator that works with Obsidian vaults and plain markdown folders out of the box. Point it at a directory of markdown files and get a navigable HTML site — no config required.

Rockgarden handles Obsidian-specific syntax (wiki-links, embeds, callouts) so you can publish your vault without changing how you write. For plain markdown, it just works.

## Philosophy

**Progressive customization.** Start with zero config and add complexity only when you need it:

- **Zero config** — Point at a folder, get a site
- **Convention** — Drop CSS in `_styles/`, templates in `_templates/`
- **Configuration** — Define collections, navigation, themes in `rockgarden.toml`
- **Full control** — Custom templates, build hooks, data pipelines

The goal is to scale from a personal wiki to a full-featured site without switching tools.

## Installation

```bash
pip install rockgarden
```

Or with uv:

```bash
uv tool install rockgarden
```

## Quick Start

```bash
rockgarden build     # build your site
rockgarden serve     # preview locally
```

A short alias is also available: `rgdn build`, `rgdn serve`.

## Features

**Obsidian support:**
- Wiki-links (`[[page]]`, `[[page|text]]`, `[[page#section]]`)
- Note transclusions (`![[note]]`)
- Media embeds (images, audio, video, PDF)
- Callouts (all Obsidian callout types)

**Navigation & discovery:**
- Auto-generated sidebar, breadcrumbs, folder index pages
- Per-page table of contents
- Backlinks
- Client-side full-text search
- Tag display and tag index pages (`/tags/<tag>/`)
- Sitemap generation
- Broken link detection with visual indication

**Customization:**
- Built-in theme with dark/light mode
- Template overrides via `_templates/`
- Layout system with named Jinja2 blocks
- Custom CSS (`_styles/`) and JS (`_scripts/`) auto-injected
- Theme export for full customization (`rockgarden theme export`)

**Collections:**
- Named content subsets scoped by directory
- Load data from YAML, JSON, and TOML files
- Pydantic model validation via `_models/`
- Per-collection templates, URL patterns, and page generation
- Collection entries available in all templates

**Build pipeline:**
- Build hooks (`pre_build`, `post_collect`, `post_build`)
- Content exported to `.rockgarden/content.json` for hook scripts
- Base path prefix for subdirectory deploys
- SEO meta tags from frontmatter (description, Open Graph)

**Other:**
- Clean URLs (`/page/` instead of `/page.html`)
- Accessibility (skip links, ARIA landmarks, focus styles)
- Zero lock-in — your content stays as plain markdown files

## CLI Commands

```bash
rockgarden build           # build your site
rockgarden serve           # local dev server
rockgarden init            # initialize a new project
rockgarden theme export    # export theme for customization
rockgarden icons update    # download Lucide icons for local override
```

## Configuration

Optional. Create `rockgarden.toml` to customize:

```toml
[site]
title = "My Site"
source = "content"
output = "_site"

[build]
ignore_patterns = [".obsidian", "Templates"]

[nav]
sort = "files-first"

[theme]
name = "default"

[[collections]]
name = "speakers"
source = "speakers"
template = "speaker.html"
url_pattern = "/speakers/{slug}/"

[hooks]
post_build = ["echo 'Build complete'"]
```

## Development

Requires [just](https://just.systems) and [uv](https://docs.astral.sh/uv/).

```bash
just install   # install dependencies
just test      # run tests
just check     # lint and format check
just format    # auto-fix lint and formatting
just ci        # lint + tests (run before submitting)
just build     # build the demo site
just serve     # serve output directory
just css       # compile Tailwind CSS
```

## Requirements

Python 3.13+

## Contributing

Contributions welcome — please open an issue before submitting PRs. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT. See [LICENSE](LICENSE).
