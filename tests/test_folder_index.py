"""Tests for folder index generation."""

from pathlib import Path

from rockgarden.config import FolderSortOverride, NavConfig
from rockgarden.content import Page
from rockgarden.nav.folder_index import (
    find_folders,
    generate_folder_indexes,
)


def make_page(
    slug: str, title: str | None = None, content: str = "", **frontmatter
) -> Page:
    frontmatter_dict = dict(frontmatter)
    if title:
        frontmatter_dict["title"] = title
    return Page(
        source_path=Path(f"/vault/{slug}.md"),
        slug=slug,
        frontmatter=frontmatter_dict,
        content=content,
    )


class TestFindFolders:
    def test_empty_pages(self):
        assert find_folders([]) == set()

    def test_root_included(self):
        pages = [make_page("about")]
        assert "" in find_folders(pages)

    def test_root_and_subfolders(self):
        pages = [make_page("about"), make_page("blog/post")]
        folders = find_folders(pages)
        assert folders == {"", "blog"}

    def test_nested_folders(self):
        pages = [make_page("a/b/c/deep")]
        folders = find_folders(pages)
        assert folders == {"", "a", "a/b", "a/b/c"}


class TestGenerateFolderIndexes:
    def test_root_index_generated(self):
        pages = [make_page("about", "About"), make_page("contact", "Contact")]
        indexes = generate_folder_indexes(pages)
        slugs = [fi.slug for fi in indexes]
        assert "index" in slugs

    def test_root_title_from_site_title(self):
        pages = [make_page("about")]
        indexes = generate_folder_indexes(pages, site_title="My Site")
        root = next(fi for fi in indexes if fi.slug == "index")
        assert root.title == "My Site"

    def test_root_title_fallback(self):
        pages = [make_page("about")]
        indexes = generate_folder_indexes(pages)
        root = next(fi for fi in indexes if fi.slug == "index")
        assert root.title == "Home"

    def test_root_title_from_label_config(self):
        pages = [make_page("about")]
        config = NavConfig(labels={"/": "Welcome"})
        indexes = generate_folder_indexes(pages, config=config, site_title="My Site")
        root = next(fi for fi in indexes if fi.slug == "index")
        assert root.title == "Welcome"

    def test_root_children(self):
        pages = [
            make_page("about", "About"),
            make_page("blog/post", "A Post"),
        ]
        indexes = generate_folder_indexes(pages, site_title="Home")
        root = next(fi for fi in indexes if fi.slug == "index")
        titles = {c.title for c in root.children}
        assert "About" in titles
        assert "blog" in titles

    def test_root_children_excludes_index_page(self):
        pages = [
            make_page("index", "Home Page"),
            make_page("about", "About"),
        ]
        indexes = generate_folder_indexes(pages, site_title="My Site")
        root = next(fi for fi in indexes if fi.slug == "index")
        child_titles = {c.title for c in root.children}
        assert "About" in child_titles
        assert "Home Page" not in child_titles

    def test_root_custom_index(self):
        pages = [
            make_page("index", "Welcome Home", content="# Hello"),
            make_page("about", "About"),
        ]
        indexes = generate_folder_indexes(pages, site_title="My Site")
        root = next(fi for fi in indexes if fi.slug == "index")
        assert root.title == "Welcome Home"
        assert root.custom_content == "# Hello"

    def test_subfolder_still_works(self):
        pages = [
            make_page("about", "About"),
            make_page("blog/one", "One"),
            make_page("blog/two", "Two"),
        ]
        indexes = generate_folder_indexes(pages, site_title="My Site")
        slugs = {fi.slug for fi in indexes}
        assert "index" in slugs
        assert "blog/index" in slugs
        blog = next(fi for fi in indexes if fi.slug == "blog/index")
        child_titles = {c.title for c in blog.children}
        assert child_titles == {"One", "Two"}


