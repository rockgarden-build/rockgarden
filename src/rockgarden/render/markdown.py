"""Markdown rendering with markdown-it-py."""

import re
from html import escape

from markdown_it import MarkdownIt

_md: MarkdownIt | None = None


def get_markdown_renderer() -> MarkdownIt:
    """Get or create the markdown renderer instance.

    Uses gfm-like preset which includes:
    - Tables
    - Strikethrough (~~text~~)
    - Autolinks (bare URLs)
    - Task lists (- [ ] item)
    """
    global _md
    if _md is None:
        _md = MarkdownIt("gfm-like", {"html": True, "breaks": True})
    return _md


def render_markdown(content: str) -> str:
    """Render markdown content to HTML.

    Args:
        content: Raw markdown string.

    Returns:
        Rendered HTML string.
    """
    md = get_markdown_renderer()
    html = md.render(content)

    # Post-process to handle broken links
    # Replace <a href="BROKEN::target">text</a> with <a class="internal-link broken" data-target="target">text</a>
    def replace_broken_link(match):
        from urllib.parse import unquote

        target = unquote(match.group(1))
        text = match.group(2)
        return (
            f'<a class="internal-link broken" data-target="{escape(target)}">{text}</a>'
        )

    html = re.sub(r'<a href="BROKEN::([^"]+)">(.*?)</a>', replace_broken_link, html)

    return html
