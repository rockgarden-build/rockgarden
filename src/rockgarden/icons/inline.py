"""Inline icon syntax processing for markdown content.

Replaces :library-icon-name: patterns with inline SVG before markdown
rendering. Only resolved icons are replaced; unrecognized patterns are
left as literal text.
"""

import re

from rockgarden.icons.resolver import resolve_icon

CODE_BLOCK_PATTERN = re.compile(r"```[\s\S]*?```|~~~[\s\S]*?~~~|`[^`\n]+`")

INLINE_ICON_PATTERN = re.compile(
    r"(?<![:\w])"
    r":([a-z][a-z0-9]*)"
    r"-"
    r"([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"
    r":(?![:\w])"
)


def process_inline_icons(content: str) -> str:
    """Replace :library-icon-name: with inline SVG.

    Code blocks (fenced and inline) are preserved. Unresolved icons are
    left as literal text.

    Args:
        content: Markdown content.

    Returns:
        Content with resolved icon references replaced by SVG markup.
    """
    code_blocks: list[str] = []

    def save_code_block(match: re.Match) -> str:
        code_blocks.append(match.group(0))
        return f"\x00CODE{len(code_blocks) - 1}\x00"

    content = CODE_BLOCK_PATTERN.sub(save_code_block, content)

    def replace_icon(match: re.Match) -> str:
        library = match.group(1)
        name = match.group(2)
        svg = resolve_icon(f"{library}:{name}")
        if svg is None:
            return match.group(0)
        return svg

    content = INLINE_ICON_PATTERN.sub(replace_icon, content)

    def restore_code_block(match: re.Match) -> str:
        idx = int(match.group(1))
        return code_blocks[idx]

    content = re.sub(r"\x00CODE(\d+)\x00", restore_code_block, content)

    return content
