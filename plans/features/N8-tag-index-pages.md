# Feature N8: Tag Index Pages

Generate `/tags/<tag>/` listing pages for all unique tags found in content.

## Status: Complete ✅

## Goal

Every unique tag across all content gets a dedicated listing page. Tag badges on content pages link to their index. A root `/tags/` page lists all tags.

## Prerequisite

Tag display (N7) is complete — tags are normalized (leading `#` stripped, lowercased) and rendered on pages.

## Output

```
_site/
  tags/
    index.html          ← all tags, each linking to its listing
    python/
      index.html        ← all pages tagged "python"
    obsidian/
      index.html        ← all pages tagged "obsidian"
```

## Tag Normalization

Use the same normalization as N7: strip leading `#`, lowercase. Tags `Python`, `#python`, and `python` all map to the slug `python`.

## Template

`templates/tag_index.html` — listing page for a single tag. Shows tag name and a list of content pages (title + path).

`templates/tags_root.html` — root `/tags/` page listing all tags with page counts.

Both extend the active layout.

## Tag Badge Links

Update the tag badge rendering in `after_heading` to link each badge to `/tags/<slug>/`.

## Config

No required config. Optional:
```toml
[theme]
tag_index = true   # default: true — set false to disable tag pages entirely
```

## Implementation Plan

### 1. Tag Collection

After content is loaded, collect all tags across all pages:

```python
def collect_tags(store: ContentStore) -> dict[str, list[Page]]:
    """Return mapping of normalized tag slug → list of pages."""
```

### 2. Tag Page Generation

In `output/builder.py`, after rendering content pages:

```python
for tag_slug, pages in tags.items():
    render_tag_page(tag_slug, pages, output_dir)
render_tags_root(tags, output_dir)
```

### 3. Templates

- `templates/tag_index.html` — single tag listing
- `templates/tags_root.html` — all tags overview

### 4. Link Tag Badges

Update the `after_heading` block (or wherever tags are rendered) so each badge links to `/tags/<slug>/`.

## Key Files to Create/Modify

- `output/builder.py` — tag collection + page generation
- `templates/tag_index.html` — new
- `templates/tags_root.html` — new
- `templates/components/tags.html` (or wherever tag badges render) — add links

## Verification

- Build a vault with multiple tags → `/tags/` and `/tags/<tag>/` pages generated
- Tag badges on content pages link to the correct index
- Unnormalized tags (`#Python`, `Python`) all resolve to the same `/tags/python/` page
- Tag with no pages is not generated
