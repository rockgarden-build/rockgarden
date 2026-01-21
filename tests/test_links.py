"""Tests for markdown link transformation."""

from rockgarden.links import transform_md_links


class TestTransformMdLinksCleanUrls:
    """Tests for clean URLs mode (default)."""

    def test_relative_link(self):
        """Relative .md links are transformed to trailing slash."""
        content = "[other page](./other-page.md)"
        result = transform_md_links(content, clean_urls=True)
        assert result == "[other page](./other-page/)"

    def test_relative_link_no_dot(self):
        """Relative links without ./ are transformed."""
        content = "[page](page.md)"
        result = transform_md_links(content, clean_urls=True)
        assert result == "[page](page/)"

    def test_parent_directory_link(self):
        """Parent directory links are transformed."""
        content = "[page](../folder/page.md)"
        result = transform_md_links(content, clean_urls=True)
        assert result == "[page](../folder/page/)"

    def test_absolute_path_link(self):
        """Absolute path links are transformed."""
        content = "[page](/folder/page.md)"
        result = transform_md_links(content, clean_urls=True)
        assert result == "[page](/folder/page/)"

    def test_link_with_anchor(self):
        """Links with anchors preserve the anchor."""
        content = "[section](page.md#heading)"
        result = transform_md_links(content, clean_urls=True)
        assert result == "[section](page/#heading)"

    def test_link_with_query_string(self):
        """Links with query strings preserve the query."""
        content = "[page](page.md?foo=bar)"
        result = transform_md_links(content, clean_urls=True)
        assert result == "[page](page/?foo=bar)"

    def test_multiple_links(self):
        """Multiple links in content are all transformed."""
        content = "See [page one](one.md) and [page two](two.md)."
        result = transform_md_links(content, clean_urls=True)
        assert result == "See [page one](one/) and [page two](two/)."


class TestTransformMdLinksNoCleanUrls:
    """Tests for clean_urls=False mode (.html extension)."""

    def test_relative_link(self):
        """Relative .md links are transformed to .html."""
        content = "[other page](./other-page.md)"
        result = transform_md_links(content, clean_urls=False)
        assert result == "[other page](./other-page.html)"

    def test_relative_link_no_dot(self):
        """Relative links without ./ are transformed."""
        content = "[page](page.md)"
        result = transform_md_links(content, clean_urls=False)
        assert result == "[page](page.html)"

    def test_parent_directory_link(self):
        """Parent directory links are transformed."""
        content = "[page](../folder/page.md)"
        result = transform_md_links(content, clean_urls=False)
        assert result == "[page](../folder/page.html)"

    def test_absolute_path_link(self):
        """Absolute path links are transformed."""
        content = "[page](/folder/page.md)"
        result = transform_md_links(content, clean_urls=False)
        assert result == "[page](/folder/page.html)"

    def test_link_with_anchor(self):
        """Links with anchors preserve the anchor."""
        content = "[section](page.md#heading)"
        result = transform_md_links(content, clean_urls=False)
        assert result == "[section](page.html#heading)"

    def test_link_with_query_string(self):
        """Links with query strings preserve the query."""
        content = "[page](page.md?foo=bar)"
        result = transform_md_links(content, clean_urls=False)
        assert result == "[page](page.html?foo=bar)"

    def test_multiple_links(self):
        """Multiple links in content are all transformed."""
        content = "See [page one](one.md) and [page two](two.md)."
        result = transform_md_links(content, clean_urls=False)
        assert result == "See [page one](one.html) and [page two](two.html)."


class TestExternalLinksPreserved:
    """Tests for external link preservation (mode independent)."""

    def test_external_http_link_preserved(self):
        """External http links are not transformed."""
        content = "[example](http://example.com/page.md)"
        result = transform_md_links(content)
        assert result == "[example](http://example.com/page.md)"

    def test_external_https_link_preserved(self):
        """External https links are not transformed."""
        content = "[example](https://example.com/page.md)"
        result = transform_md_links(content)
        assert result == "[example](https://example.com/page.md)"

    def test_mailto_link_preserved(self):
        """Mailto links are not transformed."""
        content = "[email](mailto:test@example.md)"
        result = transform_md_links(content)
        assert result == "[email](mailto:test@example.md)"

    def test_protocol_relative_link_preserved(self):
        """Protocol-relative links are not transformed."""
        content = "[page](//example.com/page.md)"
        result = transform_md_links(content)
        assert result == "[page](//example.com/page.md)"

    def test_non_md_link_preserved(self):
        """Non-.md links are not transformed."""
        content = "[image](./image.png)"
        result = transform_md_links(content)
        assert result == "[image](./image.png)"

    def test_html_link_preserved(self):
        """Already .html links are not transformed."""
        content = "[page](./page.html)"
        result = transform_md_links(content)
        assert result == "[page](./page.html)"


class TestCodeBlockPreservation:
    def test_link_in_fenced_code_block(self):
        """Links in fenced code blocks are not transformed."""
        content = "```\n[page](page.md)\n```"
        result = transform_md_links(content)
        assert result == "```\n[page](page.md)\n```"

    def test_link_in_inline_code(self):
        """Links in inline code are not transformed."""
        content = "Use `[page](page.md)` syntax."
        result = transform_md_links(content)
        assert result == "Use `[page](page.md)` syntax."

    def test_link_outside_code_block_clean_urls(self):
        """Links outside code blocks are still transformed (clean URLs)."""
        content = "```\ncode\n```\n\n[page](page.md)"
        result = transform_md_links(content, clean_urls=True)
        assert result == "```\ncode\n```\n\n[page](page/)"

    def test_link_outside_code_block_no_clean_urls(self):
        """Links outside code blocks are still transformed (no clean URLs)."""
        content = "```\ncode\n```\n\n[page](page.md)"
        result = transform_md_links(content, clean_urls=False)
        assert result == "```\ncode\n```\n\n[page](page.html)"

    def test_mixed_content_clean_urls(self):
        """Mixed code and regular content is handled correctly (clean URLs)."""
        content = "[one](one.md) `[two](two.md)` [three](three.md)"
        result = transform_md_links(content, clean_urls=True)
        assert result == "[one](one/) `[two](two.md)` [three](three/)"

    def test_mixed_content_no_clean_urls(self):
        """Mixed code and regular content is handled correctly (no clean URLs)."""
        content = "[one](one.md) `[two](two.md)` [three](three.md)"
        result = transform_md_links(content, clean_urls=False)
        assert result == "[one](one.html) `[two](two.md)` [three](three.html)"
