"""Tests for URL and path generation utilities."""

import pytest

from rockgarden.config import Config, SiteConfig
from rockgarden.output.builder import build_site
from rockgarden.urls import (
    generate_slug,
    get_base_path,
    get_folder_url,
    get_host_url,
    get_output_path,
    get_url,
)


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

    def test_consecutive_dashes_collapsed(self):
        """Dashes from spaces around hyphens are collapsed."""
        assert generate_slug("Session 42 - Title.md") == "session-42-title"

    def test_existing_consecutive_dashes_collapsed(self):
        """Pre-existing consecutive dashes in filenames are collapsed."""
        assert generate_slug("foo--bar.md") == "foo-bar"


class TestGenerateSlugPreserve:
    def test_preserves_casing(self):
        """Preserve style keeps original casing."""
        assert generate_slug("About.md", style="preserve") == "About"

    def test_preserves_spaces(self):
        """Preserve style keeps spaces."""
        result = generate_slug("Getting Started.md", style="preserve")
        assert result == "Getting Started"

    def test_preserves_special_characters(self):
        """Preserve style keeps dashes and other characters."""
        result = generate_slug("Session 42 - Title.md", style="preserve")
        assert result == "Session 42 - Title"

    def test_preserves_nested_path_casing(self):
        """Preserve style keeps directory casing."""
        result = generate_slug("NPCs/Olvir the Wise.md", style="preserve")
        assert result == "NPCs/Olvir the Wise"

    def test_preserves_underscores(self):
        """Preserve style keeps underscores as-is."""
        result = generate_slug("my_file_name.md", style="preserve")
        assert result == "my_file_name"

    def test_index_file(self):
        """Preserve style handles index files."""
        result = generate_slug("Folder/index.md", style="preserve")
        assert result == "Folder/index"


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


class TestGetUrlEncoding:
    def test_spaces_encoded_clean_urls(self):
        """Spaces in slugs are percent-encoded in URLs."""
        result = get_url("Session 42 - Title", clean_urls=True)
        assert result == "/Session%2042%20-%20Title/"

    def test_spaces_encoded_no_clean_urls(self):
        """Spaces encoded in non-clean URLs."""
        result = get_url("Session 42 - Title", clean_urls=False)
        assert result == "/Session%2042%20-%20Title.html"

    def test_nested_spaces_encoded(self):
        """Spaces encoded in nested paths."""
        result = get_url("NPCs/Olvir the Wise", clean_urls=True)
        assert result == "/NPCs/Olvir%20the%20Wise/"

    def test_kebab_slug_unchanged(self):
        """Kebab slugs are not affected by encoding."""
        assert get_url("getting-started", clean_urls=True) == "/getting-started/"

    def test_output_path_not_encoded(self):
        """Filesystem output paths preserve spaces (no encoding)."""
        result = get_output_path("Session 42 - Title", clean_urls=True)
        assert result == "Session 42 - Title/index.html"

    def test_folder_url_spaces_encoded(self):
        """Folder URLs encode spaces."""
        result = get_folder_url("My Folder", clean_urls=True)
        assert result == "/My%20Folder/"


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


class TestBasePath:
    """Tests for base_path config field and its interaction with base_url."""

    def test_base_path_config_field(self):
        """base_path can be set directly in site config."""
        site = SiteConfig(base_path="/docs")
        assert site.base_path == "/docs"

    def test_base_path_strips_trailing_slash(self):
        """Trailing slash is stripped from base_path."""
        site = SiteConfig(base_path="/docs/")
        assert site.base_path == "/docs"

    def test_base_path_adds_leading_slash(self):
        """Leading slash is added if missing from base_path."""
        site = SiteConfig(base_path="docs")
        assert site.base_path == "/docs"

    def test_base_path_takes_precedence_over_base_url(self):
        """When both are set, base_path is used directly for URL prefixing."""
        site = SiteConfig(base_path="/preview", base_url="https://example.com/docs")
        # base_path is used directly, not derived from base_url
        assert site.base_path == "/preview"

    def test_base_url_derives_base_path(self):
        """When only base_url is set, base_path is derived from it."""
        base_path = get_base_path("https://example.com/docs")
        assert base_path == "/docs"

    def test_base_path_default_empty(self):
        """base_path defaults to empty string."""
        site = SiteConfig()
        assert site.base_path == ""


