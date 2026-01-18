# Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Obsidian Vault │ ──▶ │   Data Store    │ ──▶ │   HTML Output   │
│   (Markdown)    │     │   (API Layer)   │     │   (Jinja2)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Project Structure

```
rockgarden/
├── pyproject.toml
├── src/
│   └── rockgarden/
│       ├── __init__.py
│       ├── cli.py              # typer CLI
│       ├── config.py           # TOML config loading
│       ├── content/
│       │   ├── __init__.py
│       │   ├── store.py        # Content store & API
│       │   ├── loader.py       # File discovery & parsing
│       │   └── models.py       # Content/model classes
│       ├── obsidian/
│       │   ├── __init__.py
│       │   ├── wikilinks.py    # [[link]] processing
│       │   ├── embeds.py       # ![[embed]] processing
│       │   └── callouts.py     # Callout conversion
│       ├── render/
│       │   ├── __init__.py
│       │   ├── engine.py       # Jinja2 setup
│       │   └── markdown.py     # markdown-it-py setup
│       └── output/
│           ├── __init__.py
│           ├── builder.py      # Site generation
│           └── search.py       # Search index
└── templates/                  # Default Jinja2 templates
    ├── base.html
    ├── page.html
    └── folder.html
```

## Dependencies

- `typer` - CLI
- `markdown-it-py` - Markdown parsing
- `jinja2` - Templates
- `python-frontmatter` - YAML frontmatter
- `tomllib` (stdlib 3.11+) - Config parsing

## Decisions

- **Project name:** `rockgarden` (available on PyPI)
- **Config format:** TOML (`rockgarden.toml`)
- **Package manager:** uv
- **Templating:** Jinja2
- **CLI framework:** typer (rich integration later)
- **Markdown parser:** markdown-it-py (CommonMark, extensible)
- **Formatting/Linting:** ruff
- **Testing:** pytest
- **Version bumping:** commitizen
- **Commit style:** conventional commits
