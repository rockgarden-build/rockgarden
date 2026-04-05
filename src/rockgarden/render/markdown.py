"""Markdown rendering with markdown-it-py."""

import re
from html import escape

from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.tasklists import tasklists_plugin
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

_md: MarkdownIt | None = None
_highlight_formatter = HtmlFormatter(nowrap=False, cssclass="highlight")


def _fence_renderer(self, tokens, idx, options, env):
    """Render fenced code blocks with Pygments syntax highlighting."""
    token = tokens[idx]
    info = token.info.strip() if token.info else ""
    lang = info.split()[0] if info else ""
    code = token.content

    if lang == "math":
        return f'<div class="math block">\n{escape(code)}</div>\n'

    if lang:
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
            return highlight(code, lexer, _highlight_formatter)
        except ClassNotFound:
            pass

    escaped = escape(code)
    lang_attr = f' class="language-{escape(lang)}"' if lang else ""
    return f"<pre><code{lang_attr}>{escaped}</code></pre>\n"


def get_markdown_renderer() -> MarkdownIt:
    """Get or create the markdown renderer instance.

    Uses gfm-like preset which includes:
    - Tables
    - Strikethrough (~~text~~)
    - Autolinks (bare URLs)

    Additional plugins:
    - Task lists (- [ ] item) via mdit-py-plugins
    - Footnotes ([^1] references and [^1]: definitions) via mdit-py-plugins
    - Dollar math ($..$ inline, $$...$$ block) via mdit-py-plugins
    - Syntax highlighting via Pygments
    """
    global _md
    if _md is None:
        _md = MarkdownIt("gfm-like", {"html": True, "breaks": True})
        footnote_plugin(_md)
        tasklists_plugin(_md)
        dollarmath_plugin(_md, allow_digits=False, allow_space=False)
        _md.add_render_rule("fence", _fence_renderer)
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
    # Replace <a href="BROKEN::target">text</a>
    # with <a class="internal-link broken" data-target="target">text</a>
    def replace_broken_link(match):
        from urllib.parse import unquote

        target = unquote(match.group(1))
        text = match.group(2)
        return (
            f'<a class="internal-link broken" data-target="{escape(target)}">{text}</a>'
        )

    html = re.sub(r'<a href="BROKEN::([^"]+)">(.*?)</a>', replace_broken_link, html)

    return html
