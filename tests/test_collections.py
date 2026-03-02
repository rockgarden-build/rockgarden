"""Tests for collection partitioning and ContentStore collection support."""

from pathlib import Path

from rockgarden.config import CollectionConfig
from rockgarden.content.collection import Collection, partition_collections
from rockgarden.content.models import Page
from rockgarden.content.store import ContentStore


def make_page(rel_path: str, slug: str = "") -> Page:
    """Helper to create a Page with a relative source path."""
    if not slug:
        slug = rel_path.replace(".md", "").replace("/", "-")
    return Page(
        source_path=Path(rel_path),
        slug=slug,
        frontmatter={},
        content="",
    )


class TestPartitionCollections:
    def test_no_collections_configured(self):
        """Empty config → empty dict."""
        pages = [make_page("about.md", "about")]
        result = partition_collections(pages, [], Path("."))
        assert result == {}

    def test_single_collection(self):
        """Pages matched by source prefix."""
        pages = [
            make_page("characters/alice.md", "characters/alice"),
            make_page("characters/bob.md", "characters/bob"),
            make_page("locations/town.md", "locations/town"),
        ]
        configs = [CollectionConfig(name="characters", source="characters")]
        result = partition_collections(pages, configs, Path("."))

        assert "characters" in result
        assert len(result["characters"].entries) == 2
        slugs = {p.slug for p in result["characters"].entries}
        assert slugs == {"characters/alice", "characters/bob"}

    def test_nested_collections(self):
        """Pages in nested dirs appear in both parent and child collections."""
        pages = [
            make_page("characters/pcs/alice.md", "characters/pcs/alice"),
            make_page("characters/npcs/bob.md", "characters/npcs/bob"),
            make_page("characters/index.md", "characters/index"),
        ]
        configs = [
            CollectionConfig(name="characters", source="characters"),
            CollectionConfig(name="pcs", source="characters/pcs"),
        ]
        result = partition_collections(pages, configs, Path("."))

        assert len(result["characters"].entries) == 3
        assert len(result["pcs"].entries) == 1
        assert result["pcs"].entries[0].slug == "characters/pcs/alice"

    def test_empty_collection(self):
        """Collection with no matching pages exists with empty entries."""
        pages = [make_page("about.md", "about")]
        configs = [CollectionConfig(name="speakers", source="speakers")]
        result = partition_collections(pages, configs, Path("."))

        assert "speakers" in result
        assert result["speakers"].entries == []

    def test_absolute_source_paths(self):
        """Pages with absolute source paths are matched correctly."""
        source = Path("/vault/content")
        pages = [
            Page(
                source_path=source / "characters" / "alice.md",
                slug="characters/alice",
                frontmatter={},
                content="",
            ),
            Page(
                source_path=source / "about.md",
                slug="about",
                frontmatter={},
                content="",
            ),
        ]
        configs = [CollectionConfig(name="characters", source="characters")]
        result = partition_collections(pages, configs, source)

        assert len(result["characters"].entries) == 1
        assert result["characters"].entries[0].slug == "characters/alice"

    def test_trailing_slash_in_source(self):
        """Trailing slash in collection source config is handled."""
        pages = [make_page("characters/alice.md", "characters/alice")]
        configs = [CollectionConfig(name="characters", source="characters/")]
        result = partition_collections(pages, configs, Path("."))

        assert len(result["characters"].entries) == 1

    def test_page_not_in_any_collection(self):
        """Pages outside any collection source are not included."""
        pages = [
            make_page("characters/alice.md", "characters/alice"),
            make_page("about.md", "about"),
        ]
        configs = [CollectionConfig(name="characters", source="characters")]
        result = partition_collections(pages, configs, Path("."))

        assert len(result["characters"].entries) == 1
        all_entries = [e for c in result.values() for e in c.entries]
        assert not any(e.slug == "about" for e in all_entries)

    def test_collection_preserves_config(self):
        """Collection stores its config."""
        cfg = CollectionConfig(
            name="talks",
            source="talks",
            template="talk.html",
            url_pattern="/talks/{slug}/",
        )
        result = partition_collections([], [cfg], Path("."))
        assert result["talks"].config is cfg


class TestContentStoreCollections:
    def test_store_without_collections(self):
        """Default ContentStore has empty collections."""
        store = ContentStore([])
        assert store.collections == {}

    def test_store_with_collections(self):
        """ContentStore stores provided collections."""
        page = make_page("characters/alice.md", "characters/alice")
        cfg = CollectionConfig(name="characters", source="characters")
        col = Collection(name="characters", config=cfg, entries=[page])
        store = ContentStore([page], collections={"characters": col})

        assert store.get_collection("characters") is col

    def test_get_collection_missing(self):
        """get_collection returns None for unknown name."""
        store = ContentStore([])
        assert store.get_collection("nonexistent") is None

    def test_list_collection(self):
        """list_collection returns entries for a named collection."""
        page = make_page("characters/alice.md", "characters/alice")
        cfg = CollectionConfig(name="characters", source="characters")
        col = Collection(name="characters", config=cfg, entries=[page])
        store = ContentStore([page], collections={"characters": col})

        entries = store.list_collection("characters")
        assert len(entries) == 1
        assert entries[0].slug == "characters/alice"

    def test_list_collection_missing(self):
        """list_collection returns empty list for unknown name."""
        store = ContentStore([])
        assert store.list_collection("nonexistent") == []

    def test_wiki_links_resolve_across_collections(self):
        """Wiki-links still resolve for pages in collections."""
        page_in_col = Page(
            source_path=Path("characters/Alice.md"),
            slug="characters/alice",
            frontmatter={},
            content="",
        )
        page_outside = Page(
            source_path=Path("About.md"),
            slug="about",
            frontmatter={},
            content="",
        )
        store = ContentStore([page_in_col, page_outside])

        assert store.resolve_link("Alice") == "/characters/alice/"
        assert store.resolve_link("About") == "/about/"
