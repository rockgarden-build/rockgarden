# Plugins

## Status: Design before 1.0, implement after

## Concept

Project-local behavioral extensions in `_plugins/<name>/`. No global install, no marketplace.

A plugin can register:
- Build hooks
- Jinja2 template filters
- markdown-it-py extensions
- CLI subcommands

Plugins handle functionality that's too opinionated for the core (e.g., OG image generation where different users want different tools and layouts).

## Design Notes

- Themes and plugins are separate concepts in separate directories. A theme handles presentation; a plugin handles behavior.
- A theme can declare plugin dependencies (e.g., a theme that relies on an image optimization plugin).
- Plugins can provide their own templates (added to the template resolution chain).
- Hooks are a primitive: usable standalone via config, or provided by plugins.
- Installation by convention (copy/clone into project) or via CLI from a git URL or local directory.

## Fit-Test Use Cases

Scenarios for checking the design's extension points.

### A tool's own file format rendered as pages

Hypothetical: a plugin for something like [Atlas VTT](https://github.com/atlas-vtt/atlas-vtt), an Obsidian virtual tabletop that stores scenes as JSON files with a background image, tokens, fog, and pins linking to notes, some marked hidden. The plugin renders each scene as a page and as an embed in notes. Not a commitment to support Atlas. Needs:

- Content loader for a non-markdown file extension
- Adding generated pages to the content store, with their own template and URL
- Embed handler for a file type
- Read access to the content store and link resolution (pin targets to URLs, dropped pages)
- Asset registration (images referenced by the file)
- Plugin static assets (client-side JS/CSS)
- Reading the active audience profile (see `ideas.md`) to filter hidden objects

Build hooks alone can't cover this: they can write source files but can't see the store or link resolution.

## Open Questions

- Plugin discovery and loading mechanism (entry points, convention-based, or config-declared)
- Dependency resolution between plugins and themes
- Plugin configuration (own section in `rockgarden.toml` or separate config)
- How plugin-provided templates integrate with the ChoiceLoader resolution order
- Which of the extension points from the fit-test use cases join the registration list, and which internal APIs (content store, link resolution, assets) they expose for the 1.0 contract
