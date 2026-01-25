# Feature 03: Wiki-Links ✅

Resolve Obsidian-style `[[wiki-links]]` to actual page URLs.

## Syntax Support

| Syntax | Result |
|--------|--------|
| `[[Page Name]]` | Link to page with text "Page Name" |
| `[[Page Name\|Display Text]]` | Link to page with custom display text |
| `[[folder/Page Name]]` | Link with explicit path |

## Resolution Logic

1. Build index of all pages by filename and aliases (case-insensitive)
2. For each `[[link]]`, look up target in index
3. Replace with HTML anchor: `<a href="/resolved/path/">Display Text</a>`
4. Unresolved links render as plain text with warning class

## Key Files

- `content/store.py` - `ContentStore` maintains `_by_name` index for lookups
- `obsidian/wikilinks.py` - `process_wikilinks()` regex replacement
- `output/builder.py` - Calls `process_wikilinks(content, store.resolve_link)`

## ContentStore API

```python
store.resolve_link("Page Name")  # Returns "/page-name/" or None
store.get_by_name("page name")   # Returns Page object or None
```

Resolution is case-insensitive and handles spaces/underscores interchangeably.
