"""Asset collection and copying for static site generation."""

import re
import shutil
from collections import defaultdict
from pathlib import Path

from rockgarden.obsidian.embeds import (
    CODE_BLOCK_PATTERN,
    IMAGE_EXTENSIONS,
    MEDIA_EXTENSIONS,
)


def build_media_index(source_dir: Path) -> dict[str, list[str]]:
    """Build an index of media files by filename for vault-wide resolution.

    Args:
        source_dir: The root source directory.

    Returns:
        Dict mapping lowercase filename to list of paths relative to source_dir.
    """
    index: dict[str, list[str]] = defaultdict(list)
    for ext in MEDIA_EXTENSIONS:
        for path in source_dir.rglob(f"*.{ext}"):
            rel_path = str(path.relative_to(source_dir))
            index[path.name.lower()].append(rel_path)
        for path in source_dir.rglob(f"*.{ext.upper()}"):
            rel_path = str(path.relative_to(source_dir))
            index[path.name.lower()].append(rel_path)
    return dict(index)

MD_IMAGE_PATTERN = re.compile(
    r"!\[([^\]]*)\]"  # Alt text (can be empty)
    r"\(([^)\s]+)"  # URL/path (required, no spaces)
    r"(?:\s+[\"'][^\"']*[\"'])?\)"  # Optional title in quotes
)


def is_external_url(path: str) -> bool:
    """Check if a path is an external URL."""
    return path.startswith(("http://", "https://", "//", "data:"))


def collect_markdown_images(
    content: str,
    image_resolver: callable,
) -> set[str]:
    """Collect image paths from standard markdown image syntax.

    Finds ![alt](path) images and resolves their paths.
    Skips external URLs and images inside code blocks.

    Args:
        content: Markdown content.
        image_resolver: Function to resolve image paths.

    Returns:
        Set of resolved image paths relative to source.
    """
    code_blocks: list[str] = []

    def save_code_block(match: re.Match) -> str:
        code_blocks.append(match.group(0))
        return f"\x00CODE{len(code_blocks) - 1}\x00"

    content = CODE_BLOCK_PATTERN.sub(save_code_block, content)

    found_images: set[str] = set()

    for match in MD_IMAGE_PATTERN.finditer(content):
        path = match.group(2)

        if is_external_url(path):
            continue

        resolved = image_resolver(path)
        if resolved:
            _, actual_path = resolved
            if actual_path:
                found_images.add(actual_path)

    return found_images


def create_media_resolver(
    source_dir: Path, page_path: str, media_index: dict[str, list[str]] | None = None
):
    """Create a media resolver function for a specific page.

    The resolver searches for media files in the following order:
    1. Relative to the current page's directory
    2. Relative to the source root
    3. By filename anywhere in the vault (Obsidian's shortest-path resolution)

    Args:
        source_dir: The root source directory.
        page_path: The path of the current page relative to source_dir.
        media_index: Optional pre-built index of media files by filename.

    Returns:
        A resolver function that takes a media target and returns
        (src_url, actual_path) or None if not found.
    """
    page_dir = (source_dir / page_path).parent

    def resolve_media(target: str) -> tuple[str, str] | None:
        # Try relative to current page first
        relative_path = page_dir / target
        if relative_path.exists():
            actual_path = str(relative_path.relative_to(source_dir))
            src_url = "/" + actual_path
            return src_url, actual_path

        # Try relative to source root
        root_path = source_dir / target
        if root_path.exists():
            actual_path = target
            src_url = "/" + target
            return src_url, actual_path

        # Fallback: search by filename (Obsidian shortest-path resolution)
        if media_index:
            filename = target.rsplit("/", 1)[-1].lower()
            matches = media_index.get(filename)
            if matches:
                actual_path = matches[0]
                src_url = "/" + actual_path
                return src_url, actual_path

        return None

    return resolve_media


def copy_assets(images: set[str], source_dir: Path, output_dir: Path) -> int:
    """Copy image assets from source to output directory.

    Preserves directory structure (mirrors source paths).

    Args:
        images: Set of image paths relative to source_dir.
        source_dir: The root source directory.
        output_dir: The output directory.

    Returns:
        Number of images copied.
    """
    count = 0
    for image_path in images:
        src = source_dir / image_path
        dst = output_dir / image_path

        if not src.exists():
            continue

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        count += 1

    return count


def collect_all_images(
    source_dir: Path, ignore_patterns: list[str] | None = None
) -> set[str]:
    """Collect all image files from source directory.

    Args:
        source_dir: The root source directory.
        ignore_patterns: Patterns to ignore (not implemented yet).

    Returns:
        Set of image paths relative to source_dir.
    """
    images = set()
    for ext in IMAGE_EXTENSIONS:
        for path in source_dir.rglob(f"*.{ext}"):
            images.add(str(path.relative_to(source_dir)))
        for path in source_dir.rglob(f"*.{ext.upper()}"):
            images.add(str(path.relative_to(source_dir)))
    return images
