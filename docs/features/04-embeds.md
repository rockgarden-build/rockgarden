# Feature 04: Embeds (Partial)

Support Obsidian embed syntax `![[filename]]` for images and (eventually) note transclusions.

## Status

- [x] Image embeds with alt text and sizing
- [ ] Audio embeds
- [ ] Note transclusions (`![[note.md]]`)

## Syntax Support

| Syntax | Result |
|--------|--------|
| `![[image.png]]` | Basic image embed |
| `![[image.png\|alt text]]` | Image with alt text |
| `![[image.png\|100]]` | Image with width |
| `![[image.png\|100x200]]` | Image with width and height |
| `![[folder/image.png]]` | Image with path |

## Implementation

1. Build media index of all non-markdown files in source
2. For each embed, resolve to actual file path
3. Replace with `<img>` tag including resolved path and dimensions
4. Copy referenced media files to output directory

## Key Files

- `assets.py` - `build_media_index()`, `create_media_resolver()`
- `obsidian/embeds.py` - `process_media_embeds()`, `parse_embed()`
- `output/builder.py` - Orchestrates embed processing and asset copying

## Future: Note Transclusions

`![[note.md]]` should inline the referenced note's content. Requires:
- Recursive content resolution
- Cycle detection
- Heading/block reference support (`![[note.md#heading]]`)
