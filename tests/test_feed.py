"""Tests for Atom feed generation."""

from datetime import UTC, datetime
from pathlib import Path
from xml.etree.ElementTree import fromstring

from rockgarden.content.models import Page
from rockgarden.output.feed import build_atom_feed

ATOM_NS = "http://www.w3.org/2005/Atom"


def _ns(tag: str) -> str:
    return f"{{{ATOM_NS}}}{tag}"


class TestBuildAtomFeed:
    def _make_page(self, slug, modified=None, created=None, html=None):
        return Page(
            source_path=Path(f"{slug}.md"),
            slug=slug,
            modified=modified,
            created=created,
            html=html,
        )

    def test_valid_xml(self):
        result = build_atom_feed([], "Test", "", "https://example.com")
        root = fromstring(result)
        assert root.tag == _ns("feed")

    def test_xml_declaration(self):
        result = build_atom_feed([], "Test", "", "https://example.com")
        assert result.startswith('<?xml version="1.0"')

    def test_feed_title(self):
        result = build_atom_feed([], "My Site", "", "https://example.com")
        root = fromstring(result)
        assert root.find(_ns("title")).text == "My Site"

    def test_feed_subtitle(self):
        result = build_atom_feed([], "Site", "A description", "https://example.com")
        root = fromstring(result)
        assert root.find(_ns("subtitle")).text == "A description"

    def test_no_subtitle_when_empty(self):
        result = build_atom_feed([], "Site", "", "https://example.com")
        root = fromstring(result)
        assert root.find(_ns("subtitle")) is None

    def test_feed_links(self):
        result = build_atom_feed([], "Site", "", "https://example.com")
        root = fromstring(result)
        links = root.findall(_ns("link"))
        hrefs = {el.get("rel", "alternate"): el.get("href") for el in links}
        assert hrefs["alternate"] == "https://example.com/"
        assert hrefs["self"] == "https://example.com/feed.xml"

    def test_feed_id(self):
        result = build_atom_feed([], "Site", "", "https://example.com")
        root = fromstring(result)
        assert root.find(_ns("id")).text == "https://example.com/"

    def test_feed_updated_present(self):
        result = build_atom_feed([], "Site", "", "https://example.com")
        root = fromstring(result)
        assert root.find(_ns("updated")).text is not None

    def test_feed_updated_from_most_recent_entry(self):
        pages = [
            self._make_page("old", modified=datetime(2026, 1, 1, tzinfo=UTC)),
            self._make_page("new", modified=datetime(2026, 3, 1, tzinfo=UTC)),
        ]
        result = build_atom_feed(pages, "Site", "", "https://example.com")
        root = fromstring(result)
        assert "2026-03-01" in root.find(_ns("updated")).text

    def test_entry_title(self):
        pages = [self._make_page("about")]
        result = build_atom_feed(pages, "Site", "", "https://example.com")
        root = fromstring(result)
        entry = root.find(_ns("entry"))
        assert entry.find(_ns("title")).text == "about"

    def test_entry_link(self):
        pages = [self._make_page("about")]
        result = build_atom_feed(pages, "Site", "", "https://example.com")
        root = fromstring(result)
        entry = root.find(_ns("entry"))
        assert entry.find(_ns("link")).get("href") == "https://example.com/about/"

    def test_entry_id(self):
        pages = [self._make_page("about")]
        result = build_atom_feed(pages, "Site", "", "https://example.com")
        root = fromstring(result)
        entry = root.find(_ns("entry"))
        assert entry.find(_ns("id")).text == "https://example.com/about/"

    def test_entry_updated(self):
        pages = [self._make_page("p", modified=datetime(2026, 2, 15, tzinfo=UTC))]
        result = build_atom_feed(pages, "Site", "", "https://example.com")
        root = fromstring(result)
        entry = root.find(_ns("entry"))
        assert "2026-02-15" in entry.find(_ns("updated")).text

    def test_entry_updated_fallback_when_no_date(self):
        pages = [self._make_page("p")]
        result = build_atom_feed(pages, "Site", "", "https://example.com")
        root = fromstring(result)
        entry = root.find(_ns("entry"))
        assert entry.find(_ns("updated")) is not None
        assert entry.find(_ns("updated")).text == root.find(_ns("updated")).text

    def test_entry_content(self):
        pages = [self._make_page("p", html="<p>Hello</p>")]
        result = build_atom_feed(pages, "Site", "", "https://example.com")
        root = fromstring(result)
        entry = root.find(_ns("entry"))
        content = entry.find(_ns("content"))
        assert content.get("type") == "html"
        assert content.text == "<p>Hello</p>"

    def test_no_content_when_no_html(self):
        pages = [self._make_page("p")]
        result = build_atom_feed(pages, "Site", "", "https://example.com")
        root = fromstring(result)
        entry = root.find(_ns("entry"))
        assert entry.find(_ns("content")) is None

    def test_date_sorting(self):
        pages = [
            self._make_page("old", modified=datetime(2026, 1, 1)),
            self._make_page("new", modified=datetime(2026, 3, 1)),
            self._make_page("mid", modified=datetime(2026, 2, 1)),
        ]
        result = build_atom_feed(pages, "Site", "", "https://example.com")
        root = fromstring(result)
        titles = [e.find(_ns("title")).text for e in root.findall(_ns("entry"))]
        assert titles == ["new", "mid", "old"]

    def test_pages_without_dates_sorted_last(self):
        pages = [
            self._make_page("no-date"),
            self._make_page("dated", modified=datetime(2026, 1, 1)),
        ]
        result = build_atom_feed(pages, "Site", "", "https://example.com")
        root = fromstring(result)
        titles = [e.find(_ns("title")).text for e in root.findall(_ns("entry"))]
        assert titles == ["dated", "no-date"]

    def test_limit(self):
        pages = [self._make_page(f"p{i}") for i in range(10)]
        result = build_atom_feed(pages, "Site", "", "https://example.com", limit=3)
        root = fromstring(result)
        assert len(root.findall(_ns("entry"))) == 3

    def test_include_paths_filtering(self):
        pages = [
            self._make_page("blog/post1"),
            self._make_page("about"),
            self._make_page("blog/post2"),
        ]
        result = build_atom_feed(
            pages, "Site", "", "https://example.com", include_paths=["blog/"]
        )
        root = fromstring(result)
        titles = [e.find(_ns("title")).text for e in root.findall(_ns("entry"))]
        assert "about" not in titles
        assert len(titles) == 2

    def test_empty_pages(self):
        result = build_atom_feed([], "Site", "", "https://example.com")
        root = fromstring(result)
        assert root.findall(_ns("entry")) == []

    def test_base_path(self):
        pages = [self._make_page("about")]
        result = build_atom_feed(
            pages, "Site", "", "https://example.com", base_path="/docs"
        )
        root = fromstring(result)
        entry = root.find(_ns("entry"))
        assert "/docs/about/" in entry.find(_ns("link")).get("href")
        # Feed self link includes base_path
        links = root.findall(_ns("link"))
        self_link = [el for el in links if el.get("rel") == "self"][0]
        assert self_link.get("href") == "https://example.com/docs/feed.xml"

    def test_non_clean_urls(self):
        pages = [self._make_page("about")]
        result = build_atom_feed(
            pages, "Site", "", "https://example.com", clean_urls=False
        )
        root = fromstring(result)
        entry = root.find(_ns("entry"))
        assert entry.find(_ns("link")).get("href") == "https://example.com/about.html"

    def test_uses_created_when_no_modified(self):
        pages = [self._make_page("p", created=datetime(2026, 5, 1, tzinfo=UTC))]
        result = build_atom_feed(pages, "Site", "", "https://example.com")
        root = fromstring(result)
        entry = root.find(_ns("entry"))
        assert "2026-05-01" in entry.find(_ns("updated")).text

    def test_naive_datetime_gets_utc(self):
        pages = [self._make_page("p", modified=datetime(2026, 1, 1))]
        result = build_atom_feed(pages, "Site", "", "https://example.com")
        root = fromstring(result)
        entry = root.find(_ns("entry"))
        updated = entry.find(_ns("updated")).text
        assert "+00:00" in updated

    def test_custom_feed_path_in_self_link(self):
        result = build_atom_feed(
            [], "Site", "", "https://example.com", feed_path="/atom.xml"
        )
        root = fromstring(result)
        links = root.findall(_ns("link"))
        self_link = [el for el in links if el.get("rel") == "self"][0]
        assert self_link.get("href") == "https://example.com/atom.xml"

    def test_mixed_tz_aware_and_naive_dates(self):
        pages = [
            self._make_page("aware", modified=datetime(2026, 1, 1, tzinfo=UTC)),
            self._make_page("naive", modified=datetime(2026, 2, 1)),
            self._make_page("no-date"),
        ]
        result = build_atom_feed(pages, "Site", "", "https://example.com")
        root = fromstring(result)
        titles = [e.find(_ns("title")).text for e in root.findall(_ns("entry"))]
        assert titles == ["naive", "aware", "no-date"]

    def test_feed_level_author(self):
        result = build_atom_feed([], "Site", "", "https://example.com", author="Alice")
        root = fromstring(result)
        author_el = root.find(_ns("author"))
        assert author_el is not None
        assert author_el.find(_ns("name")).text == "Alice"

    def test_no_author_when_not_configured(self):
        result = build_atom_feed([], "Site", "", "https://example.com")
        root = fromstring(result)
        assert root.find(_ns("author")) is None

    def test_entry_author_from_frontmatter(self):
        page = self._make_page("p")
        page.frontmatter["author"] = "Bob"
        result = build_atom_feed([page], "Site", "", "https://example.com")
        root = fromstring(result)
        entry = root.find(_ns("entry"))
        assert entry.find(_ns("author")).find(_ns("name")).text == "Bob"

    def test_entry_author_omitted_when_same_as_feed(self):
        page = self._make_page("p")
        page.frontmatter["author"] = "Alice"
        result = build_atom_feed(
            [page], "Site", "", "https://example.com", author="Alice"
        )
        root = fromstring(result)
        entry = root.find(_ns("entry"))
        assert entry.find(_ns("author")) is None

    def test_entry_author_overrides_feed_default(self):
        page = self._make_page("p")
        page.frontmatter["author"] = "Bob"
        result = build_atom_feed(
            [page], "Site", "", "https://example.com", author="Alice"
        )
        root = fromstring(result)
        # Feed-level author is Alice
        assert root.find(_ns("author")).find(_ns("name")).text == "Alice"
        # Entry overrides with Bob
        entry = root.find(_ns("entry"))
        assert entry.find(_ns("author")).find(_ns("name")).text == "Bob"
