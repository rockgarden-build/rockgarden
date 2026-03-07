---
tags: [design, philosophy]
---

# Vision

Rockgarden is a static site generator built for progressive customization. It works with Obsidian vaults and plain markdown folders out of the box, but is a general-purpose SSG through configuration and customization.

## Core Principles

### Just enough configuration

- A personal wiki needs zero config. Point at folder, get site.
- A project docs site might need custom navigation and a theme.
- A conference website needs collections, data pipelines, and custom templates.

All three share enough in common that they can use the same tool. Complexity is additive: you opt into features as you need them, and the defaults generally work.

### Progressive Customization

1. **Zero config:** Markdown files become pages. Obsidian syntax just works.
2. **Convention:** Drop files in `_styles/`, `_scripts/`, `_templates/` and they're picked up automatically.
3. **Configuration:** `rockgarden.toml` for collections, navigation, themes, build hooks.
4. **Full control:** Custom templates, data pipelines, external data sources, build hooks for asset compilation.

### Everything is a Collection

Content is organized into collections. Without config, all content lives in a single default collection. Defining a named collection carves out a subset with its own namespace and progressively configurable behavior (schema, templates, page generation, etc.).

This model supports the simple case (a folder of markdown) to the complex case (typed content from multiple sources generating different page layouts) under one concept.

## Design Principles

- **Universal markdown support.** Rockgarden aims to support without configuration:
  - CommonMark
  - GitHub Flavored Markdown (GFM)
  - Obsidian markdown
  - Use plain markdown, GFM features (tables, task lists, alerts), Obsidian features (wiki-links, callouts with titles), or mix them freely in the same document. No mode detection, no feature flags necessary.
- **Works with Obsidian vaults as-is.** No special folder structure or file naming beyond what Obsidian uses.
- **Works with plain markdown.** Obsidian syntax support is additive: plain markdown renders fine without it.
- **Custom behavior is additive.** The core handles the common case. Customizations layer on top without modifying source content.
- **Build stays fast.** External data fetching is separate from the build pipeline. Builds only read local files.

## Acknowledgements

Rockgarden was inspired by [Quartz](https://quartz.jzhao.xyz/), a static site generator for Obsidian vaults. When I found myself increasingly customizing my installation I decided to start building my own implementation, with the features I always wanted in a static site generator.
