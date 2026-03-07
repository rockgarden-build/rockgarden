# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Rockgarden is a Python-based static site generator designed to work directly with Obsidian vaults. It converts markdown files with Obsidian-specific syntax (wiki-links, embeds, callouts) into navigable HTML sites.

## Development Commands

Use `just` for common tasks (see `justfile` for full list):

```bash
just install       # Install Python + Node dependencies
just test          # Run tests
just check         # Lint and format check
just format        # Auto-fix lint and format
just ci            # Run lint + tests (CI equivalent — run before marking work done)
just build         # Build the demo site (./site)
just build-docs    # Build the docs site (./docs)
just serve         # Serve output directory locally
just css           # Compile Tailwind CSS
just css-watch     # Watch and recompile Tailwind CSS
```

For single tests or other direct invocations:

```bash
uv run pytest tests/test_cli.py::test_version
uv run rockgarden --help
uv run rgdn --help  # short alias
```

## Architecture

The project follows a three-stage pipeline:
1. **Content Ingestion**: Read Obsidian vault markdown files, parse frontmatter
2. **Data Store**: In-memory API layer for querying content (`get_content()`, `list_content()`, `get_backlinks()`)
3. **HTML Output**: Jinja2 templates render the final static site

Module structure in `src/rockgarden/`:
- `cli.py` - Typer CLI with `build` and `serve` commands
- `config.py` - TOML config loading (`rockgarden.toml`)
- `content/` - Content store, file loader, data models
- `nav/` - Navigation tree, breadcrumbs, folder index generation
- `obsidian/` - Wiki-link, embed, and callout processing
- `render/` - Jinja2 and markdown-it-py setup
- `output/` - Site builder

## CSS / Tailwind

CSS is built separately from Python via Tailwind CLI. The compiled output is committed to the repo.

- **Source**: `static-src/input.css` (Tailwind directives + custom CSS)
- **Output**: `src/rockgarden/static/rockgarden.css` (compiled, minified)
- **Config**: `tailwind.config.js` (scans `src/rockgarden/templates/**/*.html`)
- **Build**: `just css`
- **Watch**: `just css-watch`

**After any template change that adds new Tailwind/daisyUI utility classes, you MUST run `just css` to regenerate the CSS.** Never use inline styles as a workaround for missing utility classes.

## Conventions

- Uses conventional commits (commitizen configured)
- Requires Python 3.13+
- Config file: `rockgarden.toml`
- Pre-release project: no need to preserve backwards compatibility

## Template Block Conventions

Page templates use named Jinja2 blocks as override points. When adding new features that render content on pages, place them in the appropriate block rather than adding inline to `page.html`. Empty blocks serve as hooks for user customization — preserve them even when adding default content.

Current block zones in `page.html`:
- `before_heading` / `after_heading` — metadata, tags, custom frontmatter rendering
- `body` — the rendered markdown
- `after_body` — supplementary content (prev/next, etc.)
- `right_sidebar` — TOC, backlinks

When decomposing or extending templates, maintain these blocks so user template overrides continue to work.
