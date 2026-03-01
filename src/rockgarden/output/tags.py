"""Tag index page generation."""

import re
from pathlib import Path

from jinja2 import Environment

from rockgarden.content.models import Page
from rockgarden.urls import get_tag_url, get_tags_root_url, get_url


def normalize_tag(tag: str) -> str:
    """Normalize a tag to a URL-safe slug.

    Strips leading '#', lowercases, and replaces any character that is not
    alphanumeric, hyphen, or underscore with a hyphen. This prevents path
    traversal via tags containing '/' or '..'.

    Tags 'Python', '#python', and 'python' all normalize to 'python'.
    Obsidian nested tags like 'character/pc' normalize to 'character-pc'.
    """
    slug = tag.lstrip("#").lower()
    slug = re.sub(r"[^a-z0-9_-]", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def collect_tags(pages: list[Page]) -> dict[str, list[Page]]:
    """Return a mapping of normalized tag slug → list of pages with that tag.

    Pages are included in the order they appear in the input list. Tags with
    no pages are not included. Result is sorted alphabetically by tag slug.
    """
    tags: dict[str, list[Page]] = {}
    for page in pages:
        raw_tags = page.frontmatter.get("tags", [])
        if isinstance(raw_tags, str):
            raw_tags = [raw_tags]
        for tag in raw_tags:
            slug = normalize_tag(tag)
            if slug:
                tags.setdefault(slug, []).append(page)
    return dict(sorted(tags.items()))


def build_tag_pages(
    tags: dict[str, list[Page]],
    env: Environment,
    site_config: dict,
    output: Path,
    clean_urls: bool = True,
) -> None:
    """Generate /tags/<slug>/ and /tags/ pages in the output directory."""
    tag_index_template = env.get_template("tag_index.html")
    tags_root_template = env.get_template("tags_root.html")

    for tag_slug, tagged_pages in tags.items():
        page_entries = [
            {"title": p.title, "url": get_url(p.slug, clean_urls)}
            for p in tagged_pages
        ]
        html = tag_index_template.render(
            tag=tag_slug,
            pages=page_entries,
            site=site_config,
        )
        if clean_urls:
            out_file = output / "tags" / tag_slug / "index.html"
        else:
            out_file = output / "tags" / f"{tag_slug}.html"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(html)

    tag_counts = {slug: len(pages) for slug, pages in tags.items()}
    html = tags_root_template.render(
        tags=tag_counts,
        site=site_config,
    )
    out_file = output / "tags" / "index.html"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(html)
