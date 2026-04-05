# Tier 1 & 2 Implementation Plan

Features expected of a modern SSG (Tier 1) and Obsidian-niche differentiators (Tier 2), informed by how Hugo, Eleventy, Astro, Quartz, MkDocs, and Zola handle these.

One branch + PR per item. Plan → implement → test → PR → feedback → merge cycle.

## Progress

- [x] 1a. Heading link fragments not slugified
- [x] 1b. Macros not processed in transclusions
- [x] 2a. Math rendering (KaTeX)
- [x] 2b. Highlights (`==text==`)
- [x] 2c. Comment stripping (`%% comment %%`)
- [ ] 3. Nav reverse ordering
- [ ] 4. Dev server custom 404
- [ ] 5. Incremental builds
- [ ] 6. Dev mode with live reload
- [ ] 7. Example/demo site

---

## SSG Comparison Notes

| Feature | Hugo | Eleventy | Quartz | MkDocs | Zola |
|---------|------|----------|--------|--------|------|
| Dev server | Built-in, WebSocket live reload | Built-in, DOM diffing | Built-in, hot-reload | Built-in, auto-reload | Built-in, debounced reload |
| Incremental | Partial rebuild in watch mode | `--incremental` flag, dep tracking | Incremental content rebuilds | Dirty reload flag | ~50ms full builds (not needed) |
| Math | KaTeX (build-time) | Plugin (community) | KaTeX (build-time) | KaTeX/MathJax via Material | KaTeX via shortcodes |
| Custom 404 dev | Yes | Yes | Theme-dependent | No | Theme-dependent |
| Error feedback | Console | Error overlay plugin | Console | Console | Console |

**Key takeaway**: Every SSG in this list has a built-in dev server with live reload. Most use WebSocket or SSE injection. KaTeX is the standard for math. Incremental builds vary — fast SSGs (Zola, Hugo) don't need them; Python-based ones (MkDocs, Eleventy) rely on them for DX.

---

## Phase 1: Bug Fixes

No new dependencies. Can land immediately.

### 1a. Heading link fragments not slugified

**Problem**: `resolve_link()` in `store.py:124` appends fragment as-is (`#My Heading`), but `extract_toc()` in `toc.py` generates slugified IDs (`#my-heading`) via `_slugify()`. Links like `[[Page#My Heading]]` never match the rendered anchor.

**Approach**: Extract `_slugify` from `toc.py` to a shared location, use it in `resolve_link()`.

**Files**:
- `src/rockgarden/urls.py` — add `slugify_heading()` (move logic from `toc.py:21-25`)
- `src/rockgarden/nav/toc.py` — import from `urls`, remove local `_slugify`
- `src/rockgarden/content/store.py:123-124` — slugify fragment before appending
- Tests: `test_content_store.py` (resolve_link with fragment), `test_toc.py` (no regression)

### 1b. Macros not processed in transclusions

**Problem**: `_make_note_resolver()` in `builder.py:155-213` runs media embeds, transclusions, wikilinks, callouts on transcluded content — but never calls `apply_macros()`. Macro syntax in transcluded notes renders literally.

**Approach**: Thread `apply_macros` callable into `_make_note_resolver`. Call it on `sub_content` at line 188 before media processing.

**Files**:
- `src/rockgarden/output/builder.py:155` — add `apply_macros` param to `_make_note_resolver`, call on `sub_content` before line 189. Update recursive call (line 194) and both call sites.
- Tests: `test_transclusions.py` (macro in transcluded note expands)

---

## Phase 2: Markdown Extensions

Independent of Phase 1. Can parallelize.

### 2a. Math rendering

