# Feature 05: Callouts

Convert Obsidian callout syntax to styled HTML blocks.

## Status: Not Started

## Obsidian Callout Syntax

```markdown
> [!note] Optional Title
> Callout content here.
> Can span multiple lines.

> [!warning]
> No title, just type.

> [!tip]+ Collapsible (expanded by default)
> Content

> [!info]- Collapsible (collapsed by default)
> Content
```

## Callout Types

Standard types to support:
- `note`, `abstract`, `summary`, `tldr`
- `info`
- `tip`, `hint`, `important`
- `success`, `check`, `done`
- `question`, `help`, `faq`
- `warning`, `caution`, `attention`
- `failure`, `fail`, `missing`
- `danger`, `error`
- `bug`
- `example`
- `quote`, `cite`

## Implementation Plan

1. Parse callout blocks during markdown processing
2. Extract type, title, and collapsible state
3. Render as styled HTML with appropriate icons
4. Support nested callouts

## Output HTML

```html
<div class="callout callout-note">
  <div class="callout-title">
    <span class="callout-icon">ℹ️</span>
    <span class="callout-title-text">Note</span>
  </div>
  <div class="callout-content">
    <p>Callout content here.</p>
  </div>
</div>
```

For collapsible:
```html
<details class="callout callout-tip" open>
  <summary class="callout-title">...</summary>
  <div class="callout-content">...</div>
</details>
```

## Key Files to Create/Modify

- `obsidian/callouts.py` - New module for callout parsing
- `templates/base.html` - Add callout CSS styles
- `output/builder.py` - Integrate callout processing
