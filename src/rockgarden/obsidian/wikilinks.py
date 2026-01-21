"""Wiki-link processing for Obsidian syntax."""

import re
from collections.abc import Callable
from urllib.parse import quote

WIKILINK_PATTERN = re.compile(
    r"\[\["
    r"([^\]|]+)"  # Target (required)
    r"(?:\|([^\]]+))?"  # Display text (optional, after |)
    r"\]\]"
)

CODE_BLOCK_PATTERN = re.compile(r"```[\s\S]*?```|`[^`\n]+`")


def process_wikilinks(
    content: str,
    resolver: Callable[[str], str | None],
) -> str:
    """Convert wiki-links to standard markdown links.

    Converts [[Target]] and [[Target|Display Text]] to [text](url).
    Unresolved links are rendered as plain text.
    Wiki-links inside code blocks are preserved.

    Args:
        content: Markdown content with wiki-links.
        resolver: Function that takes a link target and returns a URL or None.

    Returns:
        Content with wiki-links converted to standard markdown links.
    """
    code_blocks: list[str] = []

    def save_code_block(match: re.Match) -> str:
        code_blocks.append(match.group(0))
        return f"\x00CODE{len(code_blocks) - 1}\x00"

    content = CODE_BLOCK_PATTERN.sub(save_code_block, content)

    def replace_wikilink(match: re.Match) -> str:
        target = match.group(1).strip()
        display = match.group(2)

        if display:
            display = display.strip()
        else:
            display = target

        url = resolver(target)
        if url:
            encoded_url = quote(url, safe="/:?#[]@!$&'()*+,;=")
            return f"[{display}]({encoded_url})"
        else:
            return display

    content = WIKILINK_PATTERN.sub(replace_wikilink, content)

    def restore_code_block(match: re.Match) -> str:
        idx = int(match.group(1))
        return code_blocks[idx]

    content = re.sub(r"\x00CODE(\d+)\x00", restore_code_block, content)

    return content