**Approach**: Math parsing is always on via `dollarmath_plugin` (with `allow_digits=False, allow_space=False` to avoid false positives on currency and prose). ` ```math ` fences handled in `_fence_renderer`. Default theme loads KaTeX from CDN by default; `math_cdn = false` config option lets users provide KaTeX locally via `_styles/` and `_scripts/`.

**Files**:
- `src/rockgarden/render/markdown.py` — register `dollarmath_plugin` unconditionally. Handle `lang == "math"` in `_fence_renderer`.
- `src/rockgarden/templates/base.html` — KaTeX CSS+JS from CDN, gated by `{% if site.math_cdn %}`
- `src/rockgarden/config.py` — add `math_cdn: bool = True` to `ThemeConfig` (default-theme-specific section)
- `src/rockgarden/output/builder.py` — pass `math_cdn` into template context
- Tests: `test_math.py` (inline `$x^2$`, block `$$\sum$$`, ` ```math ` fence, dollar signs with digits not parsed)

### 2b. Highlights (`==text==`)

**Approach**: Custom markdown-it-py inline rule plugin. Port logic from JS `markdown-it-mark` — scan for `==`, emit `mark_open`/`mark_close` tokens. The Python markdown-it API mirrors the JS one closely.

**Files**:
- `src/rockgarden/obsidian/highlights.py` — new. `highlight_plugin(md: MarkdownIt)` inline rule
- `src/rockgarden/render/markdown.py` — register plugin
- Tests: `test_highlights.py` (`==text==` → `<mark>text</mark>`, code blocks unaffected)

### 2c. Comment stripping (`%% comment %%`)

