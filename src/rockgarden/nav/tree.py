"""Navigation tree builder."""

from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch

from rockgarden.config import NavConfig
from rockgarden.content import Page


@dataclass
class NavNode:
    """A node in the navigation tree (folder or page)."""

    name: str
    path: str
    label: str
    is_folder: bool
    children: list[NavNode] = field(default_factory=list)


def _should_hide(path: str, hide_patterns: list[str]) -> bool:
    """Check if a path matches any hide pattern."""
    for pattern in hide_patterns:
        normalized_pattern = pattern.strip("/")
        normalized_path = path.strip("/")
        if fnmatch(normalized_path, normalized_pattern):
            return True
        if fnmatch(normalized_path, f"{normalized_pattern}/*"):
            return True
        if normalized_path.startswith(f"{normalized_pattern}/"):
            return True
    return False


def _resolve_label(
    path: str,
    name: str,
    labels: dict[str, str],
    folder_pages: dict[str, Page],
) -> str:
    """Resolve display label for a nav item.

    Resolution order:
    1. Config override (labels dict)
    2. Folder's index.md frontmatter title
    3. Name (titlecased)
    """
    normalized_path = f"/{path.strip('/')}" if path else "/"

    if normalized_path in labels:
        return labels[normalized_path]

    if path in folder_pages:
        page = folder_pages[path]
        if title := page.frontmatter.get("title"):
            return title

    return name.replace("-", " ").replace("_", " ").title()


def build_nav_tree(pages: list[Page], config: NavConfig | None = None) -> NavNode:
    """Build navigation tree from a list of pages.

    Args:
        pages: List of Page objects from the content store
        config: Navigation configuration (hide patterns, labels, etc.)

    Returns:
        Root NavNode containing the full navigation tree
    """
    if config is None:
        config = NavConfig()

    folder_pages: dict[str, Page] = {}
    for page in pages:
        parts = page.slug.split("/")
        if parts[-1].lower() == "index":
            folder_path = "/".join(parts[:-1])
            folder_pages[folder_path] = page

    tree: dict[str, dict] = {}

    for page in pages:
        if _should_hide(page.slug, config.hide):
            continue

        parts = page.slug.split("/")

        current = tree
        current_path_parts: list[str] = []

        for part in parts[:-1]:
            current_path_parts.append(part)
            folder_path = "/".join(current_path_parts)

            if _should_hide(folder_path, config.hide):
                break

            if part not in current:
                current[part] = {
                    "_children": {},
                    "_is_folder": True,
                    "_path": folder_path,
                }
            current = current[part]["_children"]

        if not _should_hide(page.slug, config.hide):
            page_name = parts[-1]
            if page_name.lower() != "index":
                current[page_name] = {
                    "_children": {},
                    "_is_folder": False,
                    "_path": page.slug,
                    "_page": page,
                }

    def dict_to_nodes(d: dict, parent_path: str = "") -> list[NavNode]:
        nodes = []
        for name, data in sorted(d.items()):
            if name.startswith("_"):
                continue

            path = data.get("_path", "")
            is_folder = data.get("_is_folder", False)

            if is_folder:
                label = _resolve_label(path, name, config.labels, folder_pages)
                url_path = f"/{path}/index.html" if path else "/index.html"
            else:
                page = data.get("_page")
                label = page.title if page else name
                url_path = f"/{path}.html"

            children = dict_to_nodes(data.get("_children", {}), path)

            nodes.append(
                NavNode(
                    name=name,
                    path=url_path,
                    label=label,
                    is_folder=is_folder,
                    children=children,
                )
            )

        folders = [n for n in nodes if n.is_folder]
        files = [n for n in nodes if not n.is_folder]
        return folders + files

    root_label = _resolve_label("", "Home", config.labels, folder_pages)
    root_children = dict_to_nodes(tree)

    return NavNode(
        name="",
        path="/index.html",
        label=root_label,
        is_folder=True,
        children=root_children,
    )
