"""Content store for page lookups."""

from pathlib import Path

from rockgarden.content.models import Page


class ContentStore:
    """Store for looking up pages by name, slug, or alias."""

    def __init__(self, pages: list[Page]) -> None:
        self.pages = pages
        self._by_slug: dict[str, Page] = {}
        self._by_name: dict[str, Page] = {}

        for page in pages:
            self._index_page(page)

    def _index_page(self, page: Page) -> None:
        """Index a page for lookup."""
        self._by_slug[page.slug] = page

        name = page.source_path.stem
        self._by_name[name.lower()] = page

        if aliases := page.frontmatter.get("aliases"):
            if isinstance(aliases, list):
                for alias in aliases:
                    self._by_name[alias.lower()] = page
            elif isinstance(aliases, str):
                self._by_name[aliases.lower()] = page

    def get_by_slug(self, slug: str) -> Page | None:
        """Look up a page by its slug."""
        return self._by_slug.get(slug)

    def get_by_name(self, name: str) -> Page | None:
        """Look up a page by its name or alias (case-insensitive)."""
        return self._by_name.get(name.lower())

    def resolve_link(self, link_target: str) -> str | None:
        """Resolve a wiki-link target to a URL path.

        Args:
            link_target: The target from [[target]] or [[target|text]].

        Returns:
            The URL path (e.g., "/Getting Started.html") or None if not found.
        """
        page = self.get_by_name(link_target)
        if page:
            return "/" + page.output_path
        return None
