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

## Conventions

- Uses conventional commits (commitizen configured)
- Requires Python 3.13+
- Config file: `rockgarden.toml`
- Pre-release project: no need to preserve backwards compatibility

## Feature Docs

Before implementing features, check the docs in `docs/features/`:
- `docs/features/README.md` - Feature list and status
- `docs/features/NN-*.md` - Detailed feature specs

After completing features, update these docs to reflect current state.
