"""XML sitemap generation."""

from xml.etree.ElementTree import Element, SubElement, tostring

from rockgarden.content.models import Page
from rockgarden.nav.folder_index import FolderIndex
from rockgarden.urls import get_host_url, get_url


def build_sitemap(
    pages: list[Page],
    folder_indexes: list[FolderIndex],
    base_url: str,
    clean_urls: bool = True,
    base_path: str = "",
) -> str:
    """Generate an XML sitemap string.

    Args:
        pages: All content pages.
        folder_indexes: All folder index pages.
        base_url: Site base URL (e.g., "https://example.com").
        clean_urls: Whether clean URLs are enabled.
        base_path: Optional path prefix (e.g., "/docs").

    Returns:
        XML sitemap string.
    """
    NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
    urlset = Element("urlset", xmlns=NS)

    # Use the host portion of base_url so concatenation with base_path doesn't
    # double up when the user encoded the path in base_url itself.
    host_url = get_host_url(base_url)

    for page in pages:
        url_el = SubElement(urlset, "url")
        loc = SubElement(url_el, "loc")
        loc.text = host_url + get_url(page.slug, clean_urls, base_path)
        if page.modified:
            lastmod = SubElement(url_el, "lastmod")
            lastmod.text = page.modified.strftime("%Y-%m-%d")

    for folder in folder_indexes:
        url_el = SubElement(urlset, "url")
        loc = SubElement(url_el, "loc")
        loc.text = host_url + get_url(folder.slug, clean_urls, base_path)

    xml_bytes = tostring(urlset, encoding="unicode", xml_declaration=False)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_bytes + "\n"
