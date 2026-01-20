"""Markdown rendering with markdown-it-py."""

from markdown_it import MarkdownIt

_md: MarkdownIt | None = None


def get_markdown_renderer() -> MarkdownIt:
    """Get or create the markdown renderer instance."""
    global _md
    if _md is None:
        _md = MarkdownIt("commonmark", {"html": True})
    return _md


def render_markdown(content: str) -> str:
    """Render markdown content to HTML.

    Args:
        content: Raw markdown string.

    Returns:
        Rendered HTML string.
    """
    md = get_markdown_renderer()
    return md.render(content)
