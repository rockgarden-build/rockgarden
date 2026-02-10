"""Callout processing for GFM alerts and Obsidian callouts.

Operates on rendered HTML output. Finds <blockquote> elements whose first <p>
contains [!type] syntax and re-wraps them as styled callout elements.
"""

import re

CALLOUT_MARKER_RE = re.compile(r"\[!(\w+)\]([+-])?\s*(.*)")

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


def process_callouts(html: str) -> str:
    """Convert rendered blockquotes with callout markers to styled callout HTML.

    Finds <blockquote> elements whose first <p> starts with [!type] and
    re-wraps them as callout <div> or <details> elements. Inner HTML is
    already rendered by markdown-it-py, so formatting is preserved.

    Args:
        html: Rendered HTML string.

    Returns:
        HTML with callout blockquotes converted to styled callout elements.
    """
    result: list[str] = []
    pos = 0
    open_tag = "<blockquote>"
    close_tag = "</blockquote>"

    while pos < len(html):
        start = html.find(open_tag, pos)
        if start < 0:
            result.append(html[pos:])
            break

        result.append(html[pos:start])

        # Find matching </blockquote> accounting for nesting
        depth = 0
        i = start
        end = len(html)
        while i < len(html):
            if html[i : i + len(open_tag)] == open_tag:
                depth += 1
                i += len(open_tag)
            elif html[i : i + len(close_tag)] == close_tag:
                depth -= 1
                if depth == 0:
                    end = i + len(close_tag)
                    break
                i += len(close_tag)
            else:
                i += 1

        block_html = html[start:end]
        result.append(_try_convert_callout(block_html))
        pos = end

    return "".join(result)


def _try_convert_callout(block_html: str) -> str:
    """Convert a <blockquote> to a callout if it contains a [!type] marker.

    Returns the original HTML unchanged if it's a regular blockquote.
    """
    # Extract inner HTML: strip <blockquote>\n ... \n</blockquote>
    inner = block_html
    if inner.startswith("<blockquote>\n"):
        inner = inner[len("<blockquote>\n") :]
    elif inner.startswith("<blockquote>"):
        inner = inner[len("<blockquote>") :]
    if inner.endswith("</blockquote>\n"):
        inner = inner[: -len("</blockquote>\n")]
    elif inner.endswith("</blockquote>"):
        inner = inner[: -len("</blockquote>")]
    inner = inner.strip()

    if not inner.startswith("<p>[!"):
        return block_html

    # Find end of first <p>
    first_p_end = inner.find("</p>")
    if first_p_end < 0:
        return block_html

    first_p_content = inner[3:first_p_end]  # strip leading <p>
    after_first_p = inner[first_p_end + 4 :].strip()

    # Split first <p> on first <br /> to separate marker line from content
    br_match = re.search(r"<br\s*/?>", first_p_content)
    if br_match:
        marker_line = first_p_content[: br_match.start()]
        rest_of_p = first_p_content[br_match.end() :].lstrip("\n")
    else:
        marker_line = first_p_content
        rest_of_p = ""

    # Parse [!type][+-]? title from marker line
    type_match = CALLOUT_MARKER_RE.match(marker_line)
    if not type_match:
        return block_html

    callout_type = type_match.group(1).lower()
    fold = type_match.group(2)
    title = type_match.group(3).strip() or callout_type.capitalize()

    # Build content from rest of first <p> + subsequent elements
    content_parts: list[str] = []
    if rest_of_p:
        content_parts.append(f"<p>{rest_of_p}</p>")
    if after_first_p:
        content_parts.append(after_first_p)
    content_html = "\n".join(content_parts)

    return _build_callout_html(callout_type, fold, title, content_html)


def _build_callout_html(
    callout_type: str, fold: str | None, title: str, content_html: str
) -> str:
    """Build the final callout HTML structure."""
    icon = get_callout_icon(callout_type)
    css_class = f"callout callout-{callout_type}"

    content_div = (
        f'<div class="callout-content">\n{content_html}\n</div>' if content_html else ""
    )

    if fold:
        open_attr = " open" if fold == "+" else ""
        return f"""<details class="{css_class}"{open_attr}>
  <summary class="callout-title">
    <span class="callout-icon">{icon}</span>
    <span class="callout-title-text">{title}</span>
  </summary>
  {content_div}
</details>"""
    else:
        return f"""<div class="{css_class}">
  <div class="callout-title">
    <span class="callout-icon">{icon}</span>
    <span class="callout-title-text">{title}</span>
  </div>
  {content_div}
</div>"""


def get_callout_icon(callout_type: str) -> str:
    """Get icon for callout type.

    Args:
        callout_type: The callout type (e.g., 'note', 'warning').

    Returns:
        Emoji icon for the type, or default info icon.
    """
    return CALLOUT_ICONS.get(callout_type, "ℹ️")
