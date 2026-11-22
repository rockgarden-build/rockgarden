# Block References

## Status: Planned (Phase 1)

Support Obsidian block references: `^block-id` markers on blocks, `[[page#^block-id]]` links, and `![[page#^block-id]]` embeds.

## Open Questions

- Which block types can carry an ID (paragraphs, list items, callouts, tables, headings)
- Rendered anchor format for the target block
- Behavior for broken block references (consistent with broken page links)
- Interaction with the existing transclusion and fragment-link handling
- Whether `^block-id` markers are stripped from rendered output
