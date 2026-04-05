"""Tests for highlight (==text==) syntax."""

from rockgarden.render.markdown import render_markdown


class TestHighlights:
    def test_basic_highlight(self):
        result = render_markdown("This is ==highlighted== text")
        assert "<mark>" in result
        assert "highlighted" in result
        assert "</mark>" in result

    def test_highlight_with_inline_formatting(self):
        result = render_markdown("==**bold highlight**==")
        assert "<mark>" in result
        assert "<strong>" in result

    def test_multiple_highlights(self):
        result = render_markdown("==one== and ==two==")
        assert result.count("<mark>") == 2
        assert result.count("</mark>") == 2

    def test_no_empty_highlight(self):
        result = render_markdown("====")
        assert "<mark>" not in result

    def test_highlight_in_code_block_unchanged(self):
        result = render_markdown("```\n==not highlighted==\n```")
        assert "<mark>" not in result

    def test_inline_code_unchanged(self):
        result = render_markdown("`==not highlighted==`")
        assert "<mark>" not in result

    def test_single_equals_not_highlight(self):
        result = render_markdown("a = b")
        assert "<mark>" not in result

    def test_triple_equals_renders_with_extra_char(self):
        """=== has an odd =, so it becomes = + ==highlight==."""
        result = render_markdown("===highlighted===")
        assert "<mark>" in result
        assert "highlighted" in result
