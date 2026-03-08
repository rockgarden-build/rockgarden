---
title: Rockgarden
---

A Python static site generator that builds sites from Markdown content, with Obsidian vault support out of the box.

## Philosophy

Rockgarden prioritizes simplicity and compatibility:

- **Zero config by default** - Point it at a folder of Markdown files and get a working site
- **Non-destructive** - Never modifies your source files
- **Markdown and Obsidian** - Standard Markdown and Obsidian syntax (wiki-links, embeds, callouts) both work out of the box
- **Minimal output** - Generates clean HTML without JavaScript dependencies

## Features

- Wiki-link resolution (`[[Page Name]]`)
- Image and file embeds (`![[image.png]]`)
- Callout/admonition blocks
- GitHub Flavored Markdown (GFM) tables, strikethrough, task lists
- Auto-generated navigation sidebar
- Breadcrumb trails
- Folder index pages
- Configurable nav ordering

## Quick Start

```bash
# Install
uv add rockgarden

# Build your site
rockgarden build --source ./my-vault --output ./_site

# Preview locally
rockgarden serve
```

## Documentation

- [[Getting Started]] - Installation and first build
- [[Configuration]] - All config options
- [[Navigation]] - Nav tree, breadcrumbs, ordering
- [[Future]] - Roadmap and ideas
