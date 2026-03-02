"""Tests for stripping H1 from content."""

from rockgarden.config import Config
from rockgarden.content import strip_content_title
from rockgarden.output.builder import build_site


class TestStripContentTitle:
    def test_strips_h1(self):
        """H1 at start of content is stripped."""
        content = "# My Title\n\nSome content here."
        result = strip_content_title(content)
        assert result == "\nSome content here."

    def test_strips_h1_with_leading_whitespace(self):
        """H1 with leading blank lines is stripped."""
        content = "\n\n# My Title\n\nSome content."
        result = strip_content_title(content)
        assert result == "\nSome content."

    def test_preserves_h2(self):
        """H2 is not stripped."""
        content = "## Not H1\n\nContent."
        result = strip_content_title(content)
        assert result == "## Not H1\n\nContent."

    def test_preserves_later_h1(self):
        """H1 not at start is preserved."""
        content = "Some intro.\n\n# Later H1\n\nMore content."
        result = strip_content_title(content)
        assert result == "Some intro.\n\n# Later H1\n\nMore content."

    def test_no_h1(self):
        """Content without H1 is unchanged."""
        content = "Just some content.\n\nMore text."
        result = strip_content_title(content)
        assert result == "Just some content.\n\nMore text."

    def test_empty_content(self):
        """Empty content returns empty."""
        assert strip_content_title("") == ""

    def test_only_h1(self):
        """Content that is only H1 returns empty."""
        content = "# Just a Title"
        result = strip_content_title(content)
        assert result == ""


class TestBuildSiteStripTitle:
    """Test that build_site strips H1 from page output."""

    def test_strips_h1_when_title_in_frontmatter(self, tmp_path):
        """H1 should not appear twice when title is set in frontmatter."""
        source = tmp_path / "source"
        source.mkdir()
        (source / "page.md").write_text(
            "---\ntitle: My Page\n---\n\n# My Page\n\nSome content."
        )

        output = tmp_path / "output"
        build_site(Config.load(None), source, output)

        html = (output / "page" / "index.html").read_text()
        assert html.count("<h1") == 1

    def test_strips_h1_when_title_derived_from_filename(self, tmp_path):
        """H1 should not appear twice when title comes from filename."""
        source = tmp_path / "source"
        source.mkdir()
        (source / "my-page.md").write_text("# My Page\n\nSome content.")

        output = tmp_path / "output"
        build_site(Config.load(None), source, output)

        html = (output / "my-page" / "index.html").read_text()
        assert html.count("<h1") == 1
