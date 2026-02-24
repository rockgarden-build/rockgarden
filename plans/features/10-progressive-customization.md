# Feature 10: Progressive Customization (In Progress)

Enable customization from zero-config to fully custom site generation. See [concepts.md](../concepts.md) for terminology and the full 6-level customization ladder.

## Customization Levels

### Level 1: Zero Config
`rockgarden build` produces working site with default DaisyUI "light" theme. **Already works.**

### Level 2: DaisyUI Theme Selection
```toml
[theme]
daisyui = "cupcake"
```
Available themes: light, dark, cupcake, cyberpunk, forest, etc. ([DaisyUI themes](https://daisyui.com/docs/themes/))

### Level 3: Override Specific Templates
```
_templates/components/nav.html  # Override just the nav
```
Templates available: `base.html`, `page.html`, `folder_index.html`, `components/nav.html`, `components/breadcrumbs.html`, `components/theme_toggle.html`. **Already works via ChoiceLoader.**

#### Template Block Hooks

`page.html` exposes named Jinja2 blocks as customization points. Empty blocks act as hooks — zero output by default, available for user overrides without replacing the entire template.

**Content area blocks:**
- `before_heading` — empty hook (e.g., publication date)
- `heading` — page `<h1>` (has default content; named `heading` to avoid collision with `base.html`'s `title` block for `<title>`)
- `after_heading` — empty hook (tags, reading time, custom frontmatter like D&D Beyond links)
- `body` — rendered markdown (has default content)
- `after_body` — empty hook (prev/next links, supplementary content)

**Right sidebar blocks:**
- `right_sidebar` — parent block wrapping sidebar content
- `toc` — empty hook (table of contents)
- `backlinks` — backlinks display (has default content)

**Usage example** — a site adds a custom frontmatter link after the title:
```jinja2
{% extends "rockgarden/page.html" %}

{% block after_heading %}
{% if page.frontmatter.beyondUrl %}
<a href="{{ page.frontmatter.beyondUrl }}">{{ page.title }} on D&D Beyond</a>
{% endif %}
{% endblock %}
```

Blocks with default content can be extended with `{{ super() }}` to add to them rather than replace.

### Level 4: Custom Layouts
```yaml
---
layout: landing
---
```
Create `_templates/layouts/landing.html` extending `base.html`. Use `{% block body %}` for content.

### Level 5: Full Theme Replacement
Replace `_templates/base.html` for complete control. **Already works.**

## Implementation Phases

### Phase A: DaisyUI Theme Config ✅
- [x] Add `daisyui` field to `ThemeConfig` in `config.py`
- [x] Update `base.html` to use `{{ site.daisyui_theme }}`
- [x] Pass theme to site_config in `builder.py`

### Phase A-2: Template Decomposition
- [x] Add named blocks to `page.html` (`before_heading`, `heading`, `after_heading`, `body`, `after_body`)
- [x] Add right sidebar blocks (`right_sidebar`, `toc`, `backlinks`)
- [ ] Verify user template overrides work with new block structure (ChoiceLoader)
- [x] Update `folder_index.html` with common blocks (`breadcrumbs`, `before_heading`, `heading`, `after_heading`)

### Phase B: Layout System
- [ ] Extract `base.html` to minimal skeleton
- [ ] Create `layouts/docs.html` (current sidebar layout)
- [ ] Create `layouts/landing.html` (simple full-width)
- [ ] Add `resolve_layout()` to `engine.py`
- [ ] Update `page.html` and `folder_index.html` to extend variable layout

### Phase C: Documentation
- [ ] Document template override system
- [ ] Document available blocks and context variables
- [ ] Document layout creation

## Files to Modify

| File | Phase | Changes |
|------|-------|---------|
| `config.py` | A | Add `daisyui` field |
| `builder.py` | A | Pass theme to site_config |
| `templates/base.html` | A, B | Use theme var; extract to skeleton |
| `templates/layouts/docs.html` | B | New - current sidebar layout |
| `templates/layouts/landing.html` | B | New - simple layout |
| `templates/page.html` | B | Extend layout_template variable |
| `templates/folder_index.html` | B | Extend layout_template variable |
| `render/engine.py` | B | Add `resolve_layout()`, update `render_page()` |

## Verification

- `uv run pytest`
- Build with no config → "light" theme
- Build with `daisyui = "dark"` → dark theme
- Page with `layout: landing` → no sidebar
- Custom `_templates/layouts/custom.html` → works when specified
