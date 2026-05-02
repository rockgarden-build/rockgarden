"""Tests for XML sitemap generation."""

from datetime import datetime
from pathlib import Path

from rockgarden.content.models import Page
from rockgarden.nav.folder_index import FolderIndex
from rockgarden.output.sitemap import build_sitemap


class TestBuildSitemap:
    def _make_page(self, slug, modified=None):
        return Page(
            source_path=Path(f"{slug}.md"),
            slug=slug,
            modified=modified,
        )

    def test_basic_page(self):
        pages = [self._make_page("about")]
        result = build_sitemap(pages, [], "https://example.com")
        assert "https://example.com/about/" in result

    def test_includes_xml_declaration(self):
        result = build_sitemap([], [], "https://example.com")
        assert result.startswith('<?xml version="1.0"')

    def test_includes_lastmod_when_modified(self):
        pages = [self._make_page("page", datetime(2026, 1, 15))]
        result = build_sitemap(pages, [], "https://example.com")
        assert "<lastmod>2026-01-15</lastmod>" in result

    def test_no_lastmod_when_no_modified(self):
        pages = [self._make_page("page")]
        result = build_sitemap(pages, [], "https://example.com")
        assert "<lastmod>" not in result

    def test_includes_folder_indexes(self):
        folders = [FolderIndex(slug="docs/index", title="Docs", children=[])]
        result = build_sitemap([], folders, "https://example.com")
        assert "https://example.com/docs/" in result

    def test_multiple_pages(self):
        pages = [self._make_page("one"), self._make_page("two")]
        result = build_sitemap(pages, [], "https://example.com")
        assert "https://example.com/one/" in result
        assert "https://example.com/two/" in result

    def test_base_url_no_trailing_slash(self):
        pages = [self._make_page("page")]
        result = build_sitemap(pages, [], "https://example.com")
        assert "https://example.com/page/" in result
        assert "https://example.com//page/" not in result

    def test_non_clean_urls(self):
        pages = [self._make_page("page")]
        result = build_sitemap(pages, [], "https://example.com", clean_urls=False)
        assert "https://example.com/page.html" in result

    def test_base_path_applied_to_pages(self):
        pages = [self._make_page("about")]
        result = build_sitemap(pages, [], "https://example.com", base_path="/2026")
        assert "https://example.com/2026/about/" in result
        assert "<loc>https://example.com/about/</loc>" not in result

    def test_base_path_applied_to_folder_indexes(self):
        folders = [FolderIndex(slug="docs/index", title="Docs", children=[])]
        result = build_sitemap([], folders, "https://example.com", base_path="/2026")
        assert "https://example.com/2026/docs/" in result

    def test_path_in_base_url_not_doubled(self):
        # When the path is encoded in base_url and base_path is derived to
        # match (as builder.py does via get_base_path), the result must not
        # double up the path component.
        pages = [self._make_page("about")]
        folders = [FolderIndex(slug="guide/index", title="Guide", children=[])]
        result = build_sitemap(
            pages, folders, "https://example.com/docs", base_path="/docs"
        )
        assert "https://example.com/docs/about/" in result
        assert "https://example.com/docs/guide/" in result
        assert "https://example.com/docs/docs/" not in result
