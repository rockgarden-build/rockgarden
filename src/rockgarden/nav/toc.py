"""Table of contents extraction from rendered HTML."""

import re
from dataclasses import dataclass, field
from html import unescape

HEADING_RE = re.compile(
    r"<(h[2-6])(\s[^>]*)?>(.+?)</\1>", re.DOTALL
)
TAG_RE = re.compile(r"<[^>]+>")


@dataclass
class TocEntry:
    """A single entry in the table of contents."""

    id: str
    text: str
    level: int
    children: list["TocEntry"] = field(default_factory=list)


def _slugify(text: str) -> str:
    """Convert heading text to a URL-friendly slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text.strip())
    return text


def _strip_tags(html: str) -> str:
    """Remove HTML tags and unescape entities to get plain text."""
    return unescape(TAG_RE.sub("", html).strip())


def _build_tree(flat: list[TocEntry]) -> list[TocEntry]:
    """Build a nested tree from a flat list of TocEntry by level."""
    root: list[TocEntry] = []
    stack: list[TocEntry] = []

    for entry in flat:
        while stack and stack[-1].level >= entry.level:
            stack.pop()

        if stack:
            stack[-1].children.append(entry)
        else:
            root.append(entry)

        stack.append(entry)

    return root


def extract_toc(
    html: str, min_level: int = 2, max_level: int = 4
) -> tuple[str, list[TocEntry]]:
    """Extract table of contents from rendered HTML and inject heading IDs.

    Finds heading tags (h2-h6 by default), generates slugified IDs, injects
    id attributes, and builds a nested TOC structure.

    Args:
        html: Rendered HTML string.
        min_level: Minimum heading level to include (default 2).
        max_level: Maximum heading level to include (default 4).

    Returns:
        Tuple of (modified HTML with id attrs, list of TocEntry trees).
    """
    seen_ids: dict[str, int] = {}
    flat_entries: list[TocEntry] = []

    def _replace_heading(match: re.Match) -> str:
        tag = match.group(1)
        attrs = match.group(2) or ""
        inner_html = match.group(3)
        level = int(tag[1])

        if level < min_level or level > max_level:
            # Still inject ID for anchor linking, but don't add to TOC
            text = _strip_tags(inner_html)
            slug = _slugify(text)
            if not slug:
                return match.group(0)
            if slug in seen_ids:
                seen_ids[slug] += 1
                slug = f"{slug}-{seen_ids[slug]}"
            else:
                seen_ids[slug] = 0
            if "id=" in attrs:
                return match.group(0)
            return f"<{tag}{attrs} id=\"{slug}\">{inner_html}</{tag}>"

        text = _strip_tags(inner_html)
        slug = _slugify(text)
        if not slug:
            return match.group(0)

        if slug in seen_ids:
            seen_ids[slug] += 1
            slug = f"{slug}-{seen_ids[slug]}"
        else:
            seen_ids[slug] = 0

        flat_entries.append(TocEntry(id=slug, text=text, level=level))

        if "id=" in attrs:
            return match.group(0)
        return f"<{tag}{attrs} id=\"{slug}\">{inner_html}</{tag}>"

    modified_html = HEADING_RE.sub(_replace_heading, html)
    toc_tree = _build_tree(flat_entries)

    return modified_html, toc_tree
