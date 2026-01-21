---
title: Getting Started
nav_order: 1
---

## Installation

Requires Python 3.13+.

```bash
uv add rockgarden
```

Or with pip:

```bash
pip install rockgarden
```

## CLI Commands

### Build

Generate HTML from your markdown source:

```bash
rockgarden build --source ./my-vault --output ./_site
```

Short alias: `rgdn build`

### Serve

Preview the built site locally:

```bash
rockgarden serve --port 8000
```

## Supported Content

Rockgarden handles both Obsidian-style and plain markdown:

| Feature | Obsidian | Plain Markdown |
|---------|----------|----------------|
| Internal links | `[[Page Name]]` | `[text](page.md)` |
| Images | `![[image.png]]` | `![alt](image.png)` |
| Callouts | `> [!note]` | - |
| Tables | GFM | GFM |
| Task lists | `- [ ]` | `- [ ]` |

## Project Structure

Typical layout:

```
my-site/
├── rockgarden.toml    # Optional config
├── index.md           # Home page
├── page.md
└── folder/
    ├── index.md       # Folder landing page
    └── subpage.md
```

See [[Configuration]] for all options.
