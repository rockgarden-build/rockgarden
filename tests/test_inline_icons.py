"""Tests for inline icon syntax in markdown content."""

from rockgarden.icons.inline import process_inline_icons
from rockgarden.icons.resolver import LIBRARY_ALIASES, resolve_icon


class TestProcessInlineIcons:
    def test_basic_icon(self):
        result = process_inline_icons(":lucide-info:")
        assert "<svg" in result

    def test_hyphenated_icon_name(self):
        result = process_inline_icons(":lucide-map-pin:")
        assert "<svg" in result

    def test_matches_resolved_icon(self):
        result = process_inline_icons(":lucide-info:")
        assert result == resolve_icon("lucide:info")

    def test_unknown_icon_left_as_text(self):
        text = ":lucide-nonexistent-xyz:"
        assert process_inline_icons(text) == text

    def test_unknown_library_left_as_text(self):
        text = ":fakelib-info:"
        assert process_inline_icons(text) == text

    def test_inline_code_preserved(self):
        text = "Use `:lucide-info:` for info icons"
        assert process_inline_icons(text) == text

    def test_fenced_code_block_preserved(self):
        text = "```\n:lucide-info:\n```"
        assert process_inline_icons(text) == text

    def test_double_colon_not_matched(self):
        text = "::lucide-info::"
        assert process_inline_icons(text) == text

    def test_no_hyphen_not_matched(self):
        text = ":smile:"
        assert process_inline_icons(text) == text

    def test_multiple_icons(self):
        result = process_inline_icons(":lucide-info: and :lucide-star:")
        assert result.count("<svg") == 2

    def test_mixed_valid_and_invalid(self):
        result = process_inline_icons(":lucide-info: and :lucide-nonexistent-xyz:")
        assert "<svg" in result
        assert ":lucide-nonexistent-xyz:" in result

    def test_icon_in_sentence(self):
        result = process_inline_icons("Click :lucide-settings: to configure.")
        assert "<svg" in result
        assert "Click " in result
        assert " to configure." in result

    def test_adjacent_word_char_not_matched(self):
        text = "word:lucide-info:"
        assert process_inline_icons(text) == text

    def test_trailing_word_char_not_matched(self):
        text = ":lucide-info:word"
        assert process_inline_icons(text) == text


class TestLibraryAliases:
    def test_fa_alias_exists(self):
        assert LIBRARY_ALIASES["fa"] == "fontawesome"

    def test_fa_alias_applied(self):
        # fontawesome loader doesn't exist yet, so returns None,
        # but the alias should be applied (not treated as "fa" library)
        assert resolve_icon("fa:heart") is None
