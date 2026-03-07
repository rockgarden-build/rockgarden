"""Tag index page generation."""

from pathlib import Path

from jinja2 import Environment

from rockgarden.content.models import Page
from rockgarden.urls import get_url, normalize_tag


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
    base_path: str = "",
    layout_template: str = "layouts/default.html",
) -> None:
    """Generate /tags/<slug>/ and /tags/ pages in the output directory."""
    tag_index_template = env.get_template("tag_index.html")
    tags_root_template = env.get_template("tags_root.html")

    def _page_entry(p: Page) -> dict:
        return {
            "title": p.title,
            "url": get_url(p.slug, clean_urls, base_path),
            "date": p.modified or p.created,
            "tags": [
                normalize_tag(t)
                for t in p.frontmatter.get("tags", [])
                if normalize_tag(t)
            ],
        }

    def _sorted_entries(pages: list[Page]) -> list[dict]:
        entries = [_page_entry(p) for p in pages]
        return sorted(
            entries,
            key=lambda e: (e["date"] or "", e["title"]),
            reverse=True,
        )

    for tag_slug, tagged_pages in tags.items():
        page_entries = _sorted_entries(tagged_pages)
        html = tag_index_template.render(
            tag=tag_slug,
            pages=page_entries,
            site=site_config,
            layout_template=layout_template,
        )
        if clean_urls:
            out_file = output / "tags" / tag_slug / "index.html"
        else:
            out_file = output / "tags" / f"{tag_slug}.html"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(html)

    tags_data = {slug: _sorted_entries(pages) for slug, pages in tags.items()}
    html = tags_root_template.render(
        tags=tags_data,
        site=site_config,
        layout_template=layout_template,
    )
    out_file = output / "tags" / "index.html"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(html)
