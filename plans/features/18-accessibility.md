# Feature 18: Accessibility Defaults

Improve default templates to meet basic accessibility standards.

## Status: Not Started

## Goal

Update built-in templates with foundational accessibility features. No new systems — just better HTML in the defaults.

## Changes

### Skip-to-Content Link

Add as first element in `<body>`:

```html
<a href="#main-content" class="sr-only focus:not-sr-only">Skip to content</a>
```

### ARIA Landmarks

Ensure proper roles on existing elements:

```html
<nav aria-label="Main navigation">...</nav>
<aside aria-label="Sidebar">...</aside>
<main id="main-content">...</main>
```

### Focus-Visible Styles

Add visible focus indicators that work on both light and dark backgrounds:

```css
:focus-visible {
    outline: 2px solid currentColor;
    outline-offset: 2px;
}
```

### Semantic Heading Hierarchy

Ensure default templates produce a logical heading order (h1 → h2 → h3). The page title should be the only `<h1>`.

## Key Files to Modify

- `templates/base.html` — Skip link, landmark roles, focus styles
- `templates/components/nav.html` — ARIA labels
- `templates/page.html` — Main content landmark
