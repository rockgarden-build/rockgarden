---
tags: [guide]
---

# Getting Started

## Install

With uv (recommended):

```bash
uv tool install rockgarden
```

Or with pip:

```bash
pip install rockgarden
```

## Build a Site

Point rockgarden at any directory of markdown files:

```bash
rockgarden build
```

By default, rockgarden reads markdown from the current directory and writes HTML to `./_site/`. No configuration required: it handles Obsidian wiki-links, embeds, and callouts automatically.

Preview the result:

```bash
rockgarden serve
```

## Adding Configuration

Create `rockgarden.toml` to customize behavior:

```toml
[site]
title = "My Site"
source = "content"    # read from ./content/ instead of ./
output = "_site"      # write to ./_site/ instead of ./site/

[build]
ignore_patterns = [".obsidian", "Templates"]
```

See [[Configuration]] for all available options.

## Initialize a Project

To generate a starter `rockgarden.toml`:

```bash
rockgarden init
```

## Next Steps

- [[Customization]]: custom CSS, templates, themes, and more
- [[Configuration]]: full configuration reference
- [[Markdown Support]]: supported syntax reference
