# Vision

Rockgarden is a Python static site generator built around progressive customization. It works with Obsidian vaults and plain markdown folders out of the box, then scales up to a general-purpose SSG through incremental configuration.

## Core Principle

**You should never need more complexity than your site demands.**

- A personal wiki needs zero config. Point at a folder, get a site.
- A project docs site might need custom navigation and a theme.
- A conference website needs collections, data pipelines, and custom templates.

All three should use the same tool. Complexity is additive — you opt into features as you need them, and the defaults stay out of your way.

## Progressive Customization Ladder

1. **Zero config** — Markdown files become pages. Obsidian syntax just works.
2. **Convention** — Drop files in `_styles/`, `_scripts/`, `_templates/` and they're picked up automatically.
3. **Configuration** — `rockgarden.toml` for collections, navigation, themes, build hooks.
4. **Full control** — Custom templates, data pipelines, external data sources, build hooks for asset compilation.

## Everything is a Collection

Content is organized into collections. Without config, all content lives in a single implicit default collection. Defining a named collection carves out a directory subset with its own namespace and progressively configurable behavior (schema, templates, page generation, etc.).

This model unifies the simple case (a folder of markdown) with the complex case (typed content from multiple sources generating different page layouts) under one concept.

## Design Principles

- **Universal markdown support.** Rockgarden supports the superset of CommonMark, GFM (GitHub Flavored Markdown), and Obsidian markdown without requiring configuration. Use plain markdown, GFM features (tables, task lists, alerts), Obsidian features (wiki-links, callouts with titles), or mix them freely in the same document. No mode detection, no feature flags — rockgarden handles all syntax gracefully.
- **Works with Obsidian vaults as-is.** No special folder structure or file naming beyond what Obsidian uses.
- **Works with plain markdown.** Obsidian syntax support is additive — plain markdown renders fine without it.
- **Custom behavior is additive.** The core handles the common case. Customizations layer on top without modifying source content.
- **Build stays fast.** External data fetching is separate from the build pipeline. Watch mode rebuilds from local files only.
- **No lock-in.** Content is plain files on disk. There is no proprietary format or database.
