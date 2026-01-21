---
title: Configuration
nav_order: 2
---

Configuration is optional. Create `rockgarden.toml` in your project root to customize behavior.

## Site

```toml
[site]
title = "My Site"     # Page title suffix
source = "."          # Source directory
output = "_site"      # Output directory
```

## Build

```toml
[build]
ignore_patterns = [
    ".obsidian",      # Ignored by default
    "private",
    "templates",
    "Templates",
]
```

Ignored paths are completely excluded from the build.

## Navigation

```toml
[nav]
default_state = "collapsed"   # or "expanded"
sort = "files-first"          # "folders-first", "alphabetical"
hide = ["/drafts", "/private"]
labels = { "/api" = "API Reference" }
```

See [[Navigation]] for details.

## Theme

```toml
[theme]
name = ""             # Theme name (empty = default)
```

## Frontmatter

Page-level options in YAML frontmatter:

```yaml
---
title: Page Title     # Used in nav and <title>
nav_order: 1          # Pin position in nav (lower = first)
tags: [doc, guide]    # Shown in folder listings
auto_index: false     # For index.md: disable folder listing
---
```

The `auto_index` option only applies to `index.md` files. When `true` (default), the page shows both its content and an auto-generated listing of the folder's contents.

## CLI Overrides

CLI flags override config file values:

```bash
rockgarden build --source ./vault --output ./dist
rockgarden serve --port 3000
```
