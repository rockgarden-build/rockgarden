---
tags: [markdown, reference]
---

# Markdown Syntax Support

Rockgarden supports the superset of CommonMark, GFM (GitHub Flavored Markdown), and Obsidian markdown. No configuration needed — all syntax is handled gracefully.

## CommonMark (Base Markdown)

| Feature           | Syntax                     | Status |
| ----------------- | -------------------------- | ------ |
| Headings          | `# H1` through `###### H6` | ✅     |
| Paragraphs        | Plain text                 | ✅     |
| Line breaks       | Two spaces or `\` at end   | ✅     |
| Emphasis          | `*italic*` or `_italic_`   | ✅     |
| Strong            | `**bold**` or `__bold__`   | ✅     |
| Blockquotes       | `> quote`                  | ✅     |
| Lists (ordered)   | `1. item`                  | ✅     |
| Lists (unordered) | `- item` or `* item`       | ✅     |
| Code (inline)     | `` `code` ``               | ✅     |
| Code blocks       | ` ``` ` or indented        | ✅     |
| Horizontal rule   | `---` or `***`             | ✅     |
| Links             | `[text](url)`              | ✅     |
| Images            | `![alt](url)`              | ✅     |
| Autolinks         | `<http://url>`             | ✅     |
| HTML              | Raw HTML passthrough       | ✅     |

## GFM (GitHub Flavored Markdown)

| Feature             | Syntax                  | Status | Notes              |
| ------------------- | ----------------------- | ------ | ------------------ |
| Tables              | `\| col \| col \|`      | ✅     | Via markdown-it-py |
| Strikethrough       | `~~text~~`              | ✅     | Via markdown-it-py |
| Task lists          | `- [ ]` and `- [x]`     | ❌     | Planned            |
| Autolinks           | Bare URLs               | ✅     | Via markdown-it-py |
| Syntax highlighting | ` ```python `           | ❌     | Planned            |
| Footnotes           | `[^1]` and `[^1]: text` | ❌     | Planned            |
| Alerts              | `> [!NOTE]`             | ✅     |                    |

## Obsidian Markdown

### Links & References

| Feature              | Syntax              | Status | Notes           |
| -------------------- | ------------------- | ------ | --------------- |
| Wiki-links           | `[[Page Name]]`     | ✅     |                 |
| Wiki-links (aliased) | `[[Page\|Display]]` | ✅     |                 |
| Headings links       | `[[Page#Heading]]`  | ⚠️     | Partial support |
| Block references     | `[[Page#^block]]`   | ❌     | Future          |

### Embeds

| Feature           | Syntax                     | Status | Notes      |
| ----------------- | -------------------------- | ------ | ---------- |
| Image embeds      | `![[image.png]]`           | ✅     |            |
| Image sizing      | `![[image.png\|200]]`      | ✅     |            |
| Image alt text    | `![[image.png\|alt text]]` | ✅     |            |
| Audio embeds      | `![[audio.mp3]]`           | ✅     |            |
| Video embeds      | `![[video.mp4]]`           | ✅     |            |
| PDF embeds        | `![[doc.pdf]]`             | ✅     |            |
| Note transclusion | `![[note]]`                | ✅     |            |

### Formatting

| Feature       | Syntax             | Status | Notes                     |
| ------------- | ------------------ | ------ | ------------------------- |
| Highlights    | `==text==`         | ❌     | Future                    |
| Comments      | `%% comment %%`    | ❌     | Should strip during build |
| HTML comments | `<!-- comment -->` | ✅     | Standard markdown         |

### Callouts

| Feature              | Syntax            | Status | Notes      |
| -------------------- | ----------------- | ------ | ---------- |
| Basic callouts       | `> [!note]`       | ✅     |            |
| Custom titles        | `> [!note] Title` | ✅     |            |
| Collapsible (open)   | `> [!note]+`      | ✅     |            |
| Collapsible (closed) | `> [!note]-`      | ✅     |            |

### Math

| Feature         | Syntax       | Status | Notes              |
| --------------- | ------------ | ------ | ------------------ |
| Inline math     | `$E = mc^2$` | ❌     | Future             |
| Block math      | `$$...$$`    | ❌     | Future             |
| GFM math blocks | ` ```math `  | ❌     | Planned            |

### Diagrams

| Feature | Syntax         | Status | Notes              |
| ------- | -------------- | ------ | ------------------ |
| Mermaid | ` ```mermaid ` | ❌     | Planned            |

### Tags

| Feature          | Syntax               | Status | Notes                |
| ---------------- | -------------------- | ------ | -------------------- |
| Inline tags      | `#tag`               | ❌     | Future (collections) |
| Nested tags      | `#parent/child`      | ❌     | Future (collections) |
| Frontmatter tags | `tags: [tag1, tag2]` | ✅     | Already parsed       |

### Metadata

| Feature          | Syntax        | Status | Notes                    |
| ---------------- | ------------- | ------ | ------------------------ |
| YAML frontmatter | `---` block   | ✅     | Fully parsed             |
| Inline fields    | `key:: value` | ❌     | Future (Dataview compat) |

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

- Inline math: `$...$` and block math `$$...$$`
- Highlights: `==text==`
- Comment stripping: `%% comment %%`
- Block references: `[[page#^block]]`
- Inline fields: `key:: value` (Dataview compatibility)
- Inline tags: `#tag`, `#parent/child`

### Not Planned

- Canvas files (`.canvas`): binary format, not markdown
- Dataview queries: requires runtime evaluation
- Plugin-specific syntax: too varied to support generically
