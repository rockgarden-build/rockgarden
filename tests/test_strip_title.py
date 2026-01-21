"""Tests for stripping H1 from content."""

from rockgarden.content import strip_content_title


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
