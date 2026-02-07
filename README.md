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

Build your site:

```bash
rockgarden build
```

Preview locally:

```bash
rockgarden serve
```

## Features

- **Obsidian syntax** — Wiki-links (`[[page]]`, `[[page|text]]`), media embeds, callouts
- **Auto-generated navigation** — Sidebar, breadcrumbs, folder index pages
- **Themes** — Built-in theme with dark/light mode, or bring your own
- **Template overrides** — Override individual templates or swap in a full theme
- **Clean URLs** — `/getting-started/` instead of `/getting-started.html`
- **Zero lock-in** — Your content stays as plain markdown files

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
```

## Requirements

Python 3.13+
