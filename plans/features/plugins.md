# Plugins

## Status: Future

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

## Open Questions

- Plugin discovery and loading mechanism (entry points, convention-based, or config-declared)
- Dependency resolution between plugins and themes
- Plugin configuration (own section in `rockgarden.toml` or separate config)
- How plugin-provided templates integrate with the ChoiceLoader resolution order
