"""Tests for asset collection and copying."""

from rockgarden.assets import (
    collect_markdown_images,
    is_external_url,
)


class TestIsExternalUrl:
    """Tests for is_external_url function."""

    def test_http_url(self):
        assert is_external_url("http://example.com/image.png") is True

    def test_https_url(self):
        assert is_external_url("https://example.com/image.png") is True

    def test_protocol_relative(self):
        assert is_external_url("//example.com/image.png") is True

    def test_data_url(self):
        assert is_external_url("data:image/png;base64,abc123") is True

    def test_relative_path(self):
        assert is_external_url("images/photo.png") is False

    def test_absolute_path(self):
        assert is_external_url("/images/photo.png") is False

    def test_parent_path(self):
        assert is_external_url("../images/photo.png") is False


class TestCollectMarkdownImages:
    """Tests for collect_markdown_images function."""

    def _mock_resolver(self, target):
        """Simple resolver that returns the target as path."""
        return f"/{target}", target

    def test_basic_image(self):
        """Basic markdown image is collected."""
        content = "![alt text](image.png)"
        result = collect_markdown_images(content, self._mock_resolver)
        assert result == {"image.png"}

    def test_image_with_path(self):
        """Image with path is collected."""
        content = "![photo](images/photo.jpg)"
        result = collect_markdown_images(content, self._mock_resolver)
        assert result == {"images/photo.jpg"}

    def test_image_empty_alt(self):
        """Image with empty alt text is collected."""
        content = "![](diagram.svg)"
        result = collect_markdown_images(content, self._mock_resolver)
        assert result == {"diagram.svg"}

    def test_image_with_title(self):
        """Image with title attribute is collected."""
        content = '![alt](image.png "Title text")'
        result = collect_markdown_images(content, self._mock_resolver)
        assert result == {"image.png"}

    def test_multiple_images(self):
        """Multiple images are all collected."""
        content = "![one](one.png) text ![two](two.jpg)"
        result = collect_markdown_images(content, self._mock_resolver)
        assert result == {"one.png", "two.jpg"}

    def test_external_url_skipped(self):
        """External URLs are not collected."""
        content = "![external](https://example.com/image.png)"
        result = collect_markdown_images(content, self._mock_resolver)
        assert result == set()

    def test_mixed_local_and_external(self):
        """Only local images are collected."""
        content = "![local](local.png) ![ext](https://x.com/img.png)"
        result = collect_markdown_images(content, self._mock_resolver)
        assert result == {"local.png"}

    def test_unresolved_image_skipped(self):
        """Unresolved images are not collected."""

        def resolver(target):
            return None

        content = "![missing](missing.png)"
        result = collect_markdown_images(content, resolver)
        assert result == set()

    def test_image_in_code_block_skipped(self):
        """Images in code blocks are not collected."""
        content = "```\n![code](code.png)\n```"
        result = collect_markdown_images(content, self._mock_resolver)
        assert result == set()

    def test_image_in_inline_code_skipped(self):
        """Images in inline code are not collected."""
        content = "Use `![alt](image.png)` syntax"
        result = collect_markdown_images(content, self._mock_resolver)
        assert result == set()

    def test_image_outside_code_collected(self):
        """Images outside code blocks are collected."""
        content = "```\ncode\n```\n\n![real](real.png)"
        result = collect_markdown_images(content, self._mock_resolver)
        assert result == {"real.png"}
