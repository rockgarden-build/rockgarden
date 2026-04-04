# GFM Footnotes

Part of full GFM support. `[^1]` references and `[^1]: text` definitions should render as proper footnotes with backlinks.

Depends on `mdit-py-plugins` being added (see gfm-task-lists.md).

## Changes

- `src/rockgarden/render/markdown.py` — import and enable `footnote_plugin` from `mdit_py_plugins.footnote`
- `static-src/input.css` — add footnote styles (`.footnotes` section border/spacing, `.footnote-ref` and `.footnote-backref` link styles)
- `src/rockgarden/static/rockgarden.css` — rebuild via `just css`
- `docs/Markdown Support.md` — update footnotes row: ❌ → ✅
- `plans/issues.md` — remove footnotes issue
- New: `tests/test_footnotes.py` — test single/multiple footnotes, backlinks, inline footnotes if supported

## Verification

1. `just check` — lint and format check passes
2. `just test` — all tests pass including new ones
3. `just build` — demo site builds
4. `just build-docs` — docs site builds
5. Manual inspection of rendered footnote output
