# Feature 05: Callouts

Convert Obsidian callout syntax and GitHub Flavored Markdown (GFM) alerts to styled HTML blocks.

## Status: Ready to Implement

## Syntax Support

### GFM Alerts (GitHub)
```markdown
> [!NOTE]
> Content here

> [!WARNING]
> Critical content
```

- Uppercase type names (NOTE, TIP, IMPORTANT, WARNING, CAUTION)
- No custom titles
- Not collapsible
- Fixed styling

### Obsidian Callouts
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

- Case-insensitive type names (note, warning, tip, etc.)
- Custom titles (text after `[!type]`)
- Collapsible: `+` (open) or `-` (closed) suffix
- Custom icons and colors per type

## Compatibility Strategy

Support **both** GFM and Obsidian syntax:
- Accept type names in any case (NOTE/note/NoTe)
- Map both to same CSS classes: `callout-note`, `callout-warning`, etc.
- GFM alerts render as non-collapsible, Obsidian can be collapsible
- Custom titles work for both (Obsidian feature, ignored by GFM spec but we support it)

## Callout Types

Standard types (shared between GFM and Obsidian):
- `note`, `abstract`, `summary`, `tldr` → Blue
- `info` → Cyan
- `tip`, `hint`, `important` → Green
- `success`, `check`, `done` → Green
- `question`, `help`, `faq` → Purple
- `warning`, `caution`, `attention` → Orange
- `failure`, `fail`, `missing` → Red
- `danger`, `error` → Red
- `bug` → Red
- `example` → Purple
- `quote`, `cite` → Gray

GFM standard types:
- `NOTE` (maps to `note`)
- `TIP` (maps to `tip`)
- `IMPORTANT` (maps to `important`)
- `WARNING` (maps to `warning`)
- `CAUTION` (maps to `caution`)

## Implementation Approach

### Pattern: Regex Preprocessing

Follow the same pattern as `wikilinks.py` and `embeds.py`:
1. Use regex to find callout syntax in markdown
2. Save and replace code blocks (don't process callouts in code)
3. Parse callout type, title, fold state
4. Replace with HTML output
5. Restore code blocks
6. Pass processed content to markdown-it-py

### Why Not a markdown-it-py Plugin?

- No existing mdit-py-plugins for GFM alerts or Obsidian callouts
- Regex preprocessing is simpler and consistent with existing code
- Full control over HTML output
- Can support both GFM and Obsidian features in one pass

### Regex Pattern

```python
CALLOUT_PATTERN = re.compile(
    r'^(> \[!(\w+)\]([+-])?\s*(.*?))\n((?:> .*\n?)*)',
    re.MULTILINE
)
```

Captures:
- Group 1: First line (> [!type]± title)
- Group 2: Type name (case-insensitive)
- Group 3: Fold state (+ or -, optional)
- Group 4: Custom title (optional, rest of first line)
- Group 5: Content lines (subsequent > lines)

## Output HTML

### Static Callout (GFM / Obsidian without +/-)

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

### Collapsible Callout (Obsidian with +/-)

```html
<details class="callout callout-tip" open>
  <summary class="callout-title">
    <span class="callout-icon">💡</span>
    <span class="callout-title-text">Tip</span>
  </summary>
  <div class="callout-content">
    <p>Content here.</p>
  </div>
</details>
```

Note: `open` attribute present if `+`, absent if `-`

## Implementation Plan

### 1. Create `src/rockgarden/obsidian/callouts.py`

```python
"""Callout processing for GFM alerts and Obsidian callouts."""

import re
from html import escape

CALLOUT_PATTERN = re.compile(...)
CODE_BLOCK_PATTERN = re.compile(r"```[\s\S]*?```|`[^`\n]+`")

def process_callouts(content: str) -> str:
    """Convert GFM alerts and Obsidian callouts to HTML.

    Supports:
    - GFM: > [!NOTE] (uppercase, no custom title)
    - Obsidian: > [!note] Custom Title (case-insensitive)
    - Collapsible: > [!note]+ (open) or > [!note]- (closed)

    Args:
        content: Markdown content with callouts.

    Returns:
        Content with callouts converted to HTML.
    """
    # 1. Save code blocks
    # 2. Find and replace callouts
    # 3. Restore code blocks
    pass

def parse_callout(match: re.Match) -> dict:
    """Parse callout match into components."""
    pass

def callout_to_html(parsed: dict) -> str:
    """Convert parsed callout to HTML."""
    pass

def get_callout_icon(callout_type: str) -> str:
    """Get icon for callout type."""
    pass
```

Follow the structure of `wikilinks.py` and `embeds.py`:
- Save code blocks before processing
- Use regex substitution for callout replacement
- Restore code blocks after processing

### 2. Integrate into Build Pipeline

Modify where markdown processing happens (likely in `output/builder.py` or `render/markdown.py`):

```python
from rockgarden.obsidian.callouts import process_callouts

# Before rendering markdown:
content = process_callouts(content)
content = process_wikilinks(content, resolver)
content, media = process_media_embeds(content, media_resolver)
html = render_markdown(content)
```

### 3. Add CSS Styling

Add callout styles to templates (likely `templates/base.html` or a dedicated CSS file):
- Use Tailwind/DaisyUI classes for colors
- Define `.callout`, `.callout-{type}` classes
- Style `.callout-title`, `.callout-content`
- Icons can be emoji or SVG

### 4. Testing

Create test cases for:
- GFM alerts (uppercase, no title)
- Obsidian callouts (lowercase, with/without title)
- Collapsible callouts (+ and -)
- Callouts in code blocks (should not be processed)
- Multiple callouts in one document
- Nested markdown in callout content

## Key Files to Create/Modify

- **New:** `src/rockgarden/obsidian/callouts.py` - Callout parsing module
- **Modify:** `src/rockgarden/output/builder.py` or `render/markdown.py` - Integrate callout processing
- **Modify:** `src/rockgarden/templates/base.html` - Add callout CSS styles
- **New:** `tests/test_callouts.py` - Test suite for callouts

## Reference Implementations

- **JavaScript:** [ebullient/markdown-it-obsidian-callouts](https://github.com/ebullient/markdown-it-obsidian-callouts)
- **Python-Markdown:** [GooRoo/obsidian-callouts](https://github.com/GooRoo/obsidian-callouts) (different markdown library, but good reference for syntax)
- **Existing code:** `src/rockgarden/obsidian/wikilinks.py` and `embeds.py` for regex preprocessing pattern

## Design Decisions

1. **Regex preprocessing over markdown-it-py plugin**: Simpler, consistent with existing codebase, full control over output
2. **Support both GFM and Obsidian**: Make rockgarden work with standard markdown and Obsidian vaults
3. **Case-insensitive type names**: Accept NOTE/note/Note all as valid
4. **Collapsible via `<details>`**: Native HTML element, no JavaScript required
5. **Icons as emoji or SVG**: Start with emoji (simple), can enhance with SVG later
