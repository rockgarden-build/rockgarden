# GFM Syntax Highlighting

Part of full GFM support. Fenced code blocks with a language tag should get colorized syntax highlighting.

## Approach

Build-time highlighting with **Pygments** (Python-native). No added JS payload, works offline, fits the Python toolchain. The alternative (client-side highlight.js/Prism) adds page weight and causes flash-of-unstyled-code.

## Changes

- `pyproject.toml` — add `pygments>=2.17.0` dependency
- `src/rockgarden/render/markdown.py` — add custom `fence` render rule that passes code through Pygments `highlight()`. Falls back to default `<pre><code>` for unknown/missing languages.
- `static-src/input.css` — add `.highlight pre` base styles (padding, border-radius, overflow)
- Pygments theme CSS — generate light/dark theme stylesheets scoped to `[data-theme]` attributes. Either embed in `input.css` or add a separate `highlight.css` to `src/rockgarden/static/` (if separate file, add `<link>` in `src/rockgarden/templates/base.html`)
- `src/rockgarden/static/rockgarden.css` — rebuild via `just css`
- `docs/Markdown Support.md` — update syntax highlighting row: ❌ → ✅
- `plans/issues.md` — remove syntax highlighting issue
- New: `tests/test_syntax_highlight.py` — test known language produces Pygments spans, unknown language falls back to plain code, no-language falls back, content is HTML-escaped

## Open Question

How to handle light/dark Pygments themes — embed both in CSS with `[data-theme]` selectors, or pick a single theme that works in both?

## Verification

1. `just check` — lint and format check passes
2. `just test` — all tests pass including new ones
3. `just build` — demo site builds
4. `just build-docs` — docs site builds
5. Manual inspection of rendered code blocks with various languages
