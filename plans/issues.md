# Known Issues

## Bugs

- **Macros not processed in transclusions**: `preprocess_macros` is applied to page content and folder indexes but not inside `_make_note_resolver`. Transcluded notes that use macros render macro calls as literal text. Fix by passing the macros dict into the resolver and applying preprocessing there.

## Tech Debt

- **Config namespacing**: As config options grow, consider better sections or namespacing in `rockgarden.toml`. Options like `show_build_info` and `show_build_commit` sit under `[build]` but could warrant their own section.
- **Replace ASCII diagrams with mermaid**: Once mermaid rendering is implemented, update the ASCII art diagrams in docs (e.g. Architecture.md build pipeline) to use mermaid.
