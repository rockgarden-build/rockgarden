# Known Issues

## Doc tasks

- **Replace ASCII diagrams with mermaid**: Now that mermaid rendering is implemented, update the ASCII art diagrams in docs (e.g. Architecture.md build pipeline) to use mermaid.

## Config / UX

- **Search stopword list needs research and configurability**: The client-side JS search library's default stopword list is long and may filter out actual content. Needs: (1) research a better default list, (2) make the list configurable via `rockgarden.toml`, (3) pass the configured list to the JS search library initialization.

## Performance

- **CDN scripts load on every page regardless of usage**: KaTeX and Mermaid CDN scripts load on all pages even when no math or diagrams are present. Could detect usage at build time and set per-page flags to conditionally include them.

## Feature gaps

- **Add brand icon library support**: Lucide intentionally excludes brand/logo icons. Need a second icon library for social/brand icons. The resolver's `LIBRARY_ALIASES` and multi-library dispatch are already wired up — implementation is mostly adding a new loader. Candidates: Simple Icons, Font Awesome, Iconify.

## Content

- **Flesh out example site and publish as demo**: The existing small example site isn't built or published anywhere. Expand it to cover most features and publish as a standalone demo site.
