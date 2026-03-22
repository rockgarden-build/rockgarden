"""llms.txt generation following the llmstxt.org specification."""

from __future__ import annotations

from rockgarden.content.collection import Collection
from rockgarden.content.models import Page
from rockgarden.nav.folder_index import FolderIndex
from rockgarden.urls import get_url


def build_llms_txt(
    pages: list[Page],
    folder_indexes: list[FolderIndex],
    collections: dict[str, Collection],
    base_url: str,
    site_title: str,
    description: str = "",
    clean_urls: bool = True,
    base_path: str = "",
) -> str:
    """Generate an llms.txt string.

    Sections are ordered: named collections first, then remaining pages grouped
    by top-level directory, then root-level pages.

    Args:
        pages: All content pages.
        folder_indexes: All folder index pages.
        collections: Named collections mapping.
        base_url: Site base URL (e.g., "https://example.com").
        site_title: Site title for the H1 heading.
        description: Site description for the blockquote.
        clean_urls: Whether clean URLs are enabled.
        base_path: URL path prefix.

    Returns:
        llms.txt content string.
    """
    lines: list[str] = [f"# {site_title}"]

    if description:
        lines.append("")
        lines.append(f"> {description}")

    collected_slugs: set[str] = set()
    for col in collections.values():
        entries = [e for e in col.entries if isinstance(e, Page)]
        if not entries:
            continue
        lines.append("")
        lines.append(f"## {col.name}")
        lines.append("")
        for entry in sorted(entries, key=lambda p: p.title.lower()):
            url = base_url + get_url(entry.slug, clean_urls, base_path)
            lines.append(f"- [{entry.title}]({url})")
            collected_slugs.add(entry.slug)

    dir_groups: dict[str, list[Page | FolderIndex]] = {}
    root_items: list[Page | FolderIndex] = []

    all_items: list[Page | FolderIndex] = [
        p for p in pages if p.slug not in collected_slugs
    ]
    all_items.extend(folder_indexes)

    for item in all_items:
        parts = item.slug.split("/")
        if len(parts) > 1:
            top_dir = parts[0]
            dir_groups.setdefault(top_dir, []).append(item)
        else:
            root_items.append(item)

    for dir_name in sorted(dir_groups):
        items = sorted(dir_groups[dir_name], key=lambda p: p.title.lower())
        lines.append("")
        lines.append(f"## {dir_name}")
        lines.append("")
        for item in items:
            url = base_url + get_url(item.slug, clean_urls, base_path)
            lines.append(f"- [{item.title}]({url})")

    if root_items:
        items = sorted(root_items, key=lambda p: p.title.lower())
        lines.append("")
        lines.append("## Pages")
        lines.append("")
        for item in items:
            url = base_url + get_url(item.slug, clean_urls, base_path)
            lines.append(f"- [{item.title}]({url})")

    lines.append("")
    return "\n".join(lines)
