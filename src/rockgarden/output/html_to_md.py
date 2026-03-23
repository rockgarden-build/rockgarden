"""HTML to markdown conversion utility."""

from __future__ import annotations

from markdownify import markdownify


def html_to_markdown(html: str) -> str:
    """Convert HTML to markdown.

    Args:
        html: HTML string to convert.

    Returns:
        Markdown string with normalized whitespace.
    """
    if not html:
        return ""
    return markdownify(html, heading_style="ATX", bullets="-").strip()
