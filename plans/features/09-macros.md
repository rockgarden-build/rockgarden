# Feature 09: Macros

User-defined Jinja2 macros in `_macros/` directory.

## Status: Not Started

## Goal

Allow users to define reusable content snippets:

```
my-site/
├── _macros/
│   └── dnd.html
├── content/
│   └── characters/
│       └── olvir.md
```

`_macros/dnd.html`:
```jinja
{% macro stat_block(name, ac, hp, speed) %}
<div class="stat-block">
  <h3>{{ name }}</h3>
  <p><strong>AC:</strong> {{ ac }} | <strong>HP:</strong> {{ hp }} | <strong>Speed:</strong> {{ speed }}</p>
</div>
{% endmacro %}

{% macro beyond_link(id, name) %}
<a href="https://www.dndbeyond.com/monsters/{{ id }}" target="_blank">{{ name }}</a>
{% endmacro %}
```

Usage in markdown:
```markdown
# Olvir

{{ stat_block("Olvir", 15, "45", "30 ft.") }}

See also: {{ beyond_link("16938", "Goblin") }}
```

## Implementation Plan

### 1. Load Macros

```python
def load_macros(macros_dir: Path) -> dict[str, str]:
    """Load all .html files from _macros/ directory."""
    macros = {}
    for file in macros_dir.glob("*.html"):
        macros[file.stem] = file.read_text()
    return macros
```

### 2. Pre-process Content

Before markdown rendering, process Jinja2 in content:

```python
def preprocess_content(content: str, macros: dict, page: Page) -> str:
    env = Environment()
    for name, macro_content in macros.items():
        env.from_string(macro_content)  # Register macros
    template = env.from_string(content)
    return template.render(page=page)
```

### 3. Integrate with Build

In `builder.py`:
```python
macros = load_macros(source / "_macros")
for page in pages:
    content = preprocess_content(page.content, macros, page)
    # Continue with normal processing
```

## Configuration

```toml
[macros]
enabled = true
directory = "_macros"
```

## Key Files to Create/Modify

- `macros.py` - New module for macro loading/processing
- `output/builder.py` - Integrate macro preprocessing
