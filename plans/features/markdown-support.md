# Markdown Support Gaps

Unimplemented features documented in `docs/Markdown Support.md`. Grouped by effort and dependency.

## Needs `mdit-py-plugins` dependency

These require adding `mdit-py-plugins` and enabling plugins in `render/markdown.py`.

- **Footnotes** (`[^1]` / `[^1]: text`) — documented as Planned. Plugin: `footnote`.
- **Task lists** (`- [ ]` / `- [x]`) — documented as ✅ but not actually rendering. The `gfm-like` preset comments claim support but checkboxes render as literal text. Plugin: `tasklists`.

## Needs client-side JS library

- **Syntax highlighting** (` ```python `) — code fences output `class="language-*"` but no colorization. Options: highlight.js (simpler, auto-detection) or Prism (lighter, explicit). Could also do build-time with Pygments.
- **Mermaid diagrams** (` ```mermaid `) — render fenced mermaid blocks as diagrams. See `plans/features/mermaid.md` for full spec.
- **Math rendering** — inline `$...$`, block `$$...$$`, and GFM ` ```math ` fences. Needs KaTeX (lighter, faster) or MathJax (broader LaTeX support) client-side, or a build-time renderer.

## Needs preprocessing (Python)

These need processing in `render/preprocessors.py` or similar, before markdown-it-py parsing.

- **Highlights** (`==text==`) — wrap in `<mark>` tags. Straightforward regex replacement (with code block protection).
- **Comment stripping** (`%% comment %%`) — strip Obsidian comments during build. Regex replacement.
- **Inline tags** (`#tag`, `#parent/child`) — parse inline tags from content body, add to page metadata. Intersects with collections design.
- **Inline fields** (`key:: value`) — Dataview-style metadata. Parse and expose in page data.
- **Block references** (`[[Page#^block]]`) — requires block-level ID assignment and cross-page reference resolution. Most complex item here.