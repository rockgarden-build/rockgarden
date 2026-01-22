"""Tests for breadcrumb generation."""

from pathlib import Path

from rockgarden.config import NavConfig
from rockgarden.content import Page
from rockgarden.nav import build_breadcrumbs


def make_page(slug: str, title: str | None = None) -> Page:
    """Helper to create a Page with minimal required fields."""
    frontmatter = {"title": title} if title else {}
    return Page(
        source_path=Path(f"/vault/{slug}.md"),
        slug=slug,
        frontmatter=frontmatter,
        content="",
    )


class TestBuildBreadcrumbs:
    def test_root_page(self):
        """Root index page has only Home breadcrumb."""
        page = make_page("index", "Home")
        breadcrumbs = build_breadcrumbs(page, [page])

        assert len(breadcrumbs) == 1
        assert breadcrumbs[0].label == "Home"
        assert breadcrumbs[0].path == "/"

    def test_top_level_page(self):
        """Top-level page has Home and page breadcrumbs."""
        index = make_page("index", "Home")
        about = make_page("about", "About Us")
        breadcrumbs = build_breadcrumbs(about, [index, about])

        assert len(breadcrumbs) == 2
        assert breadcrumbs[0].label == "Home"
        assert breadcrumbs[1].label == "About Us"
        assert breadcrumbs[1].path == "/about/"

    def test_nested_page(self):
        """Nested page includes folder breadcrumbs."""
        index = make_page("index", "Home")
        char_index = make_page("characters/index", "Characters")
        alice = make_page("characters/alice", "Alice")

        breadcrumbs = build_breadcrumbs(alice, [index, char_index, alice])

        assert len(breadcrumbs) == 3
        assert breadcrumbs[0].label == "Home"
        assert breadcrumbs[1].label == "Characters"
        assert breadcrumbs[1].path == "/characters/"
        assert breadcrumbs[2].label == "Alice"

    def test_deeply_nested(self):
        """Deeply nested pages have full breadcrumb trail."""
        page = make_page("a/b/c/page", "Deep Page")
        breadcrumbs = build_breadcrumbs(page, [page])

        assert len(breadcrumbs) == 5
        assert breadcrumbs[0].label == "Home"
        assert breadcrumbs[1].label == "a"
        assert breadcrumbs[1].path == "/a/"
        assert breadcrumbs[2].label == "b"
        assert breadcrumbs[3].label == "c"
        assert breadcrumbs[4].label == "Deep Page"

    def test_folder_index_page(self):
        """Folder index page breadcrumbs end at folder."""
        char_index = make_page("characters/index", "Characters")
        breadcrumbs = build_breadcrumbs(char_index, [char_index])

        assert len(breadcrumbs) == 2
        assert breadcrumbs[0].label == "Home"
        assert breadcrumbs[1].label == "Characters"
        assert breadcrumbs[1].path == "/characters/"

    def test_clean_urls_disabled(self):
        """When clean_urls=False, use index.html paths."""
        page = make_page("characters/alice", "Alice")
        breadcrumbs = build_breadcrumbs(page, [page], clean_urls=False)

        assert breadcrumbs[0].path == "/index.html"
        assert breadcrumbs[1].path == "/characters/index.html"


class TestBreadcrumbLabels:
    def test_label_from_folder_index(self):
        """Folder label comes from index.md title."""
        char_index = make_page("characters/index", "The Cast")
        alice = make_page("characters/alice", "Alice")

        breadcrumbs = build_breadcrumbs(alice, [char_index, alice])

        assert breadcrumbs[1].label == "The Cast"

    def test_config_label_override(self):
        """Config label overrides folder index title."""
        char_index = make_page("characters/index", "The Cast")
        alice = make_page("characters/alice", "Alice")
        config = NavConfig(labels={"/characters": "NPCs"})

        breadcrumbs = build_breadcrumbs(alice, [char_index, alice], config)

        assert breadcrumbs[1].label == "NPCs"

    def test_default_label_preserves_name(self):
        """Default label preserves folder name, only replacing underscores."""
        page = make_page("my-folder/page", "Page")
        breadcrumbs = build_breadcrumbs(page, [page])
        assert breadcrumbs[1].label == "my-folder"

        page2 = make_page("my_folder/page", "Page")
        breadcrumbs2 = build_breadcrumbs(page2, [page2])
        assert breadcrumbs2[1].label == "my folder"
