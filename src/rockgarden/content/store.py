"""Content store for page lookups."""

import unicodedata
from pathlib import Path

from rockgarden.content.models import Page
from rockgarden.urls import get_url

# Media file extensions that can be linked with [[filename]]
MEDIA_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "svg",
    "webp",
    "bmp",
    "ico",
    "mp3",
    "wav",
    "m4a",
    "ogg",
    "3gp",
    "flac",
    "mp4",
    "webm",
    "ogv",
    "mov",
    "mkv",
    "pdf",
}


class ContentStore:
    """Store for looking up pages by name, slug, or alias."""

    def __init__(
        self,
        pages: list[Page],
        clean_urls: bool = True,
        media_index: dict[str, list[str]] | None = None,
        base_path: str = "",
    ) -> None:
        self.pages = pages
        self.clean_urls = clean_urls
        self.media_index = media_index or {}
        self.base_path = base_path
        self._by_slug: dict[str, Page] = {}
        self._by_name: dict[str, Page] = {}

        for page in pages:
            self._index_page(page)

    def _index_page(self, page: Page) -> None:
        """Index a page for lookup."""
        self._by_slug[page.slug] = page

        name = page.source_path.stem
        normalized_name = unicodedata.normalize("NFC", name).lower()
        self._by_name[normalized_name] = page

        if aliases := page.frontmatter.get("aliases"):
            if isinstance(aliases, list):
                for alias in aliases:
                    normalized_alias = unicodedata.normalize("NFC", alias).lower()
                    self._by_name[normalized_alias] = page
            elif isinstance(aliases, str):
                normalized_alias = unicodedata.normalize("NFC", aliases).lower()
                self._by_name[normalized_alias] = page

    def get_by_slug(self, slug: str) -> Page | None:
        """Look up a page by its slug."""
        return self._by_slug.get(slug)

    def get_by_name(self, name: str) -> Page | None:
        """Look up a page by name or alias (case-insensitive, Unicode-normalized)."""
        normalized_name = unicodedata.normalize("NFC", name).lower()
        return self._by_name.get(normalized_name)

    def resolve_link(self, link_target: str) -> str | None:
        """Resolve a wiki-link target to a URL path.

        Handles section links (e.g., "Page#Section") and media file links.

        Args:
            link_target: The target from [[target]] or [[target|text]].

        Returns:
            The URL path (e.g., "/getting-started/") or None if not found.
        """
        # Split on # to handle section links
        if "#" in link_target:
            page_name, fragment = link_target.split("#", 1)
            page_name = page_name.strip()
            fragment = fragment.strip()
        else:
            page_name = link_target
            fragment = None

        # Try to resolve as a page first
        page = self.get_by_name(page_name)
        if page:
            url = get_url(page.slug, self.clean_urls, self.base_path)
            if fragment:
                url = f"{url}#{fragment}"
            return url

        # Try to resolve as a media file
        if self._is_media_file(page_name):
            media_url = self._resolve_media_file(page_name)
            if media_url:
                if fragment:
                    media_url = f"{media_url}#{fragment}"
                return media_url

        return None

    def _is_media_file(self, target: str) -> bool:
        """Check if target looks like a media file."""
        ext = Path(target).suffix.lstrip(".").lower()
        return ext in MEDIA_EXTENSIONS

    def _resolve_media_file(self, target: str) -> str | None:
        """Resolve a media file target to a URL."""
        if not self.media_index:
            return None

        filename = target.rsplit("/", 1)[-1].lower()
        matches = self.media_index.get(filename)
        if matches:
            return f"{self.base_path}/{matches[0]}"

        return None
