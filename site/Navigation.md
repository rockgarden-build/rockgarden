---
title: Navigation
nav_order: 3
---

Rockgarden automatically generates navigation from your directory structure.

## Sidebar Nav

The sidebar displays a tree of all pages and folders. Folders are collapsible.

### Ordering

By default, files appear before folders, both sorted alphabetically.

**Pin specific items** with `nav_order` in frontmatter:

```yaml
---
title: Getting Started
nav_order: 1
---
```

Lower numbers appear first. Items without `nav_order` follow the default sort.

**Change default sort** in config:

```toml
[nav]
sort = "files-first"    # default
sort = "folders-first"
sort = "alphabetical"   # mixed files and folders
```

### Folder Labels

Folder display names resolve in order:

1. Config `labels` override
2. Folder's `index.md` frontmatter title
3. Folder name (titlecased)

```toml
[nav]
labels = { "/api" = "API Reference" }
```

### Hiding Paths

Hide paths from nav (pages still build and are linkable):

```toml
[nav]
hide = ["/drafts", "/internal/*"]
```

To exclude paths entirely, use `build.ignore_patterns` instead.

## Breadcrumbs

Each page shows a breadcrumb trail from root to current location.

## Folder Index Pages

Folders automatically get index pages listing their contents.

To add custom content above the listing, create `folder/index.md`:

```yaml
---
title: My Folder
---

Custom intro text here.
```

See [Examples](/examples/index.html) for a live example—it has custom content with the auto-generated listing below.

To disable the listing entirely and render as a normal page:

```yaml
---
title: My Folder
auto_index: false
---
```

This site's [homepage](/index.html) uses `auto_index: false`.
