# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Rockgarden is a Python-based static site generator designed to work directly with Obsidian vaults. It converts markdown files with Obsidian-specific syntax (wiki-links, embeds, callouts) into navigable HTML sites.

## Development Commands

```bash
# Install dependencies (uses uv)
uv sync

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/test_cli.py::test_version

# Lint and format
uv run ruff check .
uv run ruff format .

# Run CLI
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
- **Build**: `npm run build:css`
- **Watch**: `npm run watch:css`

**After any template change that adds new Tailwind/daisyUI utility classes, you MUST run `npm run build:css` to regenerate the CSS.** Never use inline styles as a workaround for missing utility classes.

## Conventions

- Uses conventional commits (commitizen configured)
- Requires Python 3.13+
- Config file: `rockgarden.toml`
- Pre-release project: no need to preserve backwards compatibility

## Template Block Conventions

Page templates use named Jinja2 blocks as override points. When adding new features that render content on pages, place them in the appropriate block rather than adding inline to `page.html`. Empty blocks serve as hooks for user customization — preserve them even when adding default content.

Current block zones in `page.html` (see Feature 10 spec for full details):
- `before_heading` / `after_heading` — metadata, tags, custom frontmatter rendering
- `body` — the rendered markdown
- `after_body` — supplementary content (prev/next, etc.)
- `right_sidebar` — TOC, backlinks

When decomposing or extending templates, maintain these blocks so user template overrides continue to work.

## Feature Implementation Workflow

**REQUIRED** — every feature implementation MUST follow these steps:

1. **Before starting**: Check `plans/features/README.md` and the feature's spec doc (`plans/features/NN-*.md`)
2. **When starting**: Update `plans/implementation.md` to mark the feature as in progress
3. **After completing**: Update all of these before considering the feature done:
   - `plans/implementation.md` — mark checklist items as complete
   - `plans/features/README.md` — update feature status and Quartz reference checklist
   - Feature spec doc (if one exists) — update status to reflect completion
