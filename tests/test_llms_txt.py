"""Tests for llms.txt generation."""

from pathlib import Path

from rockgarden.config import CollectionConfig, NavLinkConfig
from rockgarden.content.collection import Collection
from rockgarden.content.models import Page
from rockgarden.nav.folder_index import FolderIndex
from rockgarden.output.llms_txt import build_llms_full_txt, build_llms_txt


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

    def test_full_url_in_description(self):
        result = build_llms_txt(
            [],
            [],
            {},
            "https://example.com",
            "My Site",
            description="A cool site.",
            full_url="https://example.com/llms-full.txt",
        )
        assert "> A cool site." in result
        expected = "> Full content available at: https://example.com/llms-full.txt"
        assert expected in result

    def test_full_url_without_description(self):
        result = build_llms_txt(
            [],
            [],
            {},
            "https://example.com",
            "My Site",
            full_url="https://example.com/llms-full.txt",
        )
        expected = "> Full content available at: https://example.com/llms-full.txt"
        assert expected in result

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

    def test_path_in_base_url_not_doubled(self):
        # When the path is encoded in base_url and base_path is derived to
        # match (as builder.py does via get_base_path), the result must not
        # double up the path component.
        pages = [self._make_page("about", "About")]
        result = build_llms_txt(
            pages, [], {}, "https://example.com/docs", "My Site", base_path="/docs"
        )
        assert "https://example.com/docs/about/" in result
        assert "https://example.com/docs/docs/" not in result

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

    def test_nav_links_section(self):
        links = [
            NavLinkConfig(label="GitHub", url="https://github.com/example"),
            NavLinkConfig(label="Tags", url="/tags/"),
        ]
        result = build_llms_txt(
            [], [], {}, "https://example.com", "My Site", nav_links=links
        )
        assert "## Links" in result
        assert "- [GitHub](https://github.com/example)" in result
        assert "- [Tags](/tags/)" in result

    def test_nav_links_after_pages(self):
        links = [NavLinkConfig(label="GitHub", url="https://github.com/example")]
        pages = [self._make_page("about", "About")]
        result = build_llms_txt(
            pages, [], {}, "https://example.com", "My Site", nav_links=links
        )
        pages_pos = result.index("## Pages")
        links_pos = result.index("## Links")
        assert pages_pos < links_pos

    def test_nav_links_flattens_nested(self):
        links = [
            NavLinkConfig(
                label="Parent",
                url="",
                children=[
                    NavLinkConfig(label="Child", url="https://example.com/child"),
                ],
            ),
        ]
        result = build_llms_txt(
            [], [], {}, "https://example.com", "My Site", nav_links=links
        )
        assert "- [Child](https://example.com/child)" in result
        assert "Parent" not in result

    def test_no_nav_links_no_section(self):
        result = build_llms_txt(
            [], [], {}, "https://example.com", "My Site", nav_links=[]
        )
        assert "## Links" not in result

    def test_collection_folder_index_not_duplicated(self):
        page = self._make_page("blog/post1", "First Post", source_prefix="blog")
        folder = FolderIndex(slug="blog/index", title="Blog", children=[])
        col_config = CollectionConfig(name="Blog", source="blog")
        col = Collection(name="Blog", config=col_config, entries=[page])
        result = build_llms_txt(
            [page], [folder], {"blog": col}, "https://example.com", "My Site"
        )
        assert "## Blog" in result
        assert "## blog" not in result

    def test_trailing_newline(self):
        result = build_llms_txt(
            [self._make_page("about", "About")],
            [],
            {},
            "https://example.com",
            "My Site",
        )
        assert result.endswith("\n")


