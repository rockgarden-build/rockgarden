"""Markdown link processing."""

import re

LINK_PATTERN = re.compile(
    r"\[([^\]]+)\]"  # Link text in brackets
    r"\(([^)]+)\)"  # URL in parentheses
)

CODE_BLOCK_PATTERN = re.compile(r"```[\s\S]*?```|`[^`\n]+`")


def transform_md_links(content: str, clean_urls: bool = True) -> str:
    """Transform .md links in markdown content.

    With clean_urls=True (directory-based URLs):
    - [text](./page.md) → [text](./page/)
    - [text](../folder/page.md) → [text](../folder/page/)
    - [text](/folder/page.md) → [text](/folder/page/)
    - [text](page.md#heading) → [text](page/#heading)

    With clean_urls=False:
    - [text](./page.md) → [text](./page.html)
    - [text](page.md#heading) → [text](page.html#heading)

    External URLs and non-.md links are preserved.
    Links inside code blocks are not transformed.

    Args:
        content: Markdown content with links.
        clean_urls: If True, use trailing slash format; if False, use .html.

    Returns:
        Content with .md links converted.
    """
    code_blocks: list[str] = []

    def save_code_block(match: re.Match) -> str:
        code_blocks.append(match.group(0))
        return f"\x00CODE{len(code_blocks) - 1}\x00"

    content = CODE_BLOCK_PATTERN.sub(save_code_block, content)

    def replace_link(match: re.Match) -> str:
        text = match.group(1)
        url = match.group(2)

        if url.startswith(("http://", "https://", "mailto:", "//")):
            return match.group(0)

        if ".md" in url:
            if clean_urls:
                url = re.sub(r"\.md([#?]|$)", r"/\1", url)
            else:
                url = re.sub(r"\.md([#?]|$)", r".html\1", url)

        return f"[{text}]({url})"

    content = LINK_PATTERN.sub(replace_link, content)

    def restore_code_block(match: re.Match) -> str:
        idx = int(match.group(1))
        return code_blocks[idx]

    content = re.sub(r"\x00CODE(\d+)\x00", restore_code_block, content)

    return content
