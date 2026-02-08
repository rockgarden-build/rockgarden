# Feature 03: Wiki-Links ✅

Resolve Obsidian-style `[[wiki-links]]` to actual page URLs.

## Syntax Support

| Syntax | Result |
|--------|--------|
| `[[Page Name]]` | Link to page with text "Page Name" |
| `[[Page Name\|Display Text]]` | Link to page with custom display text |
| `[[folder/Page Name]]` | Link with explicit path |
| `[[Page Name#Section]]` | Link to page with section fragment |
| `[[image.png]]` | Link to media file (not embed) |

## Resolution Logic

1. Build index of all pages by filename and aliases (case-insensitive)
2. Build media index of all media files (images, audio, video, PDFs)
3. For each `[[link]]`, look up target in index:
   - If link contains `#`, split into page name and fragment, resolve page and append fragment
   - Try to resolve as a page first
   - If not a page, check if target is a media file and resolve to media path
4. Replace with HTML anchor: `<a href="/resolved/path/">Display Text</a>`
5. Unresolved links render as plain text with warning class

## Key Files

- `content/store.py` - `ContentStore` maintains `_by_name` index for lookups
- `obsidian/wikilinks.py` - `process_wikilinks()` regex replacement
- `output/builder.py` - Calls `process_wikilinks(content, store.resolve_link)`

## ContentStore API

```python
store.resolve_link("Page Name")          # Returns "/page-name/" or None
store.resolve_link("Page#Section")       # Returns "/page/#Section" or None
store.resolve_link("image.png")          # Returns "/attachments/image.png" or None
store.get_by_name("page name")           # Returns Page object or None
```

Resolution is case-insensitive and handles spaces/underscores interchangeably.

## Section Links

Section links use the `#` fragment syntax to link to a specific section within a page. The fragment is preserved in the output URL:

```markdown
[[Chamber of the Stone#Thalador]]
```

Becomes:

```html
<a href="/locations/chamber-of-the-stone/#Thalador">Chamber of the Stone > Thalador</a>
```

## Media File Links

Wiki-links to media files (without the `!` embed prefix) create hyperlinks to those files:

```markdown
[[CallaDain.png]]
```

Becomes:

```html
<a href="/attachments/CallaDain.png">CallaDain.png</a>
```

Supported media extensions: png, jpg, jpeg, gif, svg, webp, bmp, ico, mp3, wav, m4a, ogg, flac, mp4, webm, mov, mkv, pdf.

Note: To embed media inline, use the embed syntax `![[image.png]]` instead (see Feature 04: Embeds).
