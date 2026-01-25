# rockgarden

A static site generator for Obsidian vaults. Converts markdown files with Obsidian-specific syntax (wiki-links, embeds, callouts) into HTML sites.

## Installation

```bash
pip install rockgarden
```

Or with uv:

```bash
uv tool install rockgarden
```

## Quick Start

Initialize a new project:

```bash
rockgarden init
```

Build your site:

```bash
rockgarden build
```

Preview locally:

```bash
rockgarden serve
```

## Features

- Wiki-links (`[[page]]` and `[[page|display text]]`)
- Media embeds (images, audio, video, PDF)
- Clean URLs
- Auto-generated navigation
- Breadcrumbs

## Configuration

Configuration is stored in `rockgarden.toml`:

```toml
[site]
title = "My Site"
source = "content"
output = "_site"
clean_urls = true

[build]
ignore_patterns = [".obsidian", "Templates"]
```

## Requirements

Python 3.13+
