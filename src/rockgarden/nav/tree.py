"""Navigation tree builder."""

from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch

from rockgarden.config import NavConfig
from rockgarden.content import Page
from rockgarden.nav.labels import resolve_label
from rockgarden.urls import get_folder_url, get_url


@dataclass
class NavNode:
    """A node in the navigation tree (folder or page)."""

    name: str
    path: str
    label: str
    is_folder: bool
    children: list[NavNode] = field(default_factory=list)
    nav_order: int | None = None
    index_path: str | None = None


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


def _sort_nav_nodes(nodes: list[NavNode], sort_strategy: str) -> list[NavNode]:
    """Sort nav nodes by nav_order (pinned first) then by strategy.

    Args:
        nodes: List of NavNode objects to sort
        sort_strategy: One of "files-first", "folders-first", "alphabetical"

    Returns:
        Sorted list of NavNode objects
    """
    pinned = [n for n in nodes if n.nav_order is not None]
    unpinned = [n for n in nodes if n.nav_order is None]

    pinned.sort(key=lambda n: (n.nav_order, n.label.lower()))

    def by_label(n: NavNode) -> str:
        return n.label.lower()

    if sort_strategy == "folders-first":
        folders = sorted([n for n in unpinned if n.is_folder], key=by_label)
        files = sorted([n for n in unpinned if not n.is_folder], key=by_label)
        unpinned = folders + files
    elif sort_strategy == "alphabetical":
        unpinned = sorted(unpinned, key=by_label)
    else:  # files-first (default)
        files = sorted([n for n in unpinned if not n.is_folder], key=by_label)
        folders = sorted([n for n in unpinned if n.is_folder], key=by_label)
        unpinned = files + folders

    return pinned + unpinned


def build_nav_tree(
    pages: list[Page],
    config: NavConfig | None = None,
    clean_urls: bool = True,
) -> NavNode:
    """Build navigation tree from a list of pages.

    Args:
        pages: List of Page objects from the content store
        config: Navigation configuration (hide patterns, labels, etc.)
        clean_urls: If True, use /path/ instead of /path/index.html

    Returns:
        Root NavNode containing the full navigation tree
    """
    if config is None:
        config = NavConfig()

    folder_pages: dict[str, Page] = {}
    for page in pages:
        parts = page.slug.split("/")
        if parts[-1] == "index":
            folder_path = "/".join(parts[:-1])
            folder_pages[folder_path] = page

    # Build mapping from slugified folder paths to original folder names
    original_folder_names: dict[str, str] = {}
    for page in pages:
        slug_parts = page.slug.split("/")
        num_parts = len(slug_parts)
        # Extract original path parts from source_path (last N parts, including filename)
        source_parts = page.source_path.parts[-num_parts:]
        # Map each folder's slug path to its original name
        for i in range(len(slug_parts) - 1):
            folder_slug_path = "/".join(slug_parts[: i + 1])
            if folder_slug_path not in original_folder_names:
                original_folder_names[folder_slug_path] = source_parts[i]

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
                original_name = original_folder_names.get(folder_path, part)
                current[part] = {
                    "_children": {},
                    "_is_folder": True,
                    "_path": folder_path,
                    "_original_name": original_name,
                }
            current = current[part]["_children"]

        if not _should_hide(page.slug, config.hide):
            page_name = parts[-1]
            if page_name != "index":
                current[page_name] = {
                    "_children": {},
                    "_is_folder": False,
                    "_path": page.slug,
                    "_page": page,
                }

    def dict_to_nodes(d: dict, parent_path: str = "") -> list[NavNode]:
        nodes = []
        for name, data in d.items():
            if name.startswith("_"):
                continue

            path = data.get("_path", "")
            is_folder = data.get("_is_folder", False)
            nav_order = None

            if is_folder:
                original_name = data.get("_original_name", name)
                label = resolve_label(path, original_name, config.labels, folder_pages)
                url_path = get_folder_url(path, clean_urls)
                if path in folder_pages:
                    nav_order = folder_pages[path].frontmatter.get("nav_order")
            else:
                page = data.get("_page")
                label = page.title if page else name
                url_path = get_url(path, clean_urls)
                if page:
                    nav_order = page.frontmatter.get("nav_order")

            children = dict_to_nodes(data.get("_children", {}), path)
            children = _sort_nav_nodes(children, config.sort)

            index_path = None
            if is_folder:
                if path in folder_pages:
                    index_page = folder_pages[path]
                    index_path = get_url(index_page.slug, clean_urls)
                elif config.link_auto_index:
                    index_path = url_path

            nodes.append(
                NavNode(
                    name=name,
                    path=url_path,
                    label=label,
                    is_folder=is_folder,
                    children=children,
                    nav_order=nav_order,
                    index_path=index_path,
                )
            )

        return _sort_nav_nodes(nodes, config.sort)

    root_label = resolve_label("", "Home", config.labels, folder_pages)
    root_children = dict_to_nodes(tree)

    return NavNode(
        name="",
        path=get_folder_url("", clean_urls),
        label=root_label,
        is_folder=True,
        children=root_children,
    )
