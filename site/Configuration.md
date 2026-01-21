---
title: Configuration
nav_order: 2
---

Rockgarden is configured via `rockgarden.toml`.

## Site Options

```toml
[site]
title = "My Site"      # Site title (appears in page titles)
source = "."           # Source directory containing markdown
output = "_site"       # Output directory for generated HTML
```

## Build Options

```toml
[build]
ignore_patterns = [
    ".obsidian",       # Obsidian config folder
    "private",         # Private notes
    "templates",       # Template files
]
```

## Theme Options

```toml
[theme]
name = ""              # Theme name (empty = default)
```

## CLI Overrides

CLI flags override config file values:

```bash
rockgarden build --source ./vault --output ./dist
```

See [[Getting Started]] for basic usage.
