# Agent & Developer Guide

Guidance for working with this codebase. See [docs/](docs/) for full documentation.

## Commands

Use `just` for common tasks (see `justfile` for full list):

- `just install` — install Python + Node dependencies
- `just test` — run tests
- `just check` — lint and format check
- `just format` — auto-fix lint and format
- `just ci` — lint + tests (run before submitting)
- `just build` — build the demo site (./site)
- `just build-docs` — build the docs site (./docs)
- `just serve` — serve output directory locally
- `just css` — compile Tailwind CSS
- `just css-watch` — watch and recompile Tailwind CSS

Single test: `uv run pytest tests/test_cli.py::test_version`

## Directory Structure

- `src/rockgarden/` — main package
  - `cli.py` — Typer CLI (`build`, `serve`, `theme`, `init`)
  - `config.py` — TOML config loading
  - `content/` — content store, file loader, data models
  - `nav/` — navigation tree, breadcrumbs, folder index
  - `obsidian/` — wiki-link, embed, callout processing
  - `render/` — Jinja2 and markdown-it-py setup
  - `output/` — site builder
- `src/rockgarden/templates/` — default theme templates
- `src/rockgarden/static/` — compiled CSS + JS
- `static-src/input.css` — Tailwind source CSS
- `docs/` — documentation (built with rockgarden itself)

## Conventions

- Conventional commits (commitizen configured)
- Python 3.13+
- Config: `rockgarden.toml`
- Formatting/linting: ruff
- Testing: pytest

## CSS Build

CSS is built separately via Tailwind CLI. The compiled output is committed.

After any template change that adds new Tailwind/daisyUI utility classes, run `just css` to regenerate. Never use inline styles as a workaround.

## Template Customization

See [docs/Architecture.md](docs/Architecture.md) for template block conventions and the customization system.
