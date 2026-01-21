"""Tests for URL and path generation utilities."""

from rockgarden.urls import generate_slug, get_folder_url, get_output_path, get_url


class TestGenerateSlug:
    def test_simple_filename(self):
        """Simple filename becomes lowercase slug."""
        assert generate_slug("about.md") == "about"

    def test_uppercase_filename(self):
        """Uppercase filename becomes lowercase."""
        assert generate_slug("About.md") == "about"

    def test_spaces_to_dashes(self):
        """Spaces become dashes."""
        assert generate_slug("Getting Started.md") == "getting-started"

    def test_underscores_to_dashes(self):
        """Underscores become dashes."""
        assert generate_slug("getting_started.md") == "getting-started"

    def test_mixed_spaces_underscores(self):
        """Mixed spaces and underscores normalize to dashes."""
        assert generate_slug("my_file name.md") == "my-file-name"

    def test_multiple_spaces(self):
        """Multiple consecutive spaces become single dash."""
        assert generate_slug("Getting  Started.md") == "getting-started"

    def test_nested_path(self):
        """Nested paths preserve directory structure."""
        assert generate_slug("NPCs/Olvir.md") == "npcs/olvir"

    def test_nested_path_with_spaces(self):
        """Nested paths with spaces are normalized."""
        assert generate_slug("NPCs/Olvir the Wise.md") == "npcs/olvir-the-wise"

    def test_deeply_nested(self):
        """Deeply nested paths work correctly."""
        assert generate_slug("a/b/c/page.md") == "a/b/c/page"

    def test_index_file(self):
        """Index files preserve 'index' name."""
        assert generate_slug("folder/index.md") == "folder/index"

    def test_root_index(self):
        """Root index file."""
        assert generate_slug("index.md") == "index"

    def test_case_insensitive_extension(self):
        """Extension removal is case-insensitive."""
        assert generate_slug("about.MD") == "about"


class TestGetOutputPath:
    def test_clean_urls_regular_page(self):
        """Regular page with clean URLs uses directory."""
        assert get_output_path("about", clean_urls=True) == "about/index.html"

    def test_clean_urls_nested_page(self):
        """Nested page with clean URLs uses directory."""
        result = get_output_path("docs/getting-started", clean_urls=True)
        assert result == "docs/getting-started/index.html"

    def test_no_clean_urls_regular_page(self):
        """Regular page without clean URLs uses .html."""
        assert get_output_path("about", clean_urls=False) == "about.html"

    def test_no_clean_urls_nested_page(self):
        """Nested page without clean URLs uses .html."""
        result = get_output_path("docs/getting-started", clean_urls=False)
        assert result == "docs/getting-started.html"

    def test_index_page_clean_urls(self):
        """Index pages always use index.html regardless of clean_urls."""
        assert get_output_path("docs/index", clean_urls=True) == "docs/index.html"

    def test_index_page_no_clean_urls(self):
        """Index pages always use index.html."""
        assert get_output_path("docs/index", clean_urls=False) == "docs/index.html"

    def test_root_index(self):
        """Root index page."""
        assert get_output_path("index", clean_urls=True) == "index.html"


class TestGetUrl:
    def test_clean_urls_regular_page(self):
        """Regular page with clean URLs uses trailing slash."""
        assert get_url("about", clean_urls=True) == "/about/"

    def test_clean_urls_nested_page(self):
        """Nested page with clean URLs uses trailing slash."""
        result = get_url("docs/getting-started", clean_urls=True)
        assert result == "/docs/getting-started/"

    def test_no_clean_urls_regular_page(self):
        """Regular page without clean URLs uses .html."""
        assert get_url("about", clean_urls=False) == "/about.html"

    def test_no_clean_urls_nested_page(self):
        """Nested page without clean URLs uses .html."""
        result = get_url("docs/getting-started", clean_urls=False)
        assert result == "/docs/getting-started.html"

    def test_index_page_clean_urls(self):
        """Index page URL points to folder."""
        assert get_url("docs/index", clean_urls=True) == "/docs/"

    def test_index_page_no_clean_urls(self):
        """Index page URL still points to folder for consistency."""
        assert get_url("docs/index", clean_urls=False) == "/docs/"

    def test_root_index_clean_urls(self):
        """Root index points to /."""
        assert get_url("index", clean_urls=True) == "/"

    def test_root_index_no_clean_urls(self):
        """Root index points to / even without clean_urls."""
        assert get_url("index", clean_urls=False) == "/"


class TestGetFolderUrl:
    def test_clean_urls(self):
        """Folder with clean URLs uses trailing slash."""
        assert get_folder_url("examples", clean_urls=True) == "/examples/"

    def test_no_clean_urls(self):
        """Folder without clean URLs uses index.html."""
        assert get_folder_url("examples", clean_urls=False) == "/examples/index.html"

    def test_nested_folder_clean_urls(self):
        """Nested folder with clean URLs."""
        assert get_folder_url("docs/api", clean_urls=True) == "/docs/api/"

    def test_nested_folder_no_clean_urls(self):
        """Nested folder without clean URLs."""
        assert get_folder_url("docs/api", clean_urls=False) == "/docs/api/index.html"

    def test_root_folder_clean_urls(self):
        """Root folder with clean URLs."""
        assert get_folder_url("", clean_urls=True) == "/"

    def test_root_folder_no_clean_urls(self):
        """Root folder without clean URLs."""
        assert get_folder_url("", clean_urls=False) == "/index.html"
