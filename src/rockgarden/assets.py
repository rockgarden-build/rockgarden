"""Asset collection and copying for static site generation."""

import shutil
from pathlib import Path

from rockgarden.obsidian.embeds import IMAGE_EXTENSIONS


def create_image_resolver(source_dir: Path, page_path: str):
    """Create an image resolver function for a specific page.

    The resolver searches for images in the following order:
    1. Relative to the current page's directory
    2. Relative to the source root

    Args:
        source_dir: The root source directory.
        page_path: The path of the current page relative to source_dir.

    Returns:
        A resolver function that takes an image target and returns
        (src_url, actual_path) or None if not found.
    """
    page_dir = (source_dir / page_path).parent

    def resolve_image(target: str) -> tuple[str, str] | None:
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

        return None

    return resolve_image


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
