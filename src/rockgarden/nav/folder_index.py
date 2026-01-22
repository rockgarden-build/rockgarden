"""Folder index page generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from rockgarden.config import NavConfig
from rockgarden.content import Page
from rockgarden.nav.labels import resolve_label
from rockgarden.urls import get_folder_url, get_url


@dataclass
class FolderChild:
    """A child item in a folder listing."""

    title: str
    path: str
    is_folder: bool
    modified: datetime | None = None
    tags: list[str] = field(default_factory=list)
    nav_order: int | None = None


@dataclass
class FolderIndex:
    """Data for rendering a folder index page."""

    slug: str
    title: str
    children: list[FolderChild]
    custom_content: str | None = None
    frontmatter: dict = field(default_factory=dict)


def find_folders(pages: list[Page]) -> set[str]:
    """Find all folder paths that need index pages."""
    folders: set[str] = set()

    for page in pages:
        parts = page.slug.split("/")
        if len(parts) > 1:
            for i in range(1, len(parts)):
                folder_path = "/".join(parts[:i])
                folders.add(folder_path)

    return folders


def generate_folder_indexes(
    pages: list[Page],
    config: NavConfig | None = None,
    clean_urls: bool = True,
) -> list[FolderIndex]:
    """Generate folder index data for all folders.

    Args:
        pages: All pages from the content store
        config: Navigation config for hide patterns and labels
        clean_urls: If True, use /path/ instead of /path/index.html

    Returns:
        List of FolderIndex objects for folders that need generated indexes
    """
    if config is None:
        config = NavConfig()

    folders = find_folders(pages)

    existing_indexes: dict[str, Page] = {}
    for page in pages:
        parts = page.slug.split("/")
        if parts[-1] == "index":
            folder_path = "/".join(parts[:-1])
            existing_indexes[folder_path] = page

    folder_indexes: list[FolderIndex] = []

    for folder_path in sorted(folders):
        if _should_hide(folder_path, config.hide):
            continue

        children = _get_folder_children(folder_path, pages, config, clean_urls)

        if folder_path in existing_indexes:
            index_page = existing_indexes[folder_path]
            title = index_page.title
            custom_content = index_page.content
            frontmatter = index_page.frontmatter
        else:
            folder_name = folder_path.split("/")[-1]
            title = resolve_label(folder_path, folder_name, config.labels)
            custom_content = None
            frontmatter = {}

        folder_indexes.append(
            FolderIndex(
                slug=f"{folder_path}/index" if folder_path else "index",
                title=title,
                children=children,
                custom_content=custom_content,
                frontmatter=frontmatter,
            )
        )

    return folder_indexes


def _should_hide(path: str, hide_patterns: list[str]) -> bool:
    """Check if a path should be hidden."""
    from fnmatch import fnmatch

    for pattern in hide_patterns:
        normalized_pattern = pattern.strip("/")
        normalized_path = path.strip("/")
        if fnmatch(normalized_path, normalized_pattern):
            return True
        if normalized_path.startswith(f"{normalized_pattern}/"):
            return True
    return False


def _sort_folder_children(
    children: list[FolderChild], sort_strategy: str
) -> list[FolderChild]:
    """Sort folder children by nav_order (pinned first) then by strategy."""
    pinned = [c for c in children if c.nav_order is not None]
    unpinned = [c for c in children if c.nav_order is None]

    pinned.sort(key=lambda c: (c.nav_order, c.title.lower()))

    if sort_strategy == "folders-first":
        folders = sorted(
            [c for c in unpinned if c.is_folder], key=lambda c: c.title.lower()
        )
        files = sorted(
            [c for c in unpinned if not c.is_folder], key=lambda c: c.title.lower()
        )
        unpinned = folders + files
    elif sort_strategy == "alphabetical":
        unpinned = sorted(unpinned, key=lambda c: c.title.lower())
    else:  # files-first (default)
        files = sorted(
            [c for c in unpinned if not c.is_folder], key=lambda c: c.title.lower()
        )
        folders = sorted(
            [c for c in unpinned if c.is_folder], key=lambda c: c.title.lower()
        )
        unpinned = files + folders

    return pinned + unpinned


def _get_folder_children(
    folder_path: str,
    pages: list[Page],
    config: NavConfig,
    clean_urls: bool = True,
) -> list[FolderChild]:
    """Get direct children of a folder."""
    children: list[FolderChild] = []
    seen_subfolders: set[str] = set()

    folder_index_pages: dict[str, Page] = {}
    for page in pages:
        parts = page.slug.split("/")
        if parts[-1] == "index":
            idx_folder_path = "/".join(parts[:-1])
            folder_index_pages[idx_folder_path] = page

    prefix = f"{folder_path}/" if folder_path else ""

    for page in pages:
        if not page.slug.startswith(prefix):
            continue

        relative = page.slug[len(prefix) :]
        if not relative:
            continue

        parts = relative.split("/")

        if len(parts) == 1:
            if parts[0] == "index":
                continue
            if _should_hide(page.slug, config.hide):
                continue

            modified = None
            if page.source_path.exists():
                modified = datetime.fromtimestamp(page.source_path.stat().st_mtime)

            children.append(
                FolderChild(
                    title=page.title,
                    path=get_url(page.slug, clean_urls),
                    is_folder=False,
                    modified=modified,
                    tags=page.frontmatter.get("tags", []),
                    nav_order=page.frontmatter.get("nav_order"),
                )
            )
        else:
            subfolder = parts[0]
            subfolder_path = f"{prefix}{subfolder}" if prefix else subfolder

            if subfolder_path not in seen_subfolders:
                if _should_hide(subfolder_path, config.hide):
                    continue

                seen_subfolders.add(subfolder_path)
                label = resolve_label(subfolder_path, subfolder, config.labels)

                nav_order = None
                if subfolder_path in folder_index_pages:
                    nav_order = folder_index_pages[subfolder_path].frontmatter.get(
                        "nav_order"
                    )

                children.append(
                    FolderChild(
                        title=label,
                        path=get_folder_url(subfolder_path, clean_urls),
                        is_folder=True,
                        nav_order=nav_order,
                    )
                )

    return _sort_folder_children(children, config.sort)
