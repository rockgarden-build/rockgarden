"""Label resolution for navigation items."""

from rockgarden.content import FolderMeta, Page


def resolve_label(
    path: str,
    name: str,
    labels: dict[str, str],
    folder_metas: dict[str, FolderMeta] | None = None,
    folder_pages: dict[str, Page] | None = None,
) -> str:
    """Resolve display label for a nav item.

    Resolution order:
    1. Config override (labels dict)
    2. `label` field in the folder's `_folder.md` metadata
    3. Folder index page title (from index.md / folder-note frontmatter)
    4. Name with underscores replaced by spaces (fallback)
    """
    normalized_path = f"/{path.strip('/')}" if path else "/"

    if normalized_path in labels:
        return labels[normalized_path]

    if folder_metas and path in folder_metas:
        meta_label = folder_metas[path].label
        if meta_label:
            return meta_label

    if folder_pages and path in folder_pages:
        return folder_pages[path].title

    return name.replace("_", " ")
