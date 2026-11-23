# Hover Previews

## Status: Planned (Phase 1)

Popover preview of a linked internal page when hovering a link, similar to Obsidian's page preview.

## Open Questions

- Content source: fetch the target page's HTML and extract the article, or generate a per-page preview payload at build time
- Preview scope: whole page, first N characters, or the linked heading/block section for fragment links
- Behavior on touch devices
- Whether previews apply to nav, backlinks, and search results or only in-content links
- Opt-out mechanism (config, per-page frontmatter)
