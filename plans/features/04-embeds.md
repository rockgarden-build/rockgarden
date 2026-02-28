# Feature 04: Embeds

Support Obsidian embed syntax `![[filename]]` for media files and note transclusions.

## Status: Complete

- [x] Image embeds with alt text and sizing
- [x] Audio embeds (`mp3`, `wav`, `m4a`, `ogg`, `3gp`, `flac`)
- [x] Video embeds (`mp4`, `webm`, `ogv`, `mov`, `mkv`)
- [x] PDF embeds (via `<iframe>`)
- [x] Note transclusions (`![[note]]`, `![[note.md]]`)

## Syntax Support

| Syntax | Result |
|--------|--------|
| `![[image.png]]` | Basic image embed |
| `![[image.png\|alt text]]` | Image with alt text |
| `![[image.png\|100]]` | Image with width |
| `![[image.png\|100x200]]` | Image with width and height |
| `![[folder/image.png]]` | Image with path |
| `![[audio.mp3]]` | Audio player |
| `![[video.mp4]]` | Video player |
| `![[document.pdf]]` | PDF iframe |
| `![[Note Name]]` | Note transclusion (inline rendered content) |
| `![[Note Name#Heading]]` | Note transclusion (full note; heading ref ignored) |

## Implementation

### Media Embeds

1. Build media index of all non-markdown files in source
2. For each embed, resolve to actual file path
3. Replace with appropriate HTML element
4. Copy referenced media files to output directory

### Note Transclusions

1. After media embeds are processed, remaining `![[...]]` patterns are checked against the content store
2. If target resolves to a markdown note, render its content through the full pipeline
3. Replace with `<div class="transclusion">...</div>`
4. Cycle detection via visited set; cycles leave embed unchanged

## Key Files

- `assets.py` - `build_media_index()`, `create_media_resolver()`
- `obsidian/embeds.py` - `process_media_embeds()`, `parse_embed()`
- `obsidian/transclusions.py` - `process_note_transclusions()`
- `output/builder.py` - Orchestrates embed and transclusion processing

## Future

- Heading/block reference support (`![[note.md#heading]]` inlines only that section)
