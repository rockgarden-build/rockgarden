# Plan: Generate `llms-full.txt`

## Context

Rockgarden generates `llms.txt` — a link index of all site pages. We want to also generate `llms-full.txt`, which concatenates the rendered content of all pages into a single file using the same grouping structure. This is useful for LLMs that want full site context without fetching each page individually.

The MCP export plan (`plans/rockgarden-mcp.md`) calls for similar HTML→markdown conversion using `markdownify`. This feature introduces that shared utility, which MCP export will reuse later.

For v1, we use `page.html` (content-only HTML, pre-template) rather than extracting from template-rendered HTML. A note will be added to the MCP plan to revisit `llms-full.txt` content source when the selector-based extraction lands.

## Files to Modify

1. **`pyproject.toml`** — add `markdownify` dependency
2. **`src/rockgarden/output/html_to_md.py`** (new) — shared HTML→markdown utility
3. **`src/rockgarden/output/llms_txt.py`** — refactor grouping logic into shared helper, add `build_llms_full_txt()`
4. **`src/rockgarden/config.py`** — add `full: bool = False` to `LlmsTxtConfig`
5. **`src/rockgarden/output/builder.py`** — wire up `llms-full.txt` generation
6. **`tests/test_html_to_md.py`** (new) — tests for HTML→markdown utility
7. **`tests/test_llms_txt.py`** — tests for `build_llms_full_txt()`
8. **`plans/rockgarden-mcp.md`** — add note about revisiting llms-full.txt content source

## Implementation

### 1. Add `markdownify` dependency

Add `"markdownify>=0.14.1"` to `pyproject.toml` dependencies. Run `uv sync`.

### 2. Create `src/rockgarden/output/html_to_md.py`

Thin wrapper around `markdownify.markdownify()`:

```python
def html_to_markdown(html: str) -> str:
```

- `heading_style="ATX"` (# headings)
- `bullets="-"`
- Strip/normalize whitespace
- Return empty string for empty/None input
- Keep images as `![alt](url)` — URLs are useful context even in plain text

### 3. Refactor grouping logic in `llms_txt.py`

Extract the shared grouping/ordering logic from `build_llms_txt()` into a helper:

```python
@dataclass
class _SectionItem:
    title: str
    url: str
    html: str | None  # content HTML (None for nav links)

@dataclass
class _Section:
    heading: str
    items: list[_SectionItem]

def _group_content(...) -> list[_Section]:
```

Both `build_llms_txt()` and `build_llms_full_txt()` call `_group_content()`, then format differently:
- `build_llms_txt()`: `- [Title](url)` list items
- `build_llms_full_txt()`: H2 title + source URL + converted markdown content + `---` separator

### 4. Add `build_llms_full_txt()`

Same signature as `build_llms_txt()`. Output format per page entry:

```
## Page Title

Source: https://example.com/page/

<converted markdown content>

---
```

- Nav links section: just links, no content to inline (same as `llms.txt`)
- FolderIndex items: use `custom_content` field; skip content block if None
- Page items: use `page.html`; skip content block if None

### 5. Config change

```python
class LlmsTxtConfig(BaseModel):
    enabled: bool = False
    description: str = ""
    full: bool = False
```

### 6. Wire up in builder

Inside the existing `if config.site.base_url and config.llms_txt.enabled:` block, after `llms.txt` generation:

```python
if config.llms_txt.full:
    llms_full_content = build_llms_full_txt(...)
    (output / "llms-full.txt").write_text(llms_full_content)
```

### 7. Tests

**`tests/test_html_to_md.py`:**
- Basic paragraph, headings, links, code blocks, empty input

**`tests/test_llms_txt.py` additions:**
- Title and description structure
- Page content is converted and included
- Source URL shown for each entry
- Section ordering matches `llms.txt`
- Pages with no HTML get title+URL only
- FolderIndex custom_content handled
- Nav links are link-only
- Separators between entries
- Trailing newline

### 8. Update MCP plan

Add note to `plans/rockgarden-mcp.md` open questions: revisit `llms-full.txt` content source when selector-based extraction is implemented — switch from `page.html` to extracted content for consistency with MCP export and support for transformative custom templates.

## Verification

1. `uv sync` succeeds with new dependency
2. `just ci` passes
3. Build the docs site with `llms_txt.full = true`, verify `llms-full.txt` output contains all page content with correct structure
4. Verify `llms.txt` is unchanged (refactor doesn't alter output)
