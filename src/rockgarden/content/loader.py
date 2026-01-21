"""Content discovery and loading."""

import fnmatch
from pathlib import Path

import frontmatter

from rockgarden.content.models import Page
from rockgarden.urls import generate_slug


def should_ignore(path: Path, source: Path, patterns: list[str]) -> bool:
    """Check if a path should be ignored based on patterns.

    Args:
        path: The file path to check.
        source: The source root directory.
        patterns: List of glob patterns to ignore.

    Returns:
        True if the path should be ignored.
    """
    rel_path = path.relative_to(source)

    for pattern in patterns:
        if fnmatch.fnmatch(str(rel_path), pattern):
            return True
        if fnmatch.fnmatch(rel_path.name, pattern):
            return True
        for part in rel_path.parts:
            if fnmatch.fnmatch(part, pattern):
                return True

    return False


def path_to_slug(path: Path, source: Path) -> str:
    """Convert a file path to a URL slug.

    Args:
        path: The file path.
        source: The source root directory.

    Returns:
        The slug (e.g., 'index', 'npcs/olvir').
    """
    rel_path = str(path.relative_to(source))
    return generate_slug(rel_path)


def load_page(path: Path, source: Path) -> Page:
    """Load a single page from a markdown file.

    Args:
        path: Path to the markdown file.
        source: The source root directory.

    Returns:
        A Page object with parsed frontmatter and content.
    """
    post = frontmatter.load(path)
    metadata = dict(post.metadata)

    if custom_slug := metadata.get("slug"):
        slug = custom_slug
    else:
        slug = path_to_slug(path, source)

    return Page(
        source_path=path,
        slug=slug,
        frontmatter=metadata,
        content=post.content,
    )


def load_content(source: Path, ignore_patterns: list[str]) -> list[Page]:
    """Discover and load all markdown files from source directory.

    Args:
        source: The source directory to scan.
        ignore_patterns: List of glob patterns to ignore.

    Returns:
        List of Page objects.
    """
    pages = []

    for path in source.rglob("*.md"):
        if should_ignore(path, source, ignore_patterns):
            continue

        page = load_page(path, source)
        pages.append(page)

    return pages
