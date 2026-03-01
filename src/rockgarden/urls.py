"""Centralized URL and path generation utilities."""

import re
from urllib.parse import urlparse


def normalize_tag(tag: str) -> str:
    """Normalize a tag to a URL-safe slug.

    Strips leading '#', lowercases, and replaces any character that is not
    alphanumeric, hyphen, or underscore with a hyphen. Prevents path traversal
    via tags containing '/' or '..'.

    Tags 'Python', '#python', and 'python' all normalize to 'python'.
    Obsidian nested tags like 'character/pc' normalize to 'character-pc'.
    """
    slug = tag.lstrip("#").lower()
    slug = re.sub(r"[^a-z0-9_-]", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def get_base_path(base_url: str) -> str:
    """Extract the path component from a base URL for use as a path prefix.

    Examples:
        "https://example.com/docs/" → "/docs"
        "https://example.com/" → ""
        "" → ""
    """
    if not base_url:
        return ""
    path = urlparse(base_url).path.rstrip("/")
    return path


def generate_slug(relative_path: str) -> str:
    """Generate URL-safe slug from a relative file path.

    Removes extension, lowercases, and replaces spaces/underscores with dashes.

    Examples:
        "Getting Started.md" → "getting-started"
        "NPCs/Olvir the Wise.md" → "npcs/olvir-the-wise"
        "folder/index.md" → "folder/index"

    Args:
        relative_path: Relative path from source root (e.g., "NPCs/Olvir.md").

    Returns:
        URL-safe slug (e.g., "npcs/olvir").
    """
    slug = re.sub(r"\.md$", "", relative_path, flags=re.IGNORECASE)
    slug = slug.lower()
    slug = re.sub(r"[ _]+", "-", slug)
    return slug


def get_output_path(slug: str, clean_urls: bool = True) -> str:
    """Get filesystem output path for a page.

    Args:
        slug: The page slug (e.g., "about", "folder/page").
        clean_urls: If True, generates directory-based output paths.

    Returns:
        Output file path:
        - clean_urls=True:  "about" → "about/index.html"
        - clean_urls=False: "about" → "about.html"
        - Index pages:      "folder/index" → "folder/index.html" (always)
    """
    parts = slug.split("/")
    if parts[-1] == "index":
        return f"{slug}.html"

    if clean_urls:
        return f"{slug}/index.html"
    return f"{slug}.html"


def get_url(slug: str, clean_urls: bool = True, base_path: str = "") -> str:
    """Get URL for a page.

    Args:
        slug: The page slug (e.g., "about", "folder/page").
        clean_urls: If True, uses trailing slash format.
        base_path: Optional path prefix (e.g., "/docs").

    Returns:
        URL path:
        - clean_urls=True:  "about" → "/about/"
        - clean_urls=False: "about" → "/about.html"
        - Index pages:      "folder/index" → "/folder/"
    """
    parts = slug.split("/")

    if parts[-1] == "index":
        folder_path = "/".join(parts[:-1])
        if folder_path:
            return f"{base_path}/{folder_path}/"
        return f"{base_path}/"

    if clean_urls:
        return f"{base_path}/{slug}/"
    return f"{base_path}/{slug}.html"


def get_tag_url(tag_slug: str, clean_urls: bool = True, base_path: str = "") -> str:
    """Get URL for a tag index page.

    Args:
        tag_slug: Normalized tag slug (e.g., "python").
        clean_urls: If True, uses trailing slash format.
        base_path: Optional path prefix (e.g., "/docs").

    Returns:
        URL path:
        - clean_urls=True:  "python" → "/tags/python/"
        - clean_urls=False: "python" → "/tags/python.html"
    """
    if clean_urls:
        return f"{base_path}/tags/{tag_slug}/"
    return f"{base_path}/tags/{tag_slug}.html"


def get_tags_root_url(clean_urls: bool = True, base_path: str = "") -> str:
    """Get URL for the tags root index page."""
    return f"{base_path}/tags/" if clean_urls else f"{base_path}/tags/index.html"


def get_folder_url(folder_path: str, clean_urls: bool = True, base_path: str = "") -> str:
    """Get URL for a folder.

    Args:
        folder_path: Path to folder (e.g., "examples", "docs/api").
        clean_urls: If True, uses trailing slash format.
        base_path: Optional path prefix (e.g., "/docs").

    Returns:
        URL path:
        - clean_urls=True:  "examples" → "/examples/"
        - clean_urls=False: "examples" → "/examples/index.html"
        - Root folder:      "" → "/" or "/index.html"
    """
    if not folder_path:
        return f"{base_path}/" if clean_urls else f"{base_path}/index.html"

    if clean_urls:
        return f"{base_path}/{folder_path}/"
    return f"{base_path}/{folder_path}/index.html"
