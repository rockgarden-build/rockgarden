"""Tests for navigation tree building."""

from pathlib import Path

from rockgarden.config import NavConfig
from rockgarden.content import Page
from rockgarden.nav import build_nav_tree


def make_page(slug: str, title: str | None = None) -> Page:
    """Helper to create a Page with minimal required fields."""
    frontmatter = {"title": title} if title else {}
    return Page(
        source_path=Path(f"/vault/{slug}.md"),
        slug=slug,
        frontmatter=frontmatter,
        content="",
    )


class TestBuildNavTree:
    def test_empty_pages(self):
        """Empty page list produces root-only tree."""
        tree = build_nav_tree([])
        assert tree.name == ""
        assert tree.is_folder is True
        assert tree.children == []

    def test_flat_pages(self):
        """Pages without folders appear as children of root."""
        pages = [
            make_page("about", "About Us"),
            make_page("contact", "Contact"),
        ]
        tree = build_nav_tree(pages)

        assert len(tree.children) == 2
        assert tree.children[0].label == "About Us"
        assert tree.children[0].path == "/about.html"
        assert tree.children[0].is_folder is False

    def test_nested_folders(self):
        """Pages in folders create nested tree structure."""
        pages = [
            make_page("characters/alice", "Alice"),
            make_page("characters/bob", "Bob"),
            make_page("locations/town", "Town"),
        ]
        tree = build_nav_tree(pages)

        assert len(tree.children) == 2
        folders = [c for c in tree.children if c.is_folder]
        assert len(folders) == 2

        characters = next(c for c in folders if c.name == "characters")
        assert characters.label == "Characters"
        assert len(characters.children) == 2

    def test_deeply_nested(self):
        """Deep nesting is preserved."""
        pages = [
            make_page("a/b/c/page", "Deep Page"),
        ]
        tree = build_nav_tree(pages)

        assert len(tree.children) == 1
        a = tree.children[0]
        assert a.name == "a"
        assert a.is_folder is True

        b = a.children[0]
        assert b.name == "b"

        c = b.children[0]
        assert c.name == "c"

        page = c.children[0]
        assert page.label == "Deep Page"
        assert page.is_folder is False

    def test_folders_sorted_before_files(self):
        """Folders appear before files at each level."""
        pages = [
            make_page("zebra", "Zebra"),
            make_page("folder/page", "Page"),
            make_page("alpha", "Alpha"),
        ]
        tree = build_nav_tree(pages)

        assert tree.children[0].is_folder is True
        assert tree.children[0].name == "folder"
        assert tree.children[1].is_folder is False
        assert tree.children[2].is_folder is False


class TestNavConfigHide:
    def test_hide_path(self):
        """Hidden paths are excluded from tree."""
        pages = [
            make_page("public", "Public"),
            make_page("private/secret", "Secret"),
        ]
        config = NavConfig(hide=["/private"])
        tree = build_nav_tree(pages, config)

        assert len(tree.children) == 1
        assert tree.children[0].label == "Public"

    def test_hide_nested_path(self):
        """Hidden nested paths are excluded."""
        pages = [
            make_page("docs/public", "Public Doc"),
            make_page("docs/internal/secret", "Secret"),
        ]
        config = NavConfig(hide=["/docs/internal"])
        tree = build_nav_tree(pages, config)

        docs = tree.children[0]
        assert len(docs.children) == 1
        assert docs.children[0].label == "Public Doc"


class TestNavConfigLabels:
    def test_label_override(self):
        """Config labels override folder names."""
        pages = [
            make_page("characters/alice", "Alice"),
        ]
        config = NavConfig(labels={"/characters": "Cast"})
        tree = build_nav_tree(pages, config)

        characters = tree.children[0]
        assert characters.label == "Cast"

    def test_label_from_index_frontmatter(self):
        """Folder label comes from index.md frontmatter title."""
        pages = [
            make_page("characters/index", "The Characters"),
            make_page("characters/alice", "Alice"),
        ]
        tree = build_nav_tree(pages)

        characters = tree.children[0]
        assert characters.label == "The Characters"

    def test_config_label_overrides_frontmatter(self):
        """Config label takes precedence over frontmatter."""
        pages = [
            make_page("characters/index", "The Characters"),
            make_page("characters/alice", "Alice"),
        ]
        config = NavConfig(labels={"/characters": "Cast"})
        tree = build_nav_tree(pages, config)

        characters = tree.children[0]
        assert characters.label == "Cast"

    def test_default_label_titlecase(self):
        """Default label is titlecased folder name."""
        pages = [
            make_page("my-folder/page", "Page"),
        ]
        tree = build_nav_tree(pages)

        folder = tree.children[0]
        assert folder.label == "My Folder"
