"""Atom feed generation."""

from datetime import UTC, datetime
from xml.etree.ElementTree import Element, SubElement, tostring

from rockgarden.content.models import Page
from rockgarden.urls import get_url

ATOM_NS = "http://www.w3.org/2005/Atom"


def _get_date(page: Page) -> datetime | None:
    """Get the best available date for a page (modified, then created)."""
    return page.modified or page.created


def _format_rfc3339(dt: datetime) -> str:
    """Format a datetime as RFC 3339 for Atom feeds."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.isoformat()


def build_atom_feed(
    pages: list[Page],
    site_title: str,
    site_description: str,
    base_url: str,
    clean_urls: bool = True,
    base_path: str = "",
    limit: int = 20,
    include_paths: list[str] | None = None,
) -> str:
    """Generate an Atom feed XML string.

    Args:
        pages: All content pages.
        site_title: Site title for the feed.
        site_description: Site description used as feed subtitle.
        base_url: Site base URL (e.g., "https://example.com").
        clean_urls: Whether clean URLs are enabled.
        base_path: URL path prefix (e.g., "/blog").
        limit: Maximum number of entries in the feed.
        include_paths: If set, only include pages whose slug starts with
            one of these path prefixes.

    Returns:
        Atom XML feed string.
    """
    candidates = list(pages)

    if include_paths:
        candidates = [
            p
            for p in candidates
            if any(p.slug.startswith(prefix) for prefix in include_paths)
        ]

    # Sort by date descending; pages without dates go last
    candidates.sort(key=lambda p: _get_date(p) or datetime.min, reverse=True)
    entries = candidates[:limit]

    feed = Element("feed", xmlns=ATOM_NS)

    title_el = SubElement(feed, "title")
    title_el.text = site_title

    if site_description:
        subtitle_el = SubElement(feed, "subtitle")
        subtitle_el.text = site_description

    SubElement(feed, "link", href=base_url + base_path + "/")
    SubElement(
        feed,
        "link",
        rel="self",
        href=base_url + base_path + "/feed.xml",
    )

    id_el = SubElement(feed, "id")
    id_el.text = base_url + base_path + "/"

    # Feed updated time is the most recent entry date, or now if no entries have dates
    most_recent = None
    for entry in entries:
        dt = _get_date(entry)
        if dt:
            most_recent = dt
            break
    updated_el = SubElement(feed, "updated")
    updated_el.text = _format_rfc3339(most_recent or datetime.now(tz=UTC))

    for page in entries:
        entry_el = SubElement(feed, "entry")

        entry_title = SubElement(entry_el, "title")
        entry_title.text = page.title

        page_url = base_url + get_url(page.slug, clean_urls, base_path)
        SubElement(entry_el, "link", href=page_url)

        entry_id = SubElement(entry_el, "id")
        entry_id.text = page_url

        dt = _get_date(page)
        if dt:
            entry_updated = SubElement(entry_el, "updated")
            entry_updated.text = _format_rfc3339(dt)

        if page.html:
            content_el = SubElement(entry_el, "content", type="html")
            content_el.text = page.html

    xml_bytes = tostring(feed, encoding="unicode", xml_declaration=False)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_bytes + "\n"
