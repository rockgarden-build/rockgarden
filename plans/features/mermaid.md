# Mermaid Diagram Rendering

## Status: Done

## Problem

The Markdown Support docs claim mermaid is supported "via markdown-it-py", but markdown-it-py only outputs `<pre><code class="language-mermaid">` — no diagram rendering happens. Diagrams display as raw text.

## Approach

Load mermaid.js from CDN in the default theme and add a small init script that converts `<code class="language-mermaid">` blocks into mermaid-renderable elements.

### `src/rockgarden/templates/base.html`

Add mermaid.js via ESM module import (after existing scripts, before `</body>` or in head):

```html
<script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
    mermaid.initialize({ startOnLoad: false, theme: 'default' });
    document.querySelectorAll('code.language-mermaid').forEach(function(el) {
        const pre = el.parentElement;
        const div = document.createElement('div');
        div.classList.add('mermaid');
        div.textContent = el.textContent;
        pre.replaceWith(div);
    });
    await mermaid.run();
</script>
```

This:
1. Finds all `<code class="language-mermaid">` elements (what markdown-it-py outputs for ` ```mermaid ` fences)
2. Replaces their parent `<pre>` with a `<div class="mermaid">` containing the raw diagram text
3. Runs mermaid to render all diagrams

### `plans/ideas.md`

Add a future idea:
- **Build-time mermaid rendering**: Option to render mermaid diagrams to SVG at build time instead of requiring client-side JS. Could use mermaid CLI (`mmdc`) as a post-processing step.

## Verification

1. `just ci` — tests pass
2. `just build-docs` — docs site builds
3. Add a test mermaid block to a doc page and verify it renders as a diagram in the browser
4. Verify pages without mermaid blocks are unaffected (no console errors)
