"""Image embed processing for Obsidian syntax."""

import re
from collections.abc import Callable
from dataclasses import dataclass
from html import escape

EMBED_PATTERN = re.compile(
    r"!\[\["
    r"([^\]|]+)"  # Target (required)
    r"(?:\|([^\]]+))?"  # Params: alt text or dimensions (optional, after |)
    r"\]\]"
)

CODE_BLOCK_PATTERN = re.compile(r"```[\s\S]*?```|`[^`\n]+`")

IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "svg", "webp", "bmp", "ico"}

DIMENSION_PATTERN = re.compile(r"^(\d+)(?:x(\d+))?$")


@dataclass
class ParsedEmbed:
    """Parsed embed data."""

    target: str
    alt_text: str | None
    width: int | None
    height: int | None

    @property
    def filename(self) -> str:
        """Get just the filename without path."""
        return self.target.rsplit("/", 1)[-1]


def parse_embed(target: str, params: str | None) -> ParsedEmbed:
    """Parse embed target and optional parameters.

    Args:
        target: The embed target path (e.g., "image.png" or "folder/image.png").
        params: Optional parameters after the pipe (alt text or dimensions).

    Returns:
        ParsedEmbed with target, alt_text, width, and height.
    """
    target = target.strip()
    alt_text = None
    width = None
    height = None

    if params:
        params = params.strip()
        dim_match = DIMENSION_PATTERN.match(params)
        if dim_match:
            width = int(dim_match.group(1))
            if dim_match.group(2):
                height = int(dim_match.group(2))
        else:
            alt_text = params

    return ParsedEmbed(target=target, alt_text=alt_text, width=width, height=height)


def is_image_embed(target: str) -> bool:
    """Check if embed target is an image based on extension."""
    ext = target.rsplit(".", 1)[-1].lower() if "." in target else ""
    return ext in IMAGE_EXTENSIONS


def embed_to_html(embed: ParsedEmbed, src: str) -> str:
    """Convert parsed embed to HTML img tag.

    Args:
        embed: Parsed embed data.
        src: The resolved source URL for the image.

    Returns:
        HTML img tag string.
    """
    attrs = [f'src="{escape(src)}"']

    alt = embed.alt_text if embed.alt_text else embed.filename
    attrs.append(f'alt="{escape(alt)}"')

    if embed.width:
        attrs.append(f'width="{embed.width}"')
    if embed.height:
        attrs.append(f'height="{embed.height}"')

    return f"<img {' '.join(attrs)}>"


def process_image_embeds(
    content: str,
    image_resolver: Callable[[str], str | None],
) -> tuple[str, set[str]]:
    """Convert image embeds to HTML img tags.

    Converts ![[image.png]] syntax to <img> tags.
    Embeds inside code blocks are preserved.
    Non-image embeds (e.g., note transclusions) are left unchanged.

    Args:
        content: Markdown content with image embeds.
        image_resolver: Function that takes an image path and returns
            a tuple of (src_url, actual_path) or None if not found.

    Returns:
        Tuple of (processed content, set of resolved image paths).
    """
    code_blocks: list[str] = []
    found_images: set[str] = set()

    def save_code_block(match: re.Match) -> str:
        code_blocks.append(match.group(0))
        return f"\x00CODE{len(code_blocks) - 1}\x00"

    content = CODE_BLOCK_PATTERN.sub(save_code_block, content)

    def replace_embed(match: re.Match) -> str:
        target = match.group(1)
        params = match.group(2)

        if not is_image_embed(target):
            return match.group(0)

        embed = parse_embed(target, params)
        resolved = image_resolver(embed.target)

        if resolved is None:
            return match.group(0)

        src_url, actual_path = resolved
        if actual_path:
            found_images.add(actual_path)

        return embed_to_html(embed, src_url)

    content = EMBED_PATTERN.sub(replace_embed, content)

    def restore_code_block(match: re.Match) -> str:
        idx = int(match.group(1))
        return code_blocks[idx]

    content = re.sub(r"\x00CODE(\d+)\x00", restore_code_block, content)

    return content, found_images
