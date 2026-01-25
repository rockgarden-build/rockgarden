# Feature 10: Progressive Customization (In Progress)

Enable customization from zero-config to fully custom site generation.

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
