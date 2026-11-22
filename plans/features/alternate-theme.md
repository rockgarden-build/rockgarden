# Alternate Bundled Theme

## Status: Planned (Phase 2, ships with the demo site)

A second bundled theme with a more modern style, as an alternative to the default docs/wiki look. The demo site showcases both.

Design to be brainstormed separately.

## Open Questions

- Visual direction and target use case (to be brainstormed)
- Selection mechanism: `theme.name` currently resolves only to `_themes/<name>/`; bundled themes need a name that doesn't collide with project themes
- Shared base: extend the default theme's templates and blocks, or a standalone template set
- CSS build: one Tailwind build covering both themes, or a separate compiled stylesheet per theme
- Which `[theme]` options marked "default theme only" the new theme supports
- Demo setup: one demo source built twice (one per theme), or separate demo sites