class TestHostUrl:
    """Tests for get_host_url, used to avoid double-path bugs in absolute URLs."""

    def test_strips_path_component(self):
        assert get_host_url("https://example.com/docs") == "https://example.com"

    def test_strips_trailing_slash_with_path(self):
        assert get_host_url("https://example.com/docs/") == "https://example.com"

    def test_no_path_unchanged(self):
        assert get_host_url("https://example.com") == "https://example.com"

    def test_trailing_slash_only(self):
        assert get_host_url("https://example.com/") == "https://example.com"

    def test_empty_returns_empty(self):
        assert get_host_url("") == ""

    def test_preserves_port(self):
        assert get_host_url("http://localhost:8000/site") == "http://localhost:8000"

    def test_preserves_scheme(self):
        assert get_host_url("http://example.com/docs") == "http://example.com"

    def test_base_path_in_build_output(self, tmp_path):
        """base_path is applied to asset and navigation URLs in built HTML."""
        source = tmp_path / "source"
        source.mkdir()
        (source / "index.md").write_text("# Home\nHello")

        output = tmp_path / "output"
        config = Config(site=SiteConfig(base_path="/2026preview"))

        build_site(config, source, output)

        html = (output / "index.html").read_text()
        assert "/2026preview/_assets/rockgarden.css" in html
        assert "/2026preview/" in html

    def test_base_url_derived_path_in_build_output(self, tmp_path):
        """base_url-derived path is applied when base_path is not set."""
        source = tmp_path / "source"
        source.mkdir()
        (source / "index.md").write_text("# Home\nHello")

        output = tmp_path / "output"
        config = Config(site=SiteConfig(base_url="https://example.com/mysite"))

        build_site(config, source, output)

        html = (output / "index.html").read_text()
        assert "/mysite/_assets/rockgarden.css" in html

    def test_no_base_path_or_base_url_in_build_output(self, tmp_path):
        """Without base_path or base_url, URLs start from root."""
        source = tmp_path / "source"
        source.mkdir()
        (source / "index.md").write_text("# Home\nHello")

        output = tmp_path / "output"
        config = Config()

        build_site(config, source, output)

        html = (output / "index.html").read_text()
        assert '"/_assets/rockgarden.css' in html

    def test_base_path_precedence_in_build_output(self, tmp_path):
        """base_path takes precedence over base_url for URL prefixing."""
        source = tmp_path / "source"
        source.mkdir()
        (source / "index.md").write_text("# Home\nHello")

        output = tmp_path / "output"
        config = Config(
            site=SiteConfig(
                base_path="/preview",
                base_url="https://example.com/production",
            )
        )

        build_site(config, source, output)

        html = (output / "index.html").read_text()
        assert "/preview/_assets/rockgarden.css" in html
        assert "/production/_assets/" not in html

    def test_base_path_rejects_single_quote(self):
        with pytest.raises(ValueError, match="invalid URL path characters"):
            SiteConfig(base_path="/my's-blog")

    def test_base_path_rejects_angle_bracket(self):
        with pytest.raises(ValueError, match="invalid URL path characters"):
            SiteConfig(base_path="/bad<path")

    def test_base_path_rejects_spaces(self):
        with pytest.raises(ValueError, match="invalid URL path characters"):
            SiteConfig(base_path="/my path")

    def test_base_path_rejects_double_slash(self):
        with pytest.raises(ValueError, match="invalid URL path characters"):
            SiteConfig(base_path="//evil")

    def test_base_path_allows_valid_characters(self):
        site = SiteConfig(base_path="/my-site_v2.0")
        assert site.base_path == "/my-site_v2.0"


class TestGenerateSlugPreserveCase:
    def test_keeps_casing_replaces_spaces(self):
        """Preserve-case keeps casing but replaces spaces with dashes."""
        result = generate_slug("Getting Started.md", style="preserve-case")
        assert result == "Getting-Started"

    def test_nested_path(self):
        """Preserve-case keeps directory casing."""
        result = generate_slug("NPCs/Olvir the Wise.md", style="preserve-case")
        assert result == "NPCs/Olvir-the-Wise"

    def test_collapses_consecutive_dashes(self):
        """Preserve-case collapses consecutive dashes."""
        result = generate_slug("Session 42 - Title.md", style="preserve-case")
        assert result == "Session-42-Title"

    def test_underscores_to_dashes(self):
        """Preserve-case replaces underscores with dashes."""
        result = generate_slug("my_file_name.md", style="preserve-case")
        assert result == "my-file-name"

    def test_index_file(self):
        """Preserve-case handles index files."""
        result = generate_slug("Folder/index.md", style="preserve-case")
        assert result == "Folder/index"


