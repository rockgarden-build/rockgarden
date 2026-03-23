"""llms.txt generation following the llmstxt.org specification."""

from __future__ import annotations

from dataclasses import dataclass

from rockgarden.config import NavLinkConfig
from rockgarden.content.collection import Collection
from rockgarden.content.models import Page
from rockgarden.nav.folder_index import FolderIndex
from rockgarden.output.html_to_md import html_to_markdown
from rockgarden.urls import get_url


@dataclass
class _SectionItem:
    title: str
    url: str
    html: str | None = None


@dataclass
class _Section:
    heading: str
    items: list[_SectionItem]


def _flatten_nav_links(links: list[NavLinkConfig]) -> list[NavLinkConfig]:
    """Flatten nested nav links, keeping only entries with a URL."""
    result: list[NavLinkConfig] = []
    for link in links:
        if link.url:
            result.append(link)
        result.extend(_flatten_nav_links(link.children))
    return result


def _get_item_html(item: Page | FolderIndex) -> str | None:
    if isinstance(item, Page):
        return item.html
    return item.custom_content


def _group_content(
    pages: list[Page],
    folder_indexes: list[FolderIndex],
    collections: dict[str, Collection],
    base_url: str,
    clean_urls: bool,
    base_path: str,
    nav_links: list[NavLinkConfig] | None,
) -> list[_Section]:
    """Group pages into ordered sections.

    Returns sections in order: named collections, directory groups,
    root pages, nav links.
    """
    sections: list[_Section] = []

    collected_slugs: set[str] = set()
    for col in collections.values():
        entries = [e for e in col.entries if isinstance(e, Page)]
        if not entries:
            continue
        items = []
        for entry in sorted(entries, key=lambda p: p.title.lower()):
            url = base_url + get_url(entry.slug, clean_urls, base_path)
            items.append(_SectionItem(entry.title, url, _get_item_html(entry)))
            collected_slugs.add(entry.slug)
        sections.append(_Section(col.name, items))

    dir_groups: dict[str, list[Page | FolderIndex]] = {}
    root_items: list[Page | FolderIndex] = []

    all_items: list[Page | FolderIndex] = [
        p for p in pages if p.slug not in collected_slugs
    ]
    collected_dirs = {col.config.source for col in collections.values() if col.entries}
    all_items.extend(
        fi for fi in folder_indexes if fi.slug.rsplit("/", 1)[0] not in collected_dirs
    )

    for item in all_items:
        parts = item.slug.split("/")
        if len(parts) > 1:
            top_dir = parts[0]
            dir_groups.setdefault(top_dir, []).append(item)
        else:
            root_items.append(item)

    for dir_name in sorted(dir_groups):
        sorted_items = sorted(dir_groups[dir_name], key=lambda p: p.title.lower())
        items = []
        for item in sorted_items:
            url = base_url + get_url(item.slug, clean_urls, base_path)
            items.append(_SectionItem(item.title, url, _get_item_html(item)))
        sections.append(_Section(dir_name, items))

    if root_items:
        sorted_items = sorted(root_items, key=lambda p: p.title.lower())
        items = []
        for item in sorted_items:
            url = base_url + get_url(item.slug, clean_urls, base_path)
            items.append(_SectionItem(item.title, url, _get_item_html(item)))
        sections.append(_Section("Pages", items))

    if nav_links:
        flat_links = _flatten_nav_links(nav_links)
        if flat_links:
            items = [_SectionItem(link.label, link.url) for link in flat_links]
            sections.append(_Section("Links", items))

    return sections


def build_llms_txt(
    pages: list[Page],
    folder_indexes: list[FolderIndex],
    collections: dict[str, Collection],
    base_url: str,
    site_title: str,
    description: str = "",
    clean_urls: bool = True,
    base_path: str = "",
    nav_links: list[NavLinkConfig] | None = None,
    full_url: str = "",
) -> str:
    """Generate an llms.txt string.

    Sections are ordered: named collections first, then remaining pages grouped
    by top-level directory, then root-level pages, then nav links.

    Args:
        pages: All content pages.
        folder_indexes: All folder index pages.
        collections: Named collections mapping.
        base_url: Site base URL (e.g., "https://example.com").
        site_title: Site title for the H1 heading.
        description: Site description for the blockquote.
        clean_urls: Whether clean URLs are enabled.
        base_path: URL path prefix.
        nav_links: Custom navigation links from config.
        full_url: URL to llms-full.txt, included in description if set.

    Returns:
        llms.txt content string.
    """
    lines: list[str] = [f"# {site_title}"]

    if description or full_url:
        lines.append("")
        if description:
            lines.append(f"> {description}")
        if full_url:
            if description:
                lines.append(">")
            lines.append(f"> Full content available at: {full_url}")

    sections = _group_content(
        pages, folder_indexes, collections, base_url, clean_urls, base_path, nav_links
    )

    for section in sections:
        lines.append("")
        lines.append(f"## {section.heading}")
        lines.append("")
        for item in section.items:
            lines.append(f"- [{item.title}]({item.url})")

    lines.append("")
    return "\n".join(lines)


def build_llms_full_txt(
    pages: list[Page],
    folder_indexes: list[FolderIndex],
    collections: dict[str, Collection],
    base_url: str,
    site_title: str,
    description: str = "",
    clean_urls: bool = True,
    base_path: str = "",
    nav_links: list[NavLinkConfig] | None = None,
) -> str:
    """Generate an llms-full.txt string with inline page content.

    Same structure as llms.txt but each page entry includes its full content
    converted from HTML to markdown.

    Args:
        pages: All content pages.
        folder_indexes: All folder index pages.
        collections: Named collections mapping.
        base_url: Site base URL (e.g., "https://example.com").
        site_title: Site title for the H1 heading.
        description: Site description for the blockquote.
        clean_urls: Whether clean URLs are enabled.
        base_path: URL path prefix.
        nav_links: Custom navigation links from config.

    Returns:
        llms-full.txt content string.
    """
    lines: list[str] = [f"# {site_title}"]

    if description:
        lines.append("")
        lines.append(f"> {description}")

    sections = _group_content(
        pages, folder_indexes, collections, base_url, clean_urls, base_path, nav_links
    )

    for section in sections:
        # Nav links section: just links, no content
        if section.heading == "Links":
            lines.append("")
            lines.append(f"## {section.heading}")
            lines.append("")
            for item in section.items:
                lines.append(f"- [{item.title}]({item.url})")
            continue

        for item in section.items:
            lines.append("")
            lines.append(f"## {item.title}")
            lines.append("")
            lines.append(f"Source: {item.url}")

            content = html_to_markdown(item.html or "")
            if content:
                lines.append("")
                lines.append(content)

            lines.append("")
            lines.append("---")

    lines.append("")
    return "\n".join(lines)
