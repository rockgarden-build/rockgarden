"""Breadcrumb generation for page navigation."""

from __future__ import annotations

from dataclasses import dataclass

from rockgarden.config import NavConfig
from rockgarden.content import Page


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
        if parts[-1].lower() == "index":
            folder_path = "/".join(parts[:-1])
            folder_pages[folder_path] = p

    breadcrumbs: list[Breadcrumb] = []

    root_label = _resolve_label("", "Home", config.labels, folder_pages)
    root_path = "/" if clean_urls else "/index.html"
    breadcrumbs.append(Breadcrumb(label=root_label, path=root_path))

    parts = page.slug.split("/")

    if parts[-1].lower() == "index" and len(parts) == 1:
        return breadcrumbs

    current_path_parts: list[str] = []
    for part in parts[:-1]:
        current_path_parts.append(part)
        folder_path = "/".join(current_path_parts)

        label = _resolve_label(folder_path, part, config.labels, folder_pages)
        if clean_urls:
            path = f"/{folder_path}/"
        else:
            path = f"/{folder_path}/index.html"

        breadcrumbs.append(Breadcrumb(label=label, path=path))

    if parts[-1].lower() != "index":
        breadcrumbs.append(Breadcrumb(label=page.title, path=f"/{page.slug}.html"))

    return breadcrumbs


def _resolve_label(
    path: str,
    name: str,
    labels: dict[str, str],
    folder_pages: dict[str, Page],
) -> str:
    """Resolve display label for a breadcrumb.

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