class TestSlugStyleConfig:
    def test_default_is_slug(self):
        """url_style defaults to slug."""
        site = SiteConfig()
        assert site.url_style == "slug"

    def test_preserve_case_accepted(self):
        """url_style accepts 'preserve-case'."""
        site = SiteConfig(url_style="preserve-case")
        assert site.url_style == "preserve-case"

    def test_preserve_accepted(self):
        """url_style accepts 'preserve'."""
        site = SiteConfig(url_style="preserve")
        assert site.url_style == "preserve"

    def test_invalid_url_style_rejected(self):
        """Unknown url_style raises validation error."""
        with pytest.raises(Exception, match="url_style"):
            SiteConfig(url_style="camelCase")

    def test_preserve_build_output(self, tmp_path):
        """Preserve url_style keeps original filenames in output paths."""
        source = tmp_path / "source"
        source.mkdir()
        (source / "index.md").write_text("# Home")
        (source / "Getting Started.md").write_text("# Getting Started")

        output = tmp_path / "output"
        config = Config(site=SiteConfig(url_style="preserve"))

        build_site(config, source, output)

        assert (output / "Getting Started" / "index.html").exists()

        html = (output / "index.html").read_text()
        assert "/Getting%20Started/" in html

    def test_preserve_case_build_output(self, tmp_path):
        """Preserve-case url_style keeps casing but dashes spaces."""
        source = tmp_path / "source"
        source.mkdir()
        (source / "index.md").write_text("# Home")
        (source / "Getting Started.md").write_text("# Getting Started")

        output = tmp_path / "output"
        config = Config(site=SiteConfig(url_style="preserve-case"))

        build_site(config, source, output)

        assert (output / "Getting-Started" / "index.html").exists()

        html = (output / "index.html").read_text()
        assert "/Getting-Started/" in html


class TestGenerateSlugAscii:
    def test_accented_latin(self):
        assert generate_slug("Café.md", ascii_urls=True) == "cafe"

    def test_cjk(self):
        assert generate_slug("東京.md", ascii_urls=True) == "dong-jing"

    def test_cyrillic(self):
        assert generate_slug("Москва.md", ascii_urls=True) == "moskva"

    def test_nested_path(self):
        assert generate_slug("Cities/Zürich.md", ascii_urls=True) == "cities/zurich"

    def test_plain_ascii_unaffected(self):
        assert generate_slug("about.md", ascii_urls=True) == "about"

    def test_preserve_case_with_ascii(self):
        result = generate_slug("Café.md", style="preserve-case", ascii_urls=True)
        assert result == "Cafe"

    def test_preserve_with_ascii(self):
        result = generate_slug("Café Latte.md", style="preserve", ascii_urls=True)
        assert result == "Cafe Latte"

    def test_ascii_false_preserves_unicode(self):
        assert generate_slug("Café.md", ascii_urls=False) == "café"


class TestNormalizeTagUnicode:
    """Tests for the bug fix: Unicode preserved when ascii_urls=False."""

    def test_accented_preserved(self):
        from rockgarden.urls import normalize_tag

        assert normalize_tag("#Café") == "café"

    def test_cjk_preserved(self):
        from rockgarden.urls import normalize_tag

        result = normalize_tag("#東京")
        assert result == "東京"

    def test_basic_tag_unchanged(self):
        from rockgarden.urls import normalize_tag

        assert normalize_tag("#python") == "python"

    def test_nested_tag(self):
        from rockgarden.urls import normalize_tag

        assert normalize_tag("character/pc") == "character-pc"


class TestNormalizeTagAscii:
    def test_accented_transliterated(self):
        from rockgarden.urls import normalize_tag

        assert normalize_tag("#Café", ascii_urls=True) == "cafe"

    def test_cjk_transliterated(self):
        from rockgarden.urls import normalize_tag

        assert normalize_tag("#東京", ascii_urls=True) == "dong-jing"

    def test_cyrillic_transliterated(self):
        from rockgarden.urls import normalize_tag

        assert normalize_tag("#Москва", ascii_urls=True) == "moskva"

    def test_basic_tag_unchanged(self):
        from rockgarden.urls import normalize_tag

        assert normalize_tag("#python", ascii_urls=True) == "python"


class TestAsciiUrlsConfig:
    def test_default_false(self):
        assert SiteConfig().ascii_urls is False

    def test_set_true(self):
        assert SiteConfig(ascii_urls=True).ascii_urls is True
