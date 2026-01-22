"""Breadcrumb generation for page navigation."""

from __future__ import annotations

from dataclasses import dataclass

from rockgarden.config import NavConfig
from rockgarden.content import Page
from rockgarden.nav.labels import resolve_label
from rockgarden.urls import get_folder_url, get_url


@dataclass
class Breadcrumb:
    """A single breadcrumb in the navigation path."""

    label: str
    path: str


def build_breadcrumbs(
    page: Page,
    pages: list[Page],
    config: NavConfig | None = None,
    clean_urls: bool = True,
) -> list[Breadcrumb]:
    """Build breadcrumb trail for a page.

    Args:
        page: The current page
        pages: All pages (for looking up folder index titles)
        config: Navigation config (for label overrides)
        clean_urls: If True, use /path/ instead of /path/index.html

    Returns:
        List of Breadcrumb objects from root to current page
    """
    if config is None:
        config = NavConfig()

    folder_pages: dict[str, Page] = {}
    for p in pages:
        parts = p.slug.split("/")
        if parts[-1] == "index":
            folder_path = "/".join(parts[:-1])
            folder_pages[folder_path] = p

    # Build mapping from slugified folder paths to original folder names
    # using the current page's source_path
    original_folder_names: dict[str, str] = {}
    slug_parts = page.slug.split("/")
    num_parts = len(slug_parts)
    source_parts = page.source_path.parts[-num_parts:]
    for i in range(len(slug_parts) - 1):
        folder_slug_path = "/".join(slug_parts[: i + 1])
        original_folder_names[folder_slug_path] = source_parts[i]

    breadcrumbs: list[Breadcrumb] = []

    root_label = resolve_label("", "Home", config.labels, folder_pages)
    root_path = get_folder_url("", clean_urls)
    breadcrumbs.append(Breadcrumb(label=root_label, path=root_path))

    parts = page.slug.split("/")

    if parts[-1] == "index" and len(parts) == 1:
        return breadcrumbs

    current_path_parts: list[str] = []
    for part in parts[:-1]:
        current_path_parts.append(part)
        folder_path = "/".join(current_path_parts)

        original_name = original_folder_names.get(folder_path, part)
        label = resolve_label(folder_path, original_name, config.labels, folder_pages)
        folder_url = get_folder_url(folder_path, clean_urls)
        breadcrumbs.append(Breadcrumb(label=label, path=folder_url))

    if parts[-1] != "index":
        page_url = get_url(page.slug, clean_urls)
        breadcrumbs.append(Breadcrumb(label=page.title, path=page_url))

    return breadcrumbs
