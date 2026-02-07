# Markdown Syntax Support

Rockgarden supports the superset of CommonMark, GFM (GitHub Flavored Markdown), and Obsidian markdown. No configuration needed — all syntax is handled gracefully.

## CommonMark (Base Markdown)

| Feature | Syntax | Status |
|---------|--------|--------|
| Headings | `# H1` through `###### H6` | ✅ |
| Paragraphs | Plain text | ✅ |
| Line breaks | Two spaces or `\` at end | ✅ |
| Emphasis | `*italic*` or `_italic_` | ✅ |
| Strong | `**bold**` or `__bold__` | ✅ |
| Blockquotes | `> quote` | ✅ |
| Lists (ordered) | `1. item` | ✅ |
| Lists (unordered) | `- item` or `* item` | ✅ |
| Code (inline) | `` `code` `` | ✅ |
| Code blocks | ` ``` ` or indented | ✅ |
| Horizontal rule | `---` or `***` | ✅ |
| Links | `[text](url)` | ✅ |
| Images | `![alt](url)` | ✅ |
| Autolinks | `<http://url>` | ✅ |
| HTML | Raw HTML passthrough | ✅ |

## GFM (GitHub Flavored Markdown)

| Feature | Syntax | Status | Notes |
|---------|--------|--------|-------|
| Tables | `\| col \| col \|` | ✅ | Via markdown-it-py |
| Strikethrough | `~~text~~` | ✅ | Via markdown-it-py |
| Task lists | `- [ ]` and `- [x]` | ✅ | Via markdown-it-py |
| Autolinks | Bare URLs | ✅ | Via markdown-it-py |
| Syntax highlighting | ` ```python ` | ✅ | Via markdown-it-py |
| Footnotes | `[^1]` and `[^1]: text` | ✅ | Via markdown-it-py |
| Alerts | `> [!NOTE]` | Ready | Feature 05 |

## Obsidian Markdown

### Links & References

| Feature | Syntax | Status | Notes |
|---------|--------|--------|-------|
| Wiki-links | `[[Page Name]]` | ✅ | Feature 03 |
| Wiki-links (aliased) | `[[Page\|Display]]` | ✅ | Feature 03 |
| Headings links | `[[Page#Heading]]` | ⚠️ | Partial support |
| Block references | `[[Page#^block]]` | ❌ | Future |

### Embeds

| Feature | Syntax | Status | Notes |
|---------|--------|--------|-------|
| Image embeds | `![[image.png]]` | ✅ | Feature 04 |
| Image sizing | `![[image.png\|200]]` | ✅ | Feature 04 |
| Image alt text | `![[image.png\|alt text]]` | ✅ | Feature 04 |
| Audio embeds | `![[audio.mp3]]` | ✅ | Feature 04 |
| Video embeds | `![[video.mp4]]` | ✅ | Feature 04 |
| PDF embeds | `![[doc.pdf]]` | ✅ | Feature 04 |
| Note transclusion | `![[note]]` | ❌ | Planned |

### Formatting

| Feature | Syntax | Status | Notes |
|---------|--------|--------|-------|
| Highlights | `==text==` | ❌ | Future |
| Comments | `%% comment %%` | ❌ | Should strip during build |
| HTML comments | `<!-- comment -->` | ✅ | Standard markdown |

### Callouts

| Feature | Syntax | Status | Notes |
|---------|--------|--------|-------|
| Basic callouts | `> [!note]` | Ready | Feature 05 |
| Custom titles | `> [!note] Title` | Ready | Feature 05 |
| Collapsible (open) | `> [!note]+` | Ready | Feature 05 |
| Collapsible (closed) | `> [!note]-` | Ready | Feature 05 |

### Math

| Feature | Syntax | Status | Notes |
|---------|--------|--------|-------|
| Inline math | `$E = mc^2$` | ❌ | Future |
| Block math | `$$...$$` | ❌ | Future |
| GFM math blocks | ` ```math ` | ✅ | Via markdown-it-py |

### Diagrams

| Feature | Syntax | Status | Notes |
|---------|--------|--------|-------|
| Mermaid | ` ```mermaid ` | ✅ | Via markdown-it-py |

### Tags

| Feature | Syntax | Status | Notes |
|---------|--------|--------|-------|
| Inline tags | `#tag` | ❌ | Future (collections) |
| Nested tags | `#parent/child` | ❌ | Future (collections) |
| Frontmatter tags | `tags: [tag1, tag2]` | ✅ | Already parsed |

### Metadata

| Feature | Syntax | Status | Notes |
|---------|--------|--------|-------|
| YAML frontmatter | `---` block | ✅ | Fully parsed |
| Inline fields | `key:: value` | ❌ | Future (Dataview compat) |

## Syntax Priority

When features overlap (rare), rockgarden handles them in this order:

1. **Obsidian-specific syntax** is preprocessed first (wiki-links, embeds, callouts, comments)
2. **GFM/CommonMark** is parsed by markdown-it-py
3. **HTML passthrough** for anything not matched

This ensures:
- Code blocks protect their contents from all processing
- Obsidian syntax works even if it conflicts with markdown edge cases
- Standard markdown always works

## Future Syntax Additions

Planned for future phases:

### Phase A (Zero-Config Release)
- ❌ Note transclusion: `![[note]]`

### Phase B (General SSG)
- None markdown-specific

### Phase C (Enhanced Features)
- ❌ Inline math: `$...$` and block math `$$...$$`
- ❌ Highlights: `==text==`
- ❌ Comment stripping: `%% comment %%`
- ❌ Block references: `[[page#^block]]`
- ❌ Inline fields: `key:: value` (Dataview compatibility)

### Not Planned
- Canvas files (`.canvas`) — binary format, not markdown
- Dataview queries — requires runtime evaluation
- Plugin-specific syntax — too varied to support generically

## Testing Strategy

Each syntax feature should have test coverage for:
1. Basic usage (happy path)
2. Edge cases (nested, escaped, empty)
3. Inside code blocks (should NOT process)
4. Mixed with other syntax
5. Invalid syntax (graceful degradation)

See individual feature docs in `docs/features/` for detailed specs.
