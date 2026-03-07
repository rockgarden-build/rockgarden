# Known Issues

- **Macros not processed in transclusions**: `preprocess_macros` is applied to page content and folder indexes but not inside `_make_note_resolver`. Transcluded notes that use macros render macro calls as literal text. Fix by passing the macros dict into the resolver and applying preprocessing there.
- **Heading link fragments not slugified**: `[[Page#My Heading]]` passes the fragment through as-is, but markdown-it-py generates anchors like `#my-heading`. The fragment should be slugified to match the rendered heading anchor. See `content/store.py` `resolve_link()`.
- **Footnotes not working**: `gfm-like` preset doesn't include footnotes and `mdit-py-plugins` is not installed. Renders as literal `[^1]` text. Need to add `mdit-py-plugins` dependency and enable the footnote plugin in `render/markdown.py`.
- **Task lists not working**: `gfm-like` preset doesn't render checkboxes. Shows `[ ]` and `[x]` as literal text. Need to enable the tasklists plugin via `mdit-py-plugins`.
- **Syntax highlighting not working**: Code fences get `class="language-python"` but no actual colorization. Need a client-side highlighter (highlight.js or Prism) or a build-time approach.
- **GFM math blocks not rendering**: ` ```math ` fences output `<code class="language-math">` but no math rendering occurs. Need KaTeX or MathJax client-side, or a build-time renderer.
- **Config namespacing**: As config options grow, consider better sections or namespacing in `rockgarden.toml`. Options like `show_build_info` and `show_build_commit` sit under `[build]` but could warrant their own section.
- **Replace ASCII diagrams with mermaid**: Once mermaid rendering is implemented, update the ASCII art diagrams in docs (e.g. Architecture.md build pipeline) to use mermaid.
- **Dev server doesn't support custom 404 page**: The `serve` command uses Python's built-in HTTP server, which returns a generic 404 response. It should serve the site's custom `404.html` if present.
