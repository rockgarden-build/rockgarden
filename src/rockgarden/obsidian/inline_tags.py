"""Inline tag extraction and rendering.

Extracts Obsidian-style inline tags (#tag, #parent/child) from markdown
content. Tags are collected for the page's tag list and rendered as
clickable links. Code blocks are protected from processing.
"""

import re

from rockgarden.obsidian.embeds import CODE_BLOCK_PATTERN
from rockgarden.urls import get_tag_url, normalize_tag

INLINE_TAG_PATTERN = re.compile(r"(?<!\w)#([a-zA-Z][\w-]*(?:/[\w-]+)*)")
PLACEHOLDER_PATTERN = re.compile(r"\x00CODE(\d+)\x00")


def extract_inline_tags(
    content: str,
    clean_urls: bool = True,
    base_path: str = "",
    ascii_urls: bool = False,
) -> tuple[str, list[str]]:
    """Extract inline tags from content and render them as links.

    Returns:
        Tuple of (modified_content, list_of_raw_tag_strings).
        The modified content has inline tags replaced with markdown links.
    """
    code_blocks: list[str] = []

    def save_code_block(match: re.Match) -> str:
        code_blocks.append(match.group(0))
        return f"\x00CODE{len(code_blocks) - 1}\x00"

    content = CODE_BLOCK_PATTERN.sub(save_code_block, content)

    tags: list[str] = []

    def replace_tag(match: re.Match) -> str:
        raw_tag = match.group(1)
        tags.append(raw_tag)
        slug = normalize_tag(raw_tag, ascii_urls)
        url = get_tag_url(slug, clean_urls, base_path)
        return f"[#{raw_tag}]({url})"

    content = INLINE_TAG_PATTERN.sub(replace_tag, content)

    def restore_code_block(match: re.Match) -> str:
        idx = int(match.group(1))
        return code_blocks[idx]

    content = PLACEHOLDER_PATTERN.sub(restore_code_block, content)
    return content, tags


def expand_hierarchical_tags(tags: list[str]) -> list[str]:
    """Expand nested tags into all ancestor segments.

    ["project/active", "python"] → ["project/active", "project", "python"]
    ["a/b/c"] → ["a/b/c", "a/b", "a"]
    """
    expanded: set[str] = set()
    for tag in tags:
        expanded.add(tag)
        parts = tag.split("/")
        for i in range(1, len(parts)):
            expanded.add("/".join(parts[:i]))
    return sorted(expanded)
