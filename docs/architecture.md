# Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Obsidian Vault │ ──▶ │   Data Store    │ ──▶ │   HTML Output   │
│   (Markdown)    │     │   (API Layer)   │     │   (Jinja2)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Design Principles

- **Works with Obsidian vaults as-is:** Point rockgarden at any Obsidian vault and get a working site. No special folder structure or file naming required beyond what Obsidian uses.
- **Custom behavior is additive:** The core generator handles standard Obsidian syntax. Site-specific customizations (custom components, special frontmatter handling) are added through a clear extension process, not by modifying the vault.
- **Build speed:** Prioritize efficient builds without sacrificing core concepts.

## Project Structure

```
rockgarden/
├── pyproject.toml
├── src/
│   └── rockgarden/
│       ├── __init__.py
│       ├── cli.py              # typer CLI
│       ├── config.py           # TOML config loading
│       ├── urls.py             # URL/path generation utilities
│       ├── links.py            # Markdown link transformation
│       ├── content/
│       │   ├── __init__.py
│       │   ├── store.py        # Content store & API
│       │   ├── loader.py       # File discovery & parsing
│       │   └── models.py       # Content/model classes
│       ├── nav/
│       │   ├── __init__.py
│       │   ├── tree.py         # Navigation tree builder
│       │   ├── breadcrumbs.py  # Breadcrumb generation
│       │   └── folder_index.py # Folder index generation
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

## Extension System

Rockgarden supports customization through a layered approach:

### Jinja2 Macros (current)

Users place macro files in a `_macros/` directory within their site. These are auto-loaded and available in templates as `macros.<filename>.<macro_name>()`.

```jinja2
{# _macros/beyond_link.html #}
{% macro beyond_link(page) %}
  {% if page.frontmatter.beyondUrl %}
  <a href="{{ page.frontmatter.beyondUrl }}" class="beyond-link">
    {{ page.frontmatter.title }} on D&D Beyond
  </a>
  {% endif %}
{% endmacro %}
```

Usage in templates: `{{ macros.beyond_link.beyond_link(page) }}`

### Template Overrides & Themes

Templates are resolved in this order (first match wins):

1. **Site templates** (`_templates/`) - Override individual templates
2. **Theme** (`_themes/<name>/`) - Replace the full template set
3. **Built-in defaults** - Ship with rockgarden

This allows:
- **Single file override:** Drop `_templates/page.html` to customize just the page layout
- **Full theme:** Set `theme = "mytheme"` in config, provide `_themes/mytheme/` with complete template set
- **Zero config:** Works out of the box with sensible defaults

Templates can `{% extend %}` from any level. A site's `_templates/page.html` can extend the built-in `base.html`, or a theme's base.

### Python Plugins (future)

For more complex needs, Python plugins in `_plugins/` can hook into:
- Markdown preprocessing/postprocessing
- Template context injection
- Custom build steps
- Additional Jinja2 filters/globals

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