class TestFolderIndexSortReverse:
    def test_reverse_alphabetical(self):
        pages = [
            make_page("blog/alpha", "Alpha"),
            make_page("blog/beta", "Beta"),
            make_page("blog/gamma", "Gamma"),
        ]
        config = NavConfig(sort="alphabetical", reverse=True)
        indexes = generate_folder_indexes(pages, config)
        blog = next(fi for fi in indexes if fi.slug == "blog/index")
        titles = [c.title for c in blog.children]
        assert titles == ["Gamma", "Beta", "Alpha"]

    def test_reverse_preserves_pinned_order(self):
        pages = [
            make_page("blog/alpha", "Alpha"),
            make_page("blog/beta", "Beta"),
            make_page("blog/pinned", "Pinned", nav_order=1),
        ]
        config = NavConfig(sort="alphabetical", reverse=True)
        indexes = generate_folder_indexes(pages, config)
        blog = next(fi for fi in indexes if fi.slug == "blog/index")
        titles = [c.title for c in blog.children]
        assert titles[0] == "Pinned"
        assert titles[1:] == ["Beta", "Alpha"]


class TestFolderIndexDateSort:
    def _make_page_with_mtime(self, slug, title, tmp_path, mtime_offset=0):
        """Create a page with a real file so mtime is available."""
        import time

        file_path = tmp_path / f"{slug}.md"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(f"# {title}")
        import os

        target_time = time.time() + mtime_offset
        os.utime(file_path, (target_time, target_time))
        return Page(
            source_path=file_path,
            slug=slug,
            frontmatter={"title": title},
            content=f"# {title}",
        )

    def test_date_sort_ascending(self, tmp_path):
        pages = [
            self._make_page_with_mtime("blog/newest", "Newest", tmp_path, 100),
            self._make_page_with_mtime("blog/oldest", "Oldest", tmp_path, -100),
            self._make_page_with_mtime("blog/middle", "Middle", tmp_path, 0),
        ]
        config = NavConfig(sort="date")
        indexes = generate_folder_indexes(pages, config)
        blog = next(fi for fi in indexes if fi.slug == "blog/index")
        titles = [c.title for c in blog.children]
        assert titles == ["Oldest", "Middle", "Newest"]

    def test_date_sort_reverse_newest_first(self, tmp_path):
        pages = [
            self._make_page_with_mtime("blog/newest", "Newest", tmp_path, 100),
            self._make_page_with_mtime("blog/oldest", "Oldest", tmp_path, -100),
            self._make_page_with_mtime("blog/middle", "Middle", tmp_path, 0),
        ]
        config = NavConfig(sort="date", reverse=True)
        indexes = generate_folder_indexes(pages, config)
        blog = next(fi for fi in indexes if fi.slug == "blog/index")
        titles = [c.title for c in blog.children]
        assert titles == ["Newest", "Middle", "Oldest"]


class TestFolderIndexPerFolderOverride:
    def test_config_override(self):
        pages = [
            make_page("blog/gamma", "Gamma"),
            make_page("blog/alpha", "Alpha"),
            make_page("blog/beta", "Beta"),
            make_page("docs/one", "One"),
            make_page("docs/two", "Two"),
        ]
        config = NavConfig(
            sort="alphabetical",
            overrides={"blog": FolderSortOverride(reverse=True)},
        )
        indexes = generate_folder_indexes(pages, config)
        blog = next(fi for fi in indexes if fi.slug == "blog/index")
        blog_titles = [c.title for c in blog.children]
        assert blog_titles == ["Gamma", "Beta", "Alpha"]

        docs = next(fi for fi in indexes if fi.slug == "docs/index")
        docs_titles = [c.title for c in docs.children]
        assert docs_titles == ["One", "Two"]

    def test_frontmatter_override_wins(self):
        pages = [
            Page(
                source_path=Path("/vault/blog/index.md"),
                slug="blog/index",
                frontmatter={"sort": "alphabetical", "sort_reverse": True},
                content="",
            ),
            make_page("blog/alpha", "Alpha"),
            make_page("blog/beta", "Beta"),
            make_page("blog/gamma", "Gamma"),
        ]
        config = NavConfig(
            sort="alphabetical",
            reverse=False,
            overrides={"blog": FolderSortOverride(reverse=False)},
        )
        indexes = generate_folder_indexes(pages, config)
        blog = next(fi for fi in indexes if fi.slug == "blog/index")
        titles = [c.title for c in blog.children]
        assert titles == ["Gamma", "Beta", "Alpha"]
