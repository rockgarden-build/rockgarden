# rockgarden

A Python static site generator that builds sites from Markdown content. Point it at a directory of Markdown files and get a navigable HTML site: no config required.

Rockgarden supports Obsidian vaults out of the box — wiki-links, embeds, and callouts all work without changing how you write.

## Philosophy

**Progressive customization.** Start with zero config and add complexity only when you need it:

- **Zero config**: Point at a folder, get a site
- **Convention**: Drop CSS in `_styles/`, templates in `_templates/`
- **Configuration**: Define collections, navigation, themes in `rockgarden.toml`
- **Full control**: Custom templates, build hooks, data pipelines

The goal is to scale from a personal wiki to a full-featured site without switching tools.

## Installation

With uv (recommended):

```bash
uv tool install rockgarden
```

Or with pip:

```bash
pip install rockgarden
```

## Quick Start

```bash
rockgarden build     # build your site
rockgarden serve     # preview locally
```

## Features

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

**Obsidian support:**

- Wiki-links (`[[page]]`, `[[page|text]]`, `[[page#section]]`)
- Note transclusions (`![[note]]`)
- Media embeds (images, audio, video, PDF)
- Callouts (all Obsidian callout types)

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

## Acknowledgements

Rockgarden was inspired by [Quartz](https://quartz.jzhao.xyz/), a static site generator for Obsidian vaults. Check it out as it might be more appropriate for your use case. When I found myself increasingly customizing my installation I decided to start building my own implementation, with the features I always wanted in a static site generator.

## Contributing

Contributions may be welcome if they fit the vision of this project. Please open an issue before submitting PRs. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Security

To report a vulnerability, please use [GitHub's private security reporting](https://github.com/rockgarden-build/rockgarden/security/advisories/new). See [SECURITY.md](SECURITY.md) for details.

## License

MIT. See [LICENSE](LICENSE).
