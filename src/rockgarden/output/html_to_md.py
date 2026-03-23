"""HTML to markdown conversion utility."""

from __future__ import annotations

import re

from markdownify import markdownify

_HEADING_RE = re.compile(r"^(#{1,6})\s", re.MULTILINE)


def _bump_headings(md: str, offset: int) -> str:
    """Increase heading levels by *offset* (e.g. ## → #### when offset=2).

    Headings that would exceed H6 are clamped at H6.
    """
    if offset <= 0:
        return md

    def _replace(m: re.Match[str]) -> str:
        new_level = min(len(m.group(1)) + offset, 6)
        return "#" * new_level + " "

    return _HEADING_RE.sub(_replace, md)


def html_to_markdown(html: str, heading_offset: int = 0) -> str:
    """Convert HTML to markdown.

    Args:
        html: HTML string to convert.
        heading_offset: Increase heading levels by this amount.

    Returns:
        Markdown string with normalized whitespace.
    """
    if not html:
        return ""
    md = markdownify(html, heading_style="ATX", bullets="-").strip()
    if heading_offset:
        md = _bump_headings(md, heading_offset)
    return md
