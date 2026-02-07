# Feature 16: Static Assets (Custom CSS & JS)

Convention-based custom CSS and JavaScript inclusion.

## Status: Not Started

## Goal

Files in `_styles/` and `_scripts/` are copied to output and injected into default templates. No compilation — just plain CSS and JS by default. Users who want SCSS, Tailwind, or bundling use build hooks (Feature 15) and custom templates.

## Use Cases

- Add custom CSS to style content beyond what DaisyUI provides
- Include client-side JavaScript for interactive features
- Override default styling without replacing the entire template
- Provide a CSS entry point for build hooks to compile into

## Directory Convention

```
my-site/
├── _styles/
│   ├── custom.css
│   └── components.css
├── _scripts/
│   └── main.js
├── content/
│   └── ...
```

## Behavior

1. Files in `_styles/` are copied to `_site/styles/`
2. Files in `_scripts/` are copied to `_site/scripts/`
3. Default templates inject `<link>` and `<script>` tags for all discovered files
4. Custom templates can reference whatever they want

## Implementation Plan

### 1. Discovery

```python
def discover_assets(source: Path) -> tuple[list[Path], list[Path]]:
    styles = sorted((source / "_styles").glob("*.css"))
    scripts = sorted((source / "_scripts").glob("*.js"))
    return styles, scripts
```

### 2. Copy to Output

Copy files to `_site/styles/` and `_site/scripts/` during build.

### 3. Template Injection

Pass discovered asset paths to template context:

```html
{# In base.html #}
{% for style in styles %}
<link rel="stylesheet" href="{{ site.base_url }}styles/{{ style }}">
{% endfor %}

{% for script in scripts %}
<script src="{{ site.base_url }}scripts/{{ script }}"></script>
{% endfor %}
```

## Key Files to Create/Modify

- `output/builder.py` — Discover and copy assets, pass to templates
- `templates/base.html` — Add asset injection blocks
