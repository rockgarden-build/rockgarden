"""Centralized URL and path generation utilities."""

import re


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


def get_url(slug: str, clean_urls: bool = True) -> str:
    """Get URL for a page.

    Args:
        slug: The page slug (e.g., "about", "folder/page").
        clean_urls: If True, uses trailing slash format.

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
            return f"/{folder_path}/"
        return "/"

    if clean_urls:
        return f"/{slug}/"
    return f"/{slug}.html"


def get_folder_url(folder_path: str, clean_urls: bool = True) -> str:
    """Get URL for a folder.

    Args:
        folder_path: Path to folder (e.g., "examples", "docs/api").
        clean_urls: If True, uses trailing slash format.

    Returns:
        URL path:
        - clean_urls=True:  "examples" → "/examples/"
        - clean_urls=False: "examples" → "/examples/index.html"
        - Root folder:      "" → "/" or "/index.html"
    """
    if not folder_path:
        return "/" if clean_urls else "/index.html"

    if clean_urls:
        return f"/{folder_path}/"
    return f"/{folder_path}/index.html"
