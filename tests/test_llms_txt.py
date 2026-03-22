"""Tests for llms.txt generation."""

from pathlib import Path

from rockgarden.config import CollectionConfig
from rockgarden.content.collection import Collection
from rockgarden.content.models import Page
from rockgarden.nav.folder_index import FolderIndex
from rockgarden.output.llms_txt import build_llms_txt


class TestBuildLlmsTxt:
    def _make_page(self, slug, title=None, source_prefix=""):
        source = f"{source_prefix}/{slug}.md" if source_prefix else f"{slug}.md"
        return Page(
            source_path=Path(source),
            slug=slug,
            frontmatter={"title": title} if title else {},
        )

    def test_title_heading(self):
        result = build_llms_txt([], [], {}, "https://example.com", "My Site")
        assert result.startswith("# My Site\n")

    def test_description_blockquote(self):
        result = build_llms_txt(
            [], [], {}, "https://example.com", "My Site", description="A cool site."
        )
        assert "> A cool site." in result

    def test_no_description(self):
        result = build_llms_txt([], [], {}, "https://example.com", "My Site")
        assert ">" not in result

    def test_root_pages_under_pages_heading(self):
        pages = [self._make_page("about", "About")]
        result = build_llms_txt(pages, [], {}, "https://example.com", "My Site")
        assert "## Pages" in result
        assert "- [About](https://example.com/about/)" in result

    def test_pages_grouped_by_directory(self):
        pages = [
            self._make_page("docs/intro", "Introduction"),
            self._make_page("docs/setup", "Setup"),
        ]
        result = build_llms_txt(pages, [], {}, "https://example.com", "My Site")
        assert "## docs" in result
        assert "- [Introduction](https://example.com/docs/intro/)" in result
        assert "- [Setup](https://example.com/docs/setup/)" in result
        assert "## Pages" not in result

    def test_collection_pages_grouped_separately(self):
        page = self._make_page("blog/post1", "First Post", source_prefix="blog")
        col_config = CollectionConfig(name="Blog", source="blog")
        col = Collection(name="Blog", config=col_config, entries=[page])
        result = build_llms_txt(
            [page], [], {"blog": col}, "https://example.com", "My Site"
        )
        assert "## Blog" in result
        assert "- [First Post](https://example.com/blog/post1/)" in result
        # Should not also appear under directory grouping
        lines = result.split("\n")
        assert lines.count("## Blog") == 1
        assert "## blog" not in result

    def test_folder_indexes_included(self):
        folders = [FolderIndex(slug="docs/index", title="Docs", children=[])]
        result = build_llms_txt([], folders, {}, "https://example.com", "My Site")
        assert "## docs" in result
        assert "- [Docs](https://example.com/docs/)" in result

    def test_clean_urls_false(self):
        pages = [self._make_page("about", "About")]
        result = build_llms_txt(
            pages, [], {}, "https://example.com", "My Site", clean_urls=False
        )
        assert "https://example.com/about.html" in result

    def test_base_path(self):
        pages = [self._make_page("about", "About")]
        result = build_llms_txt(
            pages, [], {}, "https://example.com", "My Site", base_path="/docs"
        )
        assert "https://example.com/docs/about/" in result

    def test_alphabetical_ordering(self):
        pages = [
            self._make_page("zebra", "Zebra"),
            self._make_page("apple", "Apple"),
        ]
        result = build_llms_txt(pages, [], {}, "https://example.com", "My Site")
        apple_pos = result.index("Apple")
        zebra_pos = result.index("Zebra")
        assert apple_pos < zebra_pos

    def test_collections_before_directories(self):
        page_col = self._make_page("blog/post", "Post", source_prefix="blog")
        page_dir = self._make_page("docs/guide", "Guide")
        col_config = CollectionConfig(name="Blog", source="blog")
        col = Collection(name="Blog", config=col_config, entries=[page_col])
        result = build_llms_txt(
            [page_col, page_dir],
            [],
            {"blog": col},
            "https://example.com",
            "My Site",
        )
        blog_pos = result.index("## Blog")
        docs_pos = result.index("## docs")
        assert blog_pos < docs_pos

    def test_empty_site(self):
        result = build_llms_txt([], [], {}, "https://example.com", "My Site")
        assert result == "# My Site\n"

    def test_trailing_newline(self):
        result = build_llms_txt(
            [self._make_page("about", "About")],
            [],
            {},
            "https://example.com",
            "My Site",
        )
        assert result.endswith("\n")