class TestBuildLlmsFullTxt:
    def _make_page(self, slug, title=None, html=None, source_prefix=""):
        source = f"{source_prefix}/{slug}.md" if source_prefix else f"{slug}.md"
        return Page(
            source_path=Path(source),
            slug=slug,
            frontmatter={"title": title} if title else {},
            html=html,
        )

    def test_title_heading(self):
        result = build_llms_full_txt([], [], {}, "https://example.com", "My Site")
        assert result.startswith("# My Site\n")

    def test_description_blockquote(self):
        result = build_llms_full_txt(
            [], [], {}, "https://example.com", "My Site", description="A cool site."
        )
        assert "> A cool site." in result

    def test_page_content_included(self):
        pages = [self._make_page("about", "About", html="<p>Hello world</p>")]
        result = build_llms_full_txt(pages, [], {}, "https://example.com", "My Site")
        assert "Hello world" in result

    def test_page_entry_has_source_url(self):
        pages = [self._make_page("about", "About", html="<p>Content</p>")]
        result = build_llms_full_txt(pages, [], {}, "https://example.com", "My Site")
        assert "Source: https://example.com/about/" in result

    def test_page_entry_has_title_heading(self):
        pages = [self._make_page("about", "About", html="<p>Content</p>")]
        result = build_llms_full_txt(pages, [], {}, "https://example.com", "My Site")
        assert "### About" in result

    def test_separator_between_entries(self):
        pages = [
            self._make_page("about", "About", html="<p>About page</p>"),
            self._make_page("contact", "Contact", html="<p>Contact page</p>"),
        ]
        result = build_llms_full_txt(pages, [], {}, "https://example.com", "My Site")
        assert "\n---\n" in result

    def test_page_without_html(self):
        pages = [self._make_page("about", "About")]
        result = build_llms_full_txt(pages, [], {}, "https://example.com", "My Site")
        assert "### About" in result
        assert "Source: https://example.com/about/" in result

    def test_collection_pages(self):
        page = self._make_page(
            "blog/post1", "First Post", html="<p>Post content</p>", source_prefix="blog"
        )
        col_config = CollectionConfig(name="Blog", source="blog")
        col = Collection(name="Blog", config=col_config, entries=[page])
        result = build_llms_full_txt(
            [page], [], {"blog": col}, "https://example.com", "My Site"
        )
        assert "## Blog" in result
        assert "### First Post" in result
        assert "Post content" in result

    def test_folder_index_content(self):
        folder = FolderIndex(
            slug="docs/index",
            title="Docs",
            children=[],
            custom_content="<p>Welcome to docs</p>",
        )
        result = build_llms_full_txt([], [folder], {}, "https://example.com", "My Site")
        assert "### Docs" in result
        assert "Welcome to docs" in result

    def test_folder_index_no_content(self):
        folder = FolderIndex(slug="docs/index", title="Docs", children=[])
        result = build_llms_full_txt([], [folder], {}, "https://example.com", "My Site")
        assert "### Docs" in result
        assert "Source: https://example.com/docs/" in result

    def test_nav_links_are_link_only(self):
        links = [
            NavLinkConfig(label="GitHub", url="https://github.com/example"),
        ]
        result = build_llms_full_txt(
            [], [], {}, "https://example.com", "My Site", nav_links=links
        )
        assert "## Links" in result
        assert "- [GitHub](https://github.com/example)" in result

    def test_section_ordering(self):
        page_col = self._make_page(
            "blog/post", "Post", html="<p>Blog</p>", source_prefix="blog"
        )
        page_dir = self._make_page("docs/guide", "Guide", html="<p>Guide</p>")
        col_config = CollectionConfig(name="Blog", source="blog")
        col = Collection(name="Blog", config=col_config, entries=[page_col])
        links = [NavLinkConfig(label="GitHub", url="https://github.com")]
        result = build_llms_full_txt(
            [page_col, page_dir],
            [],
            {"blog": col},
            "https://example.com",
            "My Site",
            nav_links=links,
        )
        blog_pos = result.index("## Blog")
        docs_pos = result.index("## docs")
        links_pos = result.index("## Links")
        assert blog_pos < docs_pos < links_pos

    def test_trailing_newline(self):
        pages = [self._make_page("about", "About", html="<p>Content</p>")]
        result = build_llms_full_txt(pages, [], {}, "https://example.com", "My Site")
        assert result.endswith("\n")

    def test_content_headings_nested_under_page(self):
        pages = [
            self._make_page(
                "about", "About", html="<h2>Section</h2><p>Text</p><h3>Sub</h3>"
            )
        ]
        result = build_llms_full_txt(pages, [], {}, "https://example.com", "My Site")
        assert "#### Section" in result
        assert "##### Sub" in result
        assert "\n## Pages\n" in result
        assert "\n### About\n" in result

    def test_empty_site(self):
        result = build_llms_full_txt([], [], {}, "https://example.com", "My Site")
        assert result == "# My Site\n"
