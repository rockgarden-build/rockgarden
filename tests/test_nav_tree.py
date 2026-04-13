"""Tests for navigation tree building."""

from pathlib import Path

from rockgarden.config import FolderSortOverride, NavConfig, NavLinkConfig
from rockgarden.content import FolderMeta, Page
from rockgarden.nav import build_nav_tree
from rockgarden.nav.tree import convert_nav_links, inject_nav_links


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


def make_meta(folder_path: str, **fields) -> FolderMeta:
    """Helper to construct a FolderMeta with the given frontmatter fields."""
    return FolderMeta(
        source_path=Path(f"/vault/{folder_path}/_folder.md"),
        folder_path=folder_path,
        frontmatter=dict(fields),
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
        """Folder label falls back to index.md title."""
        pages = [
            make_page("characters/index", "The Characters"),
            make_page("characters/alice", "Alice"),
        ]
        tree = build_nav_tree(pages)

        characters = tree.children[0]
        assert characters.label == "The Characters"

    def test_label_from_folder_meta_overrides_index_title(self):
        """`_folder.md` label overrides the index.md title."""
        pages = [
            make_page("characters/index", "The Characters"),
            make_page("characters/alice", "Alice"),
        ]
        metas = {"characters": make_meta("characters", label="Cast")}
        tree = build_nav_tree(pages, folder_metas=metas)

        characters = tree.children[0]
        assert characters.label == "Cast"

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

    def test_nav_order_folder_from_meta(self):
        """Folder nav_order comes from `_folder.md`."""
        pages = [
            make_page("guides/index", "Guides"),
            make_page("guides/quick-start", "Quick Start"),
            make_page("reference/index", "Reference"),
            make_page("reference/api", "API"),
        ]
        metas = {"guides": make_meta("guides", label="Guides", nav_order=1)}
        tree = build_nav_tree(pages, folder_metas=metas)

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


class TestConvertNavLinks:
    def test_simple_link(self):
        links = [NavLinkConfig(label="Tags", url="/tags/")]
        nodes = convert_nav_links(links)
        assert len(nodes) == 1
        assert nodes[0].label == "Tags"
        assert nodes[0].path == "/tags/"
        assert nodes[0].is_external is False
        assert nodes[0].is_folder is False

    def test_external_link(self):
        links = [NavLinkConfig(label="GitHub", url="https://github.com/example")]
        nodes = convert_nav_links(links)
        assert nodes[0].is_external is True

    def test_http_external(self):
        links = [NavLinkConfig(label="Old Site", url="http://example.com")]
        nodes = convert_nav_links(links)
        assert nodes[0].is_external is True

    def test_nested_links(self):
        links = [
            NavLinkConfig(
                label="Resources",
                children=[
                    NavLinkConfig(label="GitHub", url="https://github.com/example"),
                    NavLinkConfig(label="Docs", url="/docs/"),
                ],
            )
        ]
        nodes = convert_nav_links(links)
        assert len(nodes) == 1
        assert nodes[0].is_folder is True
        assert nodes[0].index_path is None
        assert len(nodes[0].children) == 2
        assert nodes[0].children[0].label == "GitHub"
        assert nodes[0].children[0].is_external is True
        assert nodes[0].children[1].label == "Docs"
        assert nodes[0].children[1].is_external is False

    def test_nested_with_url(self):
        links = [
            NavLinkConfig(
                label="Resources",
                url="/resources/",
                children=[NavLinkConfig(label="Sub", url="/sub/")],
            )
        ]
        nodes = convert_nav_links(links)
        assert nodes[0].index_path == "/resources/"


class TestInjectNavLinks:
    def _make_tree(self):
        pages = [
            make_page("alpha", "Alpha"),
            make_page("beta", "Beta"),
        ]
        return build_nav_tree(pages)

    def test_after_position(self):
        tree = self._make_tree()
        links = [NavLinkConfig(label="Tags", url="/tags/")]
        inject_nav_links(tree, links, "after")
        assert tree.children[-1].label == "Tags"
        assert tree.children[0].label == "Alpha"

    def test_before_position(self):
        tree = self._make_tree()
        links = [NavLinkConfig(label="Tags", url="/tags/")]
        inject_nav_links(tree, links, "before")
        assert tree.children[0].label == "Tags"
        assert tree.children[1].label == "Alpha"

    def test_mixed_position(self):
        tree = self._make_tree()
        links = [NavLinkConfig(label="AAA Link", url="/aaa/")]
        inject_nav_links(tree, links, "mixed")
        assert tree.children[0].label == "AAA Link"
        assert tree.children[1].label == "Alpha"
        assert tree.children[2].label == "Beta"

    def test_empty_links_noop(self):
        tree = self._make_tree()
        original_children = list(tree.children)
        inject_nav_links(tree, [], "after")
        assert tree.children == original_children


class TestNavSortReverse:
    def test_reverse_unpinned_only(self):
        """Reverse should only affect unpinned items; pinned stay in order."""
        pages = [
            make_page("alpha"),
            make_page("beta"),
            make_page("gamma"),
            make_page("pinned", nav_order=1),
        ]
        config = NavConfig(sort="alphabetical", reverse=True)
        tree = build_nav_tree(pages, config)
        labels = [c.label for c in tree.children]
        assert labels == ["pinned", "gamma", "beta", "alpha"]

    def test_reverse_false_is_normal_order(self):
        pages = [make_page("alpha"), make_page("beta"), make_page("gamma")]
        config = NavConfig(sort="alphabetical", reverse=False)
        tree = build_nav_tree(pages, config)
        labels = [c.label for c in tree.children]
        assert labels == ["alpha", "beta", "gamma"]

    def test_date_strategy_falls_back_to_files_first(self):
        """Nav tree has no date field; date strategy should fall back."""
        pages = [
            make_page("alpha"),
            make_page("docs/index"),
        ]
        config = NavConfig(sort="date")
        tree = build_nav_tree(pages, config)
        # Should not error; falls back to files-first
        labels = [c.label for c in tree.children]
        assert "alpha" in labels


class TestNavPerFolderOverride:
    def test_config_override_applies_to_folder(self):
        pages = [
            make_page("blog/index", "Blog"),
            make_page("blog/alpha"),
            make_page("blog/beta"),
            make_page("blog/gamma"),
        ]
        config = NavConfig(
            sort="alphabetical",
            reverse=False,
            overrides={"blog": FolderSortOverride(reverse=True)},
        )
        tree = build_nav_tree(pages, config)
        blog_node = [c for c in tree.children if c.name == "blog"][0]
        labels = [c.label for c in blog_node.children]
        assert labels == ["gamma", "beta", "alpha"]

    def test_folder_meta_override_wins(self):
        """`_folder.md` sort/sort_reverse should override config."""
        pages = [
            make_page("blog/index", "Blog"),
            make_page("blog/alpha"),
            make_page("blog/beta"),
            make_page("blog/gamma"),
        ]
        metas = {
            "blog": make_meta("blog", sort="alphabetical", sort_reverse=True),
        }
        config = NavConfig(sort="alphabetical", reverse=False)
        tree = build_nav_tree(pages, config, folder_metas=metas)
        blog_node = [c for c in tree.children if c.name == "blog"][0]
        labels = [c.label for c in blog_node.children]
        assert labels == ["gamma", "beta", "alpha"]

    def test_root_not_affected_by_subfolder_override(self):
        pages = [
            make_page("alpha"),
            make_page("beta"),
            make_page("blog/post1"),
        ]
        config = NavConfig(
            sort="alphabetical",
            overrides={"blog": FolderSortOverride(reverse=True)},
        )
        tree = build_nav_tree(pages, config)
        root_labels = [c.label for c in tree.children if not c.is_folder]
        assert root_labels == ["alpha", "beta"]


class TestFolderNoteNav:
    """Test nav tree with folder note pages (slug rewritten to index)."""

    def test_folder_note_clickable_folder(self):
        """Folder note should make the folder node clickable."""
        pages = [
            Page(
                source_path=Path("/vault/locations/Fairshore/Fairshore.md"),
                slug="locations/fairshore/index",
                frontmatter={"title": "Fairshore"},
                content="",
            ),
            make_page("locations/fairshore/the-salty-dog", "The Salty Dog"),
        ]
        tree = build_nav_tree(pages)

        locations = tree.children[0]
        assert locations.is_folder
        fairshore = locations.children[0]
        assert fairshore.is_folder
        assert fairshore.index_path == "/locations/fairshore/"

    def test_folder_note_not_duplicate_child(self):
        """Folder note should not appear as a child of its own folder."""
        pages = [
            Page(
                source_path=Path("/vault/locations/Fairshore/Fairshore.md"),
                slug="locations/fairshore/index",
                frontmatter={"title": "Fairshore"},
                content="",
            ),
            make_page("locations/fairshore/the-salty-dog", "The Salty Dog"),
            make_page("locations/fairshore/market-square", "Market Square"),
        ]
        tree = build_nav_tree(pages)

        locations = tree.children[0]
        fairshore = locations.children[0]
        child_labels = [c.label for c in fairshore.children]
        assert "Fairshore" not in child_labels
        assert "The Salty Dog" in child_labels
        assert "Market Square" in child_labels


class TestUnlistedPages:
    """Test that unlisted frontmatter hides pages from nav."""

    def test_unlisted_page_hidden_from_nav(self):
        pages = [
            make_page("about", "About"),
            Page(
                source_path=Path("/vault/secret.md"),
                slug="secret",
                frontmatter={"title": "Secret", "unlisted": True},
                content="",
            ),
        ]
        tree = build_nav_tree(pages)
        labels = [c.label for c in tree.children]
        assert "About" in labels
        assert "Secret" not in labels

    def test_unlisted_page_folder_still_shown(self):
        pages = [
            Page(
                source_path=Path("/vault/docs/hidden.md"),
                slug="docs/hidden",
                frontmatter={"title": "Hidden", "unlisted": True},
                content="",
            ),
            make_page("docs/visible", "Visible"),
        ]
        tree = build_nav_tree(pages)
        docs = tree.children[0]
        assert docs.is_folder
        child_labels = [c.label for c in docs.children]
        assert "Visible" in child_labels
        assert "Hidden" not in child_labels

    def test_unlisted_false_still_shown(self):
        pages = [
            Page(
                source_path=Path("/vault/page.md"),
                slug="page",
                frontmatter={"title": "Page", "unlisted": False},
                content="",
            ),
        ]
        tree = build_nav_tree(pages)
        labels = [c.label for c in tree.children]
        assert "Page" in labels

    def test_unlisted_folder_meta_hides_folder(self):
        """Folder with unlisted=true in `_folder.md` should not appear in nav."""
        pages = [
            make_page("secret/index", "Secret"),
            make_page("secret/details", "Details"),
            make_page("public", "Public"),
        ]
        metas = {"secret": make_meta("secret", unlisted=True)}
        tree = build_nav_tree(pages, folder_metas=metas)
        labels = [c.label for c in tree.children]
        assert "Public" in labels
        assert "secret" not in [c.label.lower() for c in tree.children]
        assert "Details" not in labels

    def test_unlisted_index_page_renders_but_folder_visible(self):
        """Unlisted on index.md: folder still visible, but no nav link to it."""
        pages = [
            Page(
                source_path=Path("/vault/about/index.md"),
                slug="about/index",
                frontmatter={"title": "About", "unlisted": True},
                content="",
            ),
            make_page("about/team", "Team"),
        ]
        tree = build_nav_tree(pages)
        about = [c for c in tree.children if c.name == "about"]
        assert len(about) == 1
        # Folder present with children, but index_path is None because the
        # index page itself is unlisted.
        assert about[0].is_folder
        assert about[0].index_path is None
        assert "Team" in [c.label for c in about[0].children]

    def test_unlisted_folder_note_equivalent_to_unlisted_index(self):
        """Folder-note (attend/attend.md) with unlisted behaves like index.md."""
        pages = [
            Page(
                source_path=Path("/vault/attend/attend.md"),
                slug="attend/index",
                frontmatter={"title": "Attend", "unlisted": True},
                content="",
            ),
            make_page("attend/venue", "Venue"),
        ]
        tree = build_nav_tree(pages)
        attend = [c for c in tree.children if c.name == "attend"]
        assert len(attend) == 1
        assert attend[0].is_folder
        assert attend[0].index_path is None
        assert "Venue" in [c.label for c in attend[0].children]
