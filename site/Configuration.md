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
clean_urls = true     # Use /path/ instead of /path.html (default: true)
```

### Clean URLs

When `clean_urls = true` (the default):
- Pages output to directories: `about.md` → `about/index.html`
- URLs use trailing slashes: `/about/`
- Links in content transform: `[text](page.md)` → `[text](page/)`

When `clean_urls = false`:
- Pages output as files: `about.md` → `about.html`
- URLs use `.html` extension: `/about.html`
- Links in content transform: `[text](page.md)` → `[text](page.html)`

Index pages (`index.md`) always output as `index.html` in their folder.

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
slug: custom-slug     # Override generated URL slug
nav_order: 1          # Pin position in nav (lower = first)
tags: [doc, guide]    # Shown in folder listings
show_index: true      # For index.md: add folder listing
---
```

### Folder Index Pages

The `show_index` option controls how `index.md` files are rendered:

| Scenario | Result |
|----------|--------|
| No `index.md` in folder | Auto-generated folder listing |
| `index.md` exists (default) | Renders as normal page |
| `index.md` with `show_index: true` | Page content + folder listing |

This lets you write custom landing pages for folders while still optionally including the file listing.

## URL Slugs

Rockgarden generates URL-safe slugs from filenames:

| Filename | Generated Slug |
|----------|----------------|
| `Getting Started.md` | `getting-started` |
| `NPCs/Olvir the Wise.md` | `npcs/olvir-the-wise` |
| `my_page.md` | `my-page` |

Slug rules:
- Lowercase the entire path
- Replace spaces and underscores with dashes
- Preserve directory structure

Override the generated slug with frontmatter:

```yaml
---
title: Getting Started
slug: quickstart
---
```

This produces `/quickstart/` instead of `/getting-started/`.

## CLI Overrides

CLI flags override config file values:

```bash
rockgarden build --source ./vault --output ./dist
rockgarden serve --port 3000
```
