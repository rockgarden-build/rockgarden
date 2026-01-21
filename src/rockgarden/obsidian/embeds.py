"""Media embed processing for Obsidian syntax."""

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
AUDIO_EXTENSIONS = {"mp3", "wav", "m4a", "ogg", "3gp", "flac"}
VIDEO_EXTENSIONS = {"mp4", "webm", "ogv", "mov", "mkv"}
PDF_EXTENSIONS = {"pdf"}

MEDIA_EXTENSIONS = IMAGE_EXTENSIONS | AUDIO_EXTENSIONS | VIDEO_EXTENSIONS | PDF_EXTENSIONS

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


def get_extension(target: str) -> str:
    """Get lowercase file extension from target."""
    return target.rsplit(".", 1)[-1].lower() if "." in target else ""


def is_image_embed(target: str) -> bool:
    """Check if embed target is an image based on extension."""
    return get_extension(target) in IMAGE_EXTENSIONS


def is_audio_embed(target: str) -> bool:
    """Check if embed target is audio based on extension."""
    return get_extension(target) in AUDIO_EXTENSIONS


def is_video_embed(target: str) -> bool:
    """Check if embed target is video based on extension."""
    return get_extension(target) in VIDEO_EXTENSIONS


def is_pdf_embed(target: str) -> bool:
    """Check if embed target is a PDF based on extension."""
    return get_extension(target) in PDF_EXTENSIONS


def is_media_embed(target: str) -> bool:
    """Check if embed target is any supported media type."""
    return get_extension(target) in MEDIA_EXTENSIONS


def image_to_html(embed: ParsedEmbed, src: str) -> str:
    """Convert parsed embed to HTML img tag."""
    attrs = [f'src="{escape(src)}"']

    alt = embed.alt_text if embed.alt_text else embed.filename
    attrs.append(f'alt="{escape(alt)}"')

    if embed.width:
        attrs.append(f'width="{embed.width}"')
    if embed.height:
        attrs.append(f'height="{embed.height}"')

    return f"<img {' '.join(attrs)}>"


def audio_to_html(embed: ParsedEmbed, src: str) -> str:
    """Convert parsed embed to HTML audio tag."""
    return f'<audio controls src="{escape(src)}"></audio>'


def video_to_html(embed: ParsedEmbed, src: str) -> str:
    """Convert parsed embed to HTML video tag."""
    attrs = [f'src="{escape(src)}"', "controls"]

    if embed.width:
        attrs.append(f'width="{embed.width}"')
    if embed.height:
        attrs.append(f'height="{embed.height}"')

    return f"<video {' '.join(attrs)}></video>"


def pdf_to_html(embed: ParsedEmbed, src: str) -> str:
    """Convert parsed embed to HTML iframe for PDF."""
    width = embed.width or 100
    height = embed.height or 600
    width_unit = "%" if not embed.width else "px"
    return f'<iframe src="{escape(src)}" width="{width}{width_unit}" height="{height}px" style="border: none;"></iframe>'


def embed_to_html(embed: ParsedEmbed, src: str) -> str:
    """Convert parsed embed to appropriate HTML element."""
    target = embed.target

    if is_image_embed(target):
        return image_to_html(embed, src)
    elif is_audio_embed(target):
        return audio_to_html(embed, src)
    elif is_video_embed(target):
        return video_to_html(embed, src)
    elif is_pdf_embed(target):
        return pdf_to_html(embed, src)
    else:
        return image_to_html(embed, src)


def process_media_embeds(
    content: str,
    media_resolver: Callable[[str], str | None],
) -> tuple[str, set[str]]:
    """Convert media embeds to HTML elements.

    Converts ![[file]] syntax to appropriate HTML tags:
    - Images -> <img>
    - Audio -> <audio>
    - Video -> <video>
    - PDF -> <iframe>

    Embeds inside code blocks are preserved.
    Non-media embeds (e.g., note transclusions) are left unchanged.

    Args:
        content: Markdown content with media embeds.
        media_resolver: Function that takes a media path and returns
            a tuple of (src_url, actual_path) or None if not found.

    Returns:
        Tuple of (processed content, set of resolved media paths).
    """
    code_blocks: list[str] = []
    found_media: set[str] = set()

    def save_code_block(match: re.Match) -> str:
        code_blocks.append(match.group(0))
        return f"\x00CODE{len(code_blocks) - 1}\x00"

    content = CODE_BLOCK_PATTERN.sub(save_code_block, content)

    def replace_embed(match: re.Match) -> str:
        target = match.group(1)
        params = match.group(2)

        if not is_media_embed(target):
            return match.group(0)

        embed = parse_embed(target, params)
        resolved = media_resolver(embed.target)

        if resolved is None:
            return match.group(0)

        src_url, actual_path = resolved
        if actual_path:
            found_media.add(actual_path)

        return embed_to_html(embed, src_url)

    content = EMBED_PATTERN.sub(replace_embed, content)

    def restore_code_block(match: re.Match) -> str:
        idx = int(match.group(1))
        return code_blocks[idx]

    content = re.sub(r"\x00CODE(\d+)\x00", restore_code_block, content)

    return content, found_media
