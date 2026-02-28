"""Note transclusion processing for Obsidian syntax."""

import re
from collections.abc import Callable

from rockgarden.obsidian.embeds import CODE_BLOCK_PATTERN, is_media_embed

TRANSCLUSION_PATTERN = re.compile(
    r"!\[\["
    r"([^\]|#]+)"  # Target (required, no | or # in target)
    r"(?:#[^\]|]*)?"  # Optional heading ref (ignored for lookup)
    r"(?:\|[^\]]*)?"  # Optional display params (ignored)
    r"\]\]"
)


def process_note_transclusions(
    content: str,
    resolver: Callable[[str], str | None],
) -> str:
    """Replace note transclusion embeds with rendered HTML.

    Handles ![[note]] and ![[note.md]] syntax where the target resolves to a
    markdown note (not a media file). Media embeds are left unchanged.

    Embeds inside code blocks are preserved. Unresolved targets are left
    unchanged.

    Args:
        content: Markdown content with possible note transclusions.
        resolver: Function that takes a note name and returns rendered HTML,
            or None if not found or a cycle is detected.

    Returns:
        Processed content with transclusions replaced by HTML divs.
    """
    code_blocks: list[str] = []

    def save_code_block(match: re.Match) -> str:
        code_blocks.append(match.group(0))
        return f"\x00CODE{len(code_blocks) - 1}\x00"

    content = CODE_BLOCK_PATTERN.sub(save_code_block, content)

    def replace_transclusion(match: re.Match) -> str:
        target = match.group(1).strip()

        if is_media_embed(target):
            return match.group(0)

        html = resolver(target)
        if html is None:
            return match.group(0)

        return f'<div class="transclusion">{html}</div>'

    content = TRANSCLUSION_PATTERN.sub(replace_transclusion, content)

    def restore_code_block(match: re.Match) -> str:
        idx = int(match.group(1))
        return code_blocks[idx]

    content = re.sub(r"\x00CODE(\d+)\x00", restore_code_block, content)

    return content
