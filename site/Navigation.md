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
2. `label` field in the folder's `_folder.md`
3. Folder's `index.md` / folder-note title
4. Folder name (titlecased)

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

If you create `folder/index.md`, it renders as a normal page at `/folder/`:

```yaml
---
title: My Folder
---

This is a custom landing page for the folder.
```

Obsidian's folder-note convention also works: a file matching the folder name (`folder/folder.md`) renders at the same URL (`/folder/`). Both forms are equivalent.

### Folder Metadata (`_folder.md`)

Per-folder options live in an optional `_folder.md` file inside the folder. The file is frontmatter-only — any body is ignored — and is never published as a page.

```yaml
---
nav_order: 2
label: "My Folder"
sort: alphabetical
sort_reverse: false
---
```

Supported fields:

- `nav_order` — pin the folder's position in its parent nav
- `label` — override the folder's display label
- `sort` / `sort_reverse` — child sort strategy (per-folder override of config)
- `unlisted` — hide the folder (and all its descendants) from nav
- `show_index` — render the auto-generated listing at `/folder/` instead of the `index.md` page (if both exist, the `index.md` body appears as prose above the listing)

### Unlisted Behavior

`unlisted: true` on a regular page hides it from nav and folder listings (URL still works).

`unlisted: true` on an `index.md` or folder-note: the page still renders at `/folder/`, but no nav entry links to it. The folder itself remains in nav with its children. Use this for section overview pages that you want reachable via direct URL but not linked from the menu.

To hide an entire folder, set `unlisted: true` in the folder's `_folder.md`.

See [Examples](/examples/) for a live example with custom content.
