"""Tests for backlinks and link index."""

from pathlib import Path

from rockgarden.content.link_index import LinkIndex, build_link_index, extract_wikilink_targets
from rockgarden.content.models import Page
from rockgarden.content.store import ContentStore


class TestExtractWikilinkTargets:
    """Tests for extracting wiki-link targets from content."""

    def test_single_link(self):
        """Extract a single wiki-link target."""
        content = "See [[Other Page]] for details."
        targets = extract_wikilink_targets(content)
        assert targets == ["Other Page"]

    def test_multiple_links(self):
        """Extract multiple wiki-link targets."""
        content = "See [[Page One]] and [[Page Two]]."
        targets = extract_wikilink_targets(content)
        assert targets == ["Page One", "Page Two"]

    def test_link_with_display_text(self):
        """Extract target from link with display text."""
        content = "See [[Actual Page|display text]]."
        targets = extract_wikilink_targets(content)
        assert targets == ["Actual Page"]

    def test_link_in_code_block_ignored(self):
        """Wiki-links in code blocks are ignored."""
        content = "```\n[[Not A Link]]\n```"
        targets = extract_wikilink_targets(content)
        assert targets == []

    def test_link_in_inline_code_ignored(self):
        """Wiki-links in inline code are ignored."""
        content = "Use `[[syntax]]` for links."
        targets = extract_wikilink_targets(content)
        assert targets == []

    def test_mixed_content(self):
        """Extract links from mixed content with code."""
        content = "See [[Real Link]] but not `[[Code Link]]`."
        targets = extract_wikilink_targets(content)
        assert targets == ["Real Link"]

    def test_whitespace_trimmed(self):
        """Whitespace around targets is trimmed."""
        content = "[[ Spaced Link ]]"
        targets = extract_wikilink_targets(content)
        assert targets == ["Spaced Link"]


class TestLinkIndex:
    """Tests for LinkIndex class."""

    def test_get_backlinks_empty(self):
        """Get backlinks for page with no incoming links."""
        index = LinkIndex()
        backlinks = index.get_backlinks("page-a")
        assert backlinks == set()

    def test_get_backlinks_with_links(self):
        """Get backlinks for page with incoming links."""
        index = LinkIndex(
            incoming={"page-a": {"page-b", "page-c"}},
        )
        backlinks = index.get_backlinks("page-a")
        assert backlinks == {"page-b", "page-c"}

    def test_get_outgoing_links_empty(self):
        """Get outgoing links for page with no outgoing links."""
        index = LinkIndex()
        outgoing = index.get_outgoing_links("page-a")
        assert outgoing == set()

    def test_get_outgoing_links_with_links(self):
        """Get outgoing links for page with outgoing links."""
        index = LinkIndex(
            outgoing={"page-a": {"page-b", "page-c"}},
        )
        outgoing = index.get_outgoing_links("page-a")
        assert outgoing == {"page-b", "page-c"}


class TestBuildLinkIndex:
    """Tests for building link index from pages."""

    def test_single_link(self):
        """Build index with single link between pages."""
        pages = [
            Page(
                source_path=Path("page-a.md"),
                slug="page-a",
                content="See [[page-b]].",
            ),
            Page(
                source_path=Path("page-b.md"),
                slug="page-b",
                content="Content.",
            ),
        ]
        store = ContentStore(pages)
        index = build_link_index(pages, store)

        assert index.get_outgoing_links("page-a") == {"page-b"}
        assert index.get_backlinks("page-b") == {"page-a"}

    def test_bidirectional_links(self):
        """Build index with bidirectional links."""
        pages = [
            Page(
                source_path=Path("page-a.md"),
                slug="page-a",
                content="See [[page-b]].",
            ),
            Page(
                source_path=Path("page-b.md"),
                slug="page-b",
                content="See [[page-a]].",
            ),
        ]
        store = ContentStore(pages)
        index = build_link_index(pages, store)

        assert index.get_outgoing_links("page-a") == {"page-b"}
        assert index.get_outgoing_links("page-b") == {"page-a"}
        assert index.get_backlinks("page-a") == {"page-b"}
        assert index.get_backlinks("page-b") == {"page-a"}

    def test_multiple_backlinks(self):
        """Build index with multiple pages linking to one page."""
        pages = [
            Page(
                source_path=Path("page-a.md"),
                slug="page-a",
                content="See [[Hub]].",
            ),
            Page(
                source_path=Path("page-b.md"),
                slug="page-b",
                content="See [[Hub]].",
            ),
            Page(
                source_path=Path("hub.md"),
                slug="hub",
                content="Central page.",
            ),
        ]
        store = ContentStore(pages)
        index = build_link_index(pages, store)

        assert index.get_backlinks("hub") == {"page-a", "page-b"}

    def test_broken_link_ignored(self):
        """Broken links (unresolved targets) are not indexed."""
        pages = [
            Page(
                source_path=Path("page-a.md"),
                slug="page-a",
                content="See [[NonExistent]].",
            ),
        ]
        store = ContentStore(pages)
        index = build_link_index(pages, store)

        assert index.get_outgoing_links("page-a") == set()

    def test_link_with_display_text(self):
        """Links with display text are indexed by target."""
        pages = [
            Page(
                source_path=Path("page-a.md"),
                slug="page-a",
                content="See [[page-b|different text]].",
            ),
            Page(
                source_path=Path("page-b.md"),
                slug="page-b",
                content="Content.",
            ),
        ]
        store = ContentStore(pages)
        index = build_link_index(pages, store)

        assert index.get_outgoing_links("page-a") == {"page-b"}
        assert index.get_backlinks("page-b") == {"page-a"}

    def test_alias_resolution(self):
        """Links to aliases are resolved to the target page."""
        pages = [
            Page(
                source_path=Path("page-a.md"),
                slug="page-a",
                content="See [[Alias]].",
            ),
            Page(
                source_path=Path("page-b.md"),
                slug="page-b",
                content="Content.",
                frontmatter={"aliases": ["Alias"]},
            ),
        ]
        store = ContentStore(pages)
        index = build_link_index(pages, store)

        assert index.get_outgoing_links("page-a") == {"page-b"}
        assert index.get_backlinks("page-b") == {"page-a"}

    def test_self_link_ignored(self):
        """Self-links are tracked (user might want to see them)."""
        pages = [
            Page(
                source_path=Path("page-a.md"),
                slug="page-a",
                content="See [[page-a]] for more.",
            ),
        ]
        store = ContentStore(pages)
        index = build_link_index(pages, store)

        # Self-links are tracked
        assert index.get_outgoing_links("page-a") == {"page-a"}
        assert index.get_backlinks("page-a") == {"page-a"}
