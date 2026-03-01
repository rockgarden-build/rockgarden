"""Search index generation for client-side search."""

import re
from rockgarden.content.models import Page
from rockgarden.urls import get_url


def strip_html(html: str) -> str:
    """Strip HTML tags and return plain text.

    Args:
        html: HTML string to strip tags from

    Returns:
        Plain text with HTML tags removed and whitespace normalized
    """
    if not html:
        return ""

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", html)

    # Decode common HTML entities
    text = text.replace("&nbsp;", " ")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&amp;", "&")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def build_search_index(
    pages: list[Page], include_content: bool = True, clean_urls: bool = True, base_path: str = ""
) -> list[dict]:
    """Generate search index from pages.

    Args:
        pages: List of Page objects to index
        include_content: If True, index full content. If False, just title+tags.
        clean_urls: Whether to generate clean URLs (affects URL generation)

    Returns:
        List of search index entries as dicts
    """
    index = []

    for page in pages:
        # Build basic entry
        entry = {
            "title": page.title,
            "url": get_url(page.slug, clean_urls, base_path),
        }

        # Add tags if present
        tags = page.frontmatter.get("tags", [])
        if tags:
            # Ensure tags is a list
            if isinstance(tags, str):
                tags = [tags]
            entry["tags"] = tags

        # Add content if enabled
        if include_content and page.html:
            entry["content"] = strip_html(page.html)

        index.append(entry)

    return index
