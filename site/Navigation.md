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

Folders without an `index.md` automatically get a generated index page listing their contents.

If you create `folder/index.md`, it renders as a normal page:

```yaml
---
title: My Folder
---

This is a custom landing page for the folder.
```

To show both your content and the folder listing, add `show_index: true`:

```yaml
---
title: My Folder
show_index: true
---

Custom intro text above the listing.
```

See [Examples](/examples/) for a live example with custom content.