**Approach**: Pre-processing regex strip before markdown rendering, with code block protection (same pattern used by transclusions/wikilinks). Regex: `r'%%[\s\S]*?%%'`. Run early in pipeline, before macros (comments might contain macro-like syntax that shouldn't execute).

**Files**:
- `src/rockgarden/obsidian/comments.py` — new. `strip_comments(content: str) -> str`
- `src/rockgarden/output/builder.py` — call early in per-page loop (~line 560), also in `_make_note_resolver`, also in folder index processing
- Tests: `test_comments.py` (inline, multi-line block, preserved in code blocks)

---

## Phase 3: Nav Reverse Ordering

Small config addition. Independent.

**Approach**: Add `reverse: bool = False` to `NavConfig`. Apply `list.reverse()` to unpinned items after sorting in `_sort_nav_nodes()`.

**Files**:
- `src/rockgarden/config.py` — add `reverse` to `NavConfig`
- `src/rockgarden/nav/tree.py:42` — accept `reverse` param, reverse unpinned list when True. Update `build_nav_tree` to pass from config.
- Tests: `test_nav_tree.py` (reverse ordering)

---

## Phase 4: Dev Server Custom 404

Small improvement. No new dependencies.

**Approach**: Subclass `SimpleHTTPRequestHandler` to serve `404.html` from output dir with 404 status when a file isn't found. Override `send_error` or `do_GET`.

**SSG precedent**: Hugo, Eleventy, Astro all do this.

**Files**:
- `src/rockgarden/cli.py:192-239` — replace `partial(SimpleHTTPRequestHandler)` with custom handler class
- Tests: `test_cli.py` (custom 404 handler returns 404.html content)

---

## Phase 5: Incremental Builds

Prerequisite for fast dev mode. Should land before Phase 6.

**Approach**: mtime-based dirty checking with a build manifest at `.rockgarden/build-manifest.json`.

**Scope for v1** (conservative):
- Track content file mtimes. If config, templates, macros, or assets change → full rebuild.
- Global outputs (nav, search index, tag pages, sitemap, feed) always regenerate.
- Only skip the per-page render+write for unchanged pages whose output already exists.
- This handles the 90% dev case: "I edited one page."

**Manifest structure**:
```json
{
  "config_hash": "abc123",
  "template_hash": "def456",
  "pages": {
    "path/to/file.md": {
      "mtime": 1712345678.0,
      "output": "_site/path/to/file/index.html"
    }
  }
}
```

**Files**:
- `src/rockgarden/output/manifest.py` — new. `BuildManifest` class with `load()`, `save()`, `is_page_dirty()`, `is_full_rebuild_needed()`, `update_page()`
- `src/rockgarden/output/builder.py` — load manifest at start, skip clean pages, save at end. Add `incremental: bool` param to `build_site()`
- `src/rockgarden/cli.py` — add `--incremental` / `-i` flag to `build` command
- Tests: `test_incremental.py` (manifest creation, skip unchanged, dirty on edit, full rebuild on config change)

---

## Phase 6: Dev Mode with Live Reload

Largest unit of work. Depends on Phase 5.

**New dependency**: `watchdog>=3.0.0` (file system watcher, Apache-2.0, pure Python, uses FSEvents on macOS natively).

**Architecture**:
1. `rockgarden dev` new CLI command (or `serve --watch`)
2. `watchdog` observer monitors source dir, templates, config, macros, styles
3. On file change (debounced ~300ms), trigger incremental rebuild
4. After rebuild, notify browsers via SSE (Server-Sent Events)
5. Small JS snippet injected at serve time into `</body>` of HTML responses

**Why SSE over WebSocket**: Unidirectional (server→client) is sufficient for "reload now" signals. Works with stdlib `http.server`. No extra dependency needed. Eleventy uses a similar approach.

**Live reload JS** (injected by handler, not baked into templates):
```javascript
(function() {
  var es = new EventSource('/_rockgarden/events');
  es.onmessage = function(e) { if (e.data === 'reload') location.reload(); };
  es.onerror = function() { setTimeout(function() { location.reload(); }, 2000); };
})();
```

**Debouncing**: On each file event, reset a timer. Fire rebuild after 300ms of quiet. Handles editors with temp files or multi-write saves.

**Error handling** (v1): Log to console, skip reload notification. Error overlay is a future enhancement.

**Files**:
- `src/rockgarden/server/` — new subpackage
  - `handler.py` — custom HTTP handler: serves files, 404.html fallback, SSE endpoint at `/_rockgarden/events`, injects live-reload JS into HTML responses
  - `watcher.py` — `FileWatcher` wrapping `watchdog.Observer` with debounce and callback
  - `reloader.py` — `LiveReloadServer` orchestrating HTTP server, watcher, SSE client list
- `src/rockgarden/cli.py` — add `dev` command (or `--watch` flag on `serve`)
- `pyproject.toml` — add `watchdog>=3.0.0`
- Tests: `test_server.py` (SSE headers, 404 fallback, JS injection)

---

## Phase 7: Example/Demo Site

Content and deployment. Can proceed in parallel with Phases 5-6, finalized after feature phases complete.

**Approach**: Flesh out `site/` to showcase all features. Publish via GitHub Pages.

**Content to add**:
- Wikilinks, transclusions, embeds showcase
- Callouts (all types)
- Math examples (after Phase 2a)
- Highlights and comments (after Phases 2b/2c)
- Collections demo
- Nav ordering / customization
- Macros usage
- Nested folders (nav tree, breadcrumbs, folder indexes)

**Publishing**:
- `.github/workflows/deploy-demo.yml` — build + deploy to GitHub Pages
- Set `base_url` in `rockgarden.toml`

---

## Implementation Sequence

```
Phase 1 (bug fixes)            ─┐
Phase 2 (markdown extensions)   ├── can all run in parallel
Phase 3 (nav reverse)           │
Phase 4 (dev 404)              ─┘
Phase 5 (incremental builds)   ─── after Phase 1 (clean foundation)
Phase 6 (dev mode + reload)    ─── after Phase 5 (needs fast rebuilds)
Phase 7 (demo site)            ─── after Phases 2+3 (needs features to demo)
```

## New Dependencies

| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| `watchdog` | `>=3.0.0` | File system watching (Phase 6) | Apache-2.0 |

Everything else uses existing deps or CDN (KaTeX).

## Config Additions

```toml
[theme]
math = false          # Phase 2a

[nav]
reverse = false       # Phase 3
```

Incremental builds controlled via CLI flag (`--incremental`), not config.

## Verification

After each phase:
- `just test` — all tests pass
- `just check` — lint clean
- `just build` — full build succeeds
- `just build-docs` — docs build succeeds
- Manual: `just serve` and verify in browser

After Phase 6:
- `rockgarden dev` (or `serve --watch`) — edit a markdown file, confirm browser refreshes automatically
- Kill server, verify clean shutdown (no zombie watchers)

After Phase 7:
- Demo site deployed and accessible
- All features visible and working
