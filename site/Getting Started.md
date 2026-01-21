---
title: Getting Started
nav_order: 1
---

## Installation

Rockgarden requires Python 3.13+.

```bash
uv add rockgarden
```

Or with pip:

```bash
pip install rockgarden
```

## Building Your First Site

Point rockgarden at any Obsidian vault:

```bash
rockgarden build --source ./my-vault --output ./_site
```

The generated site will be in `_site/`.

## Configuration

Create a `rockgarden.toml` in your project root:

```toml
[site]
title = "My Site"
source = "."
output = "_site"

[build]
ignore_patterns = [".obsidian", "private", "templates"]
```

See [[Configuration]] for all options.
