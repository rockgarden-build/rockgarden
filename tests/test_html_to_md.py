"""Tests for HTML to markdown conversion."""

from rockgarden.output.html_to_md import html_to_markdown


class TestHtmlToMarkdown:
    def test_basic_paragraph(self):
        assert html_to_markdown("<p>Hello world</p>") == "Hello world"

    def test_headings(self):
        assert html_to_markdown("<h2>Title</h2>") == "## Title"

    def test_links_preserved(self):
        result = html_to_markdown('<a href="https://example.com">click</a>')
        assert result == "[click](https://example.com)"

    def test_code_block(self):
        result = html_to_markdown("<pre><code>x = 1</code></pre>")
        assert "x = 1" in result

    def test_list(self):
        result = html_to_markdown("<ul><li>one</li><li>two</li></ul>")
        assert "- one" in result
        assert "- two" in result

    def test_empty_string(self):
        assert html_to_markdown("") == ""

    def test_whitespace_only_empty(self):
        assert html_to_markdown("   ") == ""

    def test_whitespace_stripped(self):
        result = html_to_markdown("  <p>Hello</p>  ")
        assert result == "Hello"

    def test_heading_offset(self):
        result = html_to_markdown("<h2>Title</h2>", heading_offset=2)
        assert result == "#### Title"

    def test_heading_offset_clamps_at_h6(self):
        result = html_to_markdown("<h5>Deep</h5>", heading_offset=3)
        assert result == "###### Deep"

    def test_heading_offset_zero_unchanged(self):
        result = html_to_markdown("<h1>Top</h1>", heading_offset=0)
        assert result == "# Top"

    def test_heading_offset_preserves_code_blocks(self):
        html = "<h2>Title</h2><pre><code># comment\necho hello</code></pre>"
        result = html_to_markdown(html, heading_offset=2)
        assert "#### Title" in result
        assert "# comment" in result
        assert "### comment" not in result
