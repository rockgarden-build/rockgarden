"""Highlight syntax (==text==) for markdown-it-py.

Ported from the JS markdown-it-mark plugin. Registers an inline rule that
converts ==text== into <mark>text</mark>. Uses the delimiter runner pattern
(same as emphasis/strikethrough).
"""

from markdown_it import MarkdownIt
from markdown_it.rules_inline import StateInline
from markdown_it.rules_inline.state_inline import Delimiter


def highlight_plugin(md: MarkdownIt) -> None:
    md.inline.ruler.before("emphasis", "mark", _mark_tokenize)
    md.inline.ruler2.before("emphasis", "mark", _mark_post_process)
    md.add_render_rule("mark_open", _mark_open)
    md.add_render_rule("mark_close", _mark_close)


def _mark_open(self, tokens, idx, options, env):
    return "<mark>"


def _mark_close(self, tokens, idx, options, env):
    return "</mark>"


def _mark_tokenize(state: StateInline, silent: bool) -> bool:
    pos = state.pos
    src = state.src

    if src[pos] != "=":
        return False

    if silent:
        return False

    scanned = state.scanDelims(pos, True)
    length = scanned.length

    if length < 2:
        return False

    if length % 2:
        token = state.push("text", "", 0)
        token.content = "="
        length -= 1

    i = 0
    while i < length:
        token = state.push("text", "", 0)
        token.content = "=="

        state.delimiters.append(
            Delimiter(
                marker=ord("="),
                length=0,
                token=len(state.tokens) - 1,
                end=-1,
                open=scanned.can_open,
                close=scanned.can_close,
            )
        )

        i += 2

    state.pos += scanned.length
    return True


def _mark_post_process(state: StateInline, *args) -> None:
    delimiters = state.delimiters
    lone_markers = []
    maximum = len(delimiters)

    i = maximum - 1
    while i >= 0:
        start_delim = delimiters[i]

        if start_delim.marker != ord("="):
            i -= 1
            continue

        if start_delim.end == -1:
            i -= 1
            continue

        end_delim = delimiters[start_delim.end]

        token = state.tokens[start_delim.token]
        token.type = "mark_open"
        token.tag = "mark"
        token.nesting = 1
        token.markup = "=="
        token.content = ""

        token = state.tokens[end_delim.token]
        token.type = "mark_close"
        token.tag = "mark"
        token.nesting = -1
        token.markup = "=="
        token.content = ""

        inner = state.tokens[end_delim.token - 1]
        if inner.type == "text" and inner.content == "=":
            lone_markers.append(end_delim.token - 1)

        i -= 1

    for idx in sorted(lone_markers, reverse=True):
        del state.tokens[idx]
