"""Obsidian comment stripping (%% comment %%).

Strips Obsidian-style comments from markdown content before rendering.
Supports both inline and multi-line block comments. Comments inside
code blocks are preserved.
"""

import re

from rockgarden.obsidian.embeds import CODE_BLOCK_PATTERN

COMMENT_PATTERN = re.compile(r"%%[\s\S]*?%%")
PLACEHOLDER_PATTERN = re.compile(r"\x00CODE(\d+)\x00")


def strip_comments(content: str) -> str:
    """Remove Obsidian %% comments %% from content.

    Code blocks are protected — comments inside fenced or inline code
    are left intact.
    """
    code_blocks: list[str] = []

    def save_code_block(match: re.Match) -> str:
        code_blocks.append(match.group(0))
        return f"\x00CODE{len(code_blocks) - 1}\x00"

    content = CODE_BLOCK_PATTERN.sub(save_code_block, content)
    content = COMMENT_PATTERN.sub("", content)

    def restore_code_block(match: re.Match) -> str:
        idx = int(match.group(1))
        return code_blocks[idx]

    content = PLACEHOLDER_PATTERN.sub(restore_code_block, content)
    return content
