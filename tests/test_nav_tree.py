"""Tests for navigation tree building."""

from pathlib import Path

from rockgarden.config import NavConfig
from rockgarden.content import Page
from rockgarden.nav import build_nav_tree


def make_page(
    slug: str, title: str | None = None, nav_order: int | None = None
) -> Page:
    """Helper to create a Page with minimal required fields."""
    frontmatter = {}
    if title:
        frontmatter["title"] = title
    if nav_order is not None:
        frontmatter["nav_order"] = nav_order
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
        assert tree.children[0].path == "/about/"
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
        assert characters.label == "characters"
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

    def test_files_sorted_before_folders(self):
        """Files appear before folders, both alphabetically."""
        pages = [
            make_page("zebra", "Zebra"),
            make_page("folder/page", "Page"),
            make_page("alpha", "Alpha"),
        ]
        tree = build_nav_tree(pages)

        # Files first (alphabetically), then folders
        assert tree.children[0].is_folder is False
        assert tree.children[0].name == "alpha"
        assert tree.children[1].is_folder is False
        assert tree.children[1].name == "zebra"
        assert tree.children[2].is_folder is True
        assert tree.children[2].name == "folder"


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

    def test_default_label_preserves_name(self):
        """Default label preserves folder name, only replacing underscores."""
        pages = [
            make_page("my-folder/page", "Page"),
        ]
        tree = build_nav_tree(pages)
        folder = tree.children[0]
        assert folder.label == "my-folder"

        pages2 = [
            make_page("my_folder/page", "Page"),
        ]
        tree2 = build_nav_tree(pages2)
        folder2 = tree2.children[0]
        assert folder2.label == "my folder"


class TestNavOrder:
    def test_nav_order_pins_first(self):
        """Pages with nav_order appear before unpinned pages."""
        pages = [
            make_page("zebra", "Zebra"),
            make_page("getting-started", "Getting Started", nav_order=1),
            make_page("alpha", "Alpha"),
        ]
        tree = build_nav_tree(pages)

        assert tree.children[0].label == "Getting Started"
        assert tree.children[0].nav_order == 1
        assert tree.children[1].label == "Alpha"
        assert tree.children[2].label == "Zebra"

    def test_nav_order_sorting(self):
        """Multiple pinned pages sort by nav_order."""
        pages = [
            make_page("config", "Configuration", nav_order=2),
            make_page("getting-started", "Getting Started", nav_order=1),
            make_page("about", "About"),
        ]
        tree = build_nav_tree(pages)

        assert tree.children[0].label == "Getting Started"
        assert tree.children[1].label == "Configuration"
        assert tree.children[2].label == "About"

    def test_nav_order_negative(self):
        """Negative nav_order values work."""
        pages = [
            make_page("home", "Home", nav_order=-1),
            make_page("getting-started", "Getting Started", nav_order=1),
            make_page("about", "About"),
        ]
        tree = build_nav_tree(pages)

        assert tree.children[0].label == "Home"
        assert tree.children[1].label == "Getting Started"
        assert tree.children[2].label == "About"

    def test_nav_order_folder_from_index(self):
        """Folder nav_order comes from its index.md frontmatter."""
        pages = [
            make_page("guides/index", "Guides", nav_order=1),
            make_page("guides/quick-start", "Quick Start"),
            make_page("reference/index", "Reference"),
            make_page("reference/api", "API"),
        ]
        tree = build_nav_tree(pages)

        assert tree.children[0].label == "Guides"
        assert tree.children[0].nav_order == 1
        assert tree.children[1].label == "Reference"

    def test_nav_order_same_value_alphabetical(self):
        """Same nav_order values sort alphabetically."""
        pages = [
            make_page("zebra", "Zebra", nav_order=1),
            make_page("alpha", "Alpha", nav_order=1),
        ]
        tree = build_nav_tree(pages)

        assert tree.children[0].label == "Alpha"
        assert tree.children[1].label == "Zebra"


class TestSortConfig:
    def test_sort_files_first_default(self):
        """Default sort is files-first."""
        pages = [
            make_page("folder/page", "Page"),
            make_page("file", "File"),
        ]
        tree = build_nav_tree(pages)

        assert tree.children[0].is_folder is False
        assert tree.children[1].is_folder is True

    def test_sort_folders_first(self):
        """folders-first sort puts folders before files."""
        pages = [
            make_page("folder/page", "Page"),
            make_page("file", "File"),
        ]
        config = NavConfig(sort="folders-first")
        tree = build_nav_tree(pages, config)

        assert tree.children[0].is_folder is True
        assert tree.children[1].is_folder is False

    def test_sort_alphabetical(self):
        """alphabetical sort mixes files and folders."""
        pages = [
            make_page("bbb-folder/page", "Page"),
            make_page("aaa-file", "AAA File"),
            make_page("ccc-file", "CCC File"),
        ]
        config = NavConfig(sort="alphabetical")
        tree = build_nav_tree(pages, config)

        assert tree.children[0].label == "AAA File"
        assert tree.children[1].label == "bbb-folder"
        assert tree.children[2].label == "CCC File"

    def test_sort_with_nav_order(self):
        """Pinned items come before sort strategy."""
        pages = [
            make_page("folder/page", "Page"),
            make_page("zebra", "Zebra"),
            make_page("alpha", "Alpha", nav_order=1),
        ]
        config = NavConfig(sort="folders-first")
        tree = build_nav_tree(pages, config)

        assert tree.children[0].label == "Alpha"
        assert tree.children[1].is_folder is True
        assert tree.children[2].label == "Zebra"
