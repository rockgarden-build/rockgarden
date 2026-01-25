# Feature 01: Home Page ✅

Render `index.md` from an Obsidian vault to `_site/index.html` with basic styling. Wiki-links rendered as plain text (no resolution).

## Goal

```
uv run rockgarden build --source /path/to/vault --output _site
```

Produces `_site/index.html` from `vault/index.md` (or `vault/content/index.md` for Quartz-style layouts).

## Implementation Steps

### 1. Config Loading (`config.py`)

Load `rockgarden.toml` from current directory or specified path.

```toml
# rockgarden.toml
[site]
title = "My Site"
source = "."           # or "content" for Quartz-style
output = "_site"

[build]
ignore_patterns = [".obsidian", "private", "templates"]

[theme]
name = ""              # empty = use defaults; or name of theme in _themes/
```

Note: Full theme support comes later, but we design the template engine to support the resolution order from the start (site `_templates/` → theme → built-in defaults).

- Use `tomllib` (stdlib)
- Provide sensible defaults
- CLI flags override config values

### 2. Content Model (`content/models.py`)

```python
@dataclass
class Page:
    source_path: Path      # absolute path to .md file
    slug: str              # URL path (e.g., "index", "NPCs/olvir")
    frontmatter: dict      # parsed YAML
    content: str           # raw markdown (post-frontmatter)
    html: str | None       # rendered HTML (populated later)
```

### 3. Content Loader (`content/loader.py`)

- Discover `.md` files in source directory
- Skip files matching ignore patterns
- Parse frontmatter with `python-frontmatter`
- Return list of `Page` objects

```python
def load_content(source: Path, ignore: list[str]) -> list[Page]:
    ...
```

### 4. Markdown Rendering (`render/markdown.py`)

- Set up `markdown-it-py` with basic config
- For now: standard CommonMark rendering
- Wiki-links `[[Name]]` pass through as literal text

```python
def render_markdown(content: str) -> str:
    ...
```

### 5. Template Engine (`render/engine.py`)

- Set up Jinja2 environment with layered loader
- Resolution order: site `_templates/` → theme → package defaults
- For M1: just package defaults, but structure supports future layers

```python
def create_engine(
    site_templates: Path | None,
    theme_templates: Path | None,
) -> jinja2.Environment:
    # Uses Jinja2 ChoiceLoader for resolution order
    ...

def render_page(engine: Environment, page: Page) -> str:
    ...
```

### 6. Default Templates (`templates/`)

**`base.html`:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page.title }} - {{ site.title }}</title>
    <style>/* minimal inline CSS */</style>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
```

**`page.html`:**
```html
{% extends "base.html" %}
{% block content %}
<article>
    <h1>{{ page.title }}</h1>
    {{ page.html | safe }}
</article>
{% endblock %}
```

### 7. Builder (`output/builder.py`)

Orchestrate the build:

```python
def build_site(config: Config) -> None:
    pages = load_content(config.source, config.ignore_patterns)
    engine = create_engine(...)

    for page in pages:
        page.html = render_markdown(page.content)
        output = render_page(engine, page)
        write_file(config.output / f"{page.slug}.html", output)
```

### 8. CLI Updates (`cli.py`)

```python
@app.command()
def build(
    source: Path = typer.Option(None, help="Source directory"),
    output: Path = typer.Option(None, help="Output directory"),
    config: Path = typer.Option(None, help="Config file path"),
) -> None:
    ...
```

## Dependencies to Add

```toml
dependencies = [
    "typer>=0.9.0",
    "jinja2>=3.1.0",
    "markdown-it-py>=3.0.0",
    "python-frontmatter>=1.0.0",
]
```

## Test Plan

1. **Config loading:** Parse sample TOML, verify defaults
2. **Content loader:** Load test vault, verify Page objects
3. **Markdown rendering:** Basic markdown → HTML
4. **Template rendering:** Page object → complete HTML
5. **Integration:** Build freemenswood index.md, verify output

## Out of Scope

- Wiki-link resolution
- Embeds (images, audio)
- Multiple pages
- Search, navigation, sidebars
- CSS styling beyond minimal layout

## Success Criteria

Running `uv run rockgarden build` against freemenswood vault produces `_site/index.html` containing:
- Page title from frontmatter
- Rendered markdown content
- Wiki-links visible as `[[text]]` (unresolved)
