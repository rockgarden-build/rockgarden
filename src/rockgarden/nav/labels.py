"""Label resolution for navigation items."""

from rockgarden.content import Page


def resolve_label(
    path: str,
    name: str,
    labels: dict[str, str],
    folder_pages: dict[str, Page] | None = None,
) -> str:
    """Resolve display label for a nav item.

    Resolution order:
    1. Config override (labels dict)
    2. Folder's index page title (uses Page.title which checks frontmatter then filename)
    3. Name with underscores replaced by spaces (fallback when no index page)
    """
    normalized_path = f"/{path.strip('/')}" if path else "/"

    if normalized_path in labels:
        return labels[normalized_path]

    if folder_pages and path in folder_pages:
        return folder_pages[path].title

    return name.replace("_", " ")
