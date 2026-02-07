"""Callout processing for GFM alerts and Obsidian callouts."""

import re
from html import escape

CALLOUT_PATTERN = re.compile(
    r"^> \[!(\w+)\]([+-])?[ \t]*(.*?)\n((?:> .*\n?)*)", re.MULTILINE
)

CODE_BLOCK_PATTERN = re.compile(r"```[\s\S]*?```|`[^`\n]+`")

CALLOUT_ICONS = {
    "note": "ℹ️",
    "abstract": "📝",
    "summary": "📝",
    "tldr": "📝",
    "info": "ℹ️",
    "tip": "💡",
    "hint": "💡",
    "important": "🔥",
    "success": "✅",
    "check": "✅",
    "done": "✅",
    "question": "❓",
    "help": "❓",
    "faq": "❓",
    "warning": "⚠️",
    "caution": "⚠️",
    "attention": "⚠️",
    "failure": "❌",
    "fail": "❌",
    "missing": "❌",
    "danger": "🚨",
    "error": "🚨",
    "bug": "🐛",
    "example": "📋",
    "quote": "💭",
    "cite": "💭",
}


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
    code_blocks: list[str] = []

    def save_code_block(match: re.Match) -> str:
        code_blocks.append(match.group(0))
        return f"\x00CODE{len(code_blocks) - 1}\x00"

    content = CODE_BLOCK_PATTERN.sub(save_code_block, content)

    def replace_callout(match: re.Match) -> str:
        parsed = parse_callout(match)
        return callout_to_html(parsed)

    content = CALLOUT_PATTERN.sub(replace_callout, content)

    def restore_code_block(match: re.Match) -> str:
        idx = int(match.group(1))
        return code_blocks[idx]

    content = re.sub(r"\x00CODE(\d+)\x00", restore_code_block, content)

    return content


def parse_callout(match: re.Match) -> dict:
    """Parse callout match into components.

    Args:
        match: Regex match object from CALLOUT_PATTERN.

    Returns:
        Dict with type, fold, title, and content.
    """
    callout_type = match.group(1).lower()
    fold = match.group(2)
    custom_title = match.group(3).strip() if match.group(3) else ""
    content_lines = match.group(4)

    content = "\n".join(
        line[2:] if line.startswith("> ") else line for line in content_lines.split("\n")
    ).strip()

    title = custom_title if custom_title else callout_type.capitalize()

    return {
        "type": callout_type,
        "fold": fold,
        "title": title,
        "content": content,
    }


def callout_to_html(parsed: dict) -> str:
    """Convert parsed callout to HTML.

    Args:
        parsed: Dict from parse_callout with type, fold, title, and content.

    Returns:
        HTML string for the callout.
    """
    callout_type = parsed["type"]
    fold = parsed["fold"]
    title = parsed["title"]
    content = parsed["content"]

    icon = get_callout_icon(callout_type)
    css_class = f"callout callout-{callout_type}"

    title_html = f"""<div class="callout-title">
    <span class="callout-icon">{icon}</span>
    <span class="callout-title-text">{escape(title)}</span>
  </div>"""

    content_html = f'<div class="callout-content">\n{content}\n</div>'

    if fold:
        open_attr = ' open' if fold == '+' else ''
        return f"""<details class="{css_class}"{open_attr}>
  <summary class="callout-title">
    <span class="callout-icon">{icon}</span>
    <span class="callout-title-text">{escape(title)}</span>
  </summary>
  {content_html}
</details>"""
    else:
        return f"""<div class="{css_class}">
  {title_html}
  {content_html}
</div>"""


def get_callout_icon(callout_type: str) -> str:
    """Get icon for callout type.

    Args:
        callout_type: The callout type (e.g., 'note', 'warning').

    Returns:
        Emoji icon for the type, or default info icon.
    """
    return CALLOUT_ICONS.get(callout_type, "ℹ️")
