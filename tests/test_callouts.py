"""Tests for callout processing."""

from rockgarden.obsidian.callouts import (
    get_callout_icon,
    parse_callout,
    process_callouts,
)
import re


class TestProcessCallouts:
    """Tests for process_callouts function."""

    def test_gfm_note_uppercase(self):
        """Process GFM NOTE alert (uppercase)."""
        content = "> [!NOTE]\n> This is a note."
        result = process_callouts(content)
        assert '<div class="callout callout-note">' in result
        assert "This is a note." in result

    def test_gfm_warning_uppercase(self):
        """Process GFM WARNING alert (uppercase)."""
        content = "> [!WARNING]\n> This is a warning."
        result = process_callouts(content)
        assert '<div class="callout callout-warning">' in result
        assert "This is a warning." in result

    def test_obsidian_lowercase(self):
        """Process Obsidian callout with lowercase type."""
        content = "> [!note]\n> This is a note."
        result = process_callouts(content)
        assert '<div class="callout callout-note">' in result
        assert "This is a note." in result

    def test_obsidian_with_custom_title(self):
        """Process Obsidian callout with custom title."""
        content = "> [!tip] Custom Title\n> Tip content here."
        result = process_callouts(content)
        assert '<div class="callout callout-tip">' in result
        assert "Custom Title" in result
        assert "Tip content here." in result

    def test_obsidian_without_custom_title(self):
        """Process Obsidian callout without custom title uses capitalized type."""
        content = "> [!warning]\n> Warning content."
        result = process_callouts(content)
        assert "Warning" in result
        assert "Warning content." in result

    def test_collapsible_expanded(self):
        """Process collapsible callout with + (expanded by default)."""
        content = "> [!note]+ Expandable Note\n> Content here."
        result = process_callouts(content)
        assert '<details class="callout callout-note" open>' in result
        assert '<summary class="callout-title">' in result
        assert "Expandable Note" in result
        assert "Content here." in result

    def test_collapsible_collapsed(self):
        """Process collapsible callout with - (collapsed by default)."""
        content = "> [!info]- Collapsible Info\n> Hidden content."
        result = process_callouts(content)
        assert '<details class="callout callout-info">' in result
        assert ' open' not in result
        assert '<summary class="callout-title">' in result
        assert "Collapsible Info" in result
        assert "Hidden content." in result

    def test_multiline_content(self):
        """Process callout with multiple lines of content."""
        content = "> [!note]\n> Line one.\n> Line two.\n> Line three."
        result = process_callouts(content)
        assert "Line one." in result
        assert "Line two." in result
        assert "Line three." in result

    def test_callout_in_code_block_not_processed(self):
        """Callouts inside code blocks are not processed."""
        content = "```\n> [!note]\n> This should not be processed.\n```"
        result = process_callouts(content)
        assert '<div class="callout' not in result
        assert "> [!note]" in result

    def test_callout_in_inline_code_not_processed(self):
        """Callouts inside inline code are not processed."""
        content = "Some text `> [!note]` more text"
        result = process_callouts(content)
        assert '<div class="callout' not in result
        assert "> [!note]" in result

    def test_multiple_callouts(self):
        """Process multiple callouts in one document."""
        content = (
            "> [!note]\n> First note.\n\n"
            "Some text in between.\n\n"
            "> [!warning]\n> A warning.\n"
        )
        result = process_callouts(content)
        assert result.count('<div class="callout callout-note">') == 1
        assert result.count('<div class="callout callout-warning">') == 1
        assert "First note." in result
        assert "A warning." in result

    def test_all_standard_types(self):
        """All standard callout types are recognized."""
        types = [
            "note", "abstract", "summary", "tldr", "info",
            "tip", "hint", "important",
            "success", "check", "done",
            "question", "help", "faq",
            "warning", "caution", "attention",
            "failure", "fail", "missing",
            "danger", "error", "bug",
            "example", "quote", "cite"
        ]
        for callout_type in types:
            content = f"> [!{callout_type}]\n> Content."
            result = process_callouts(content)
            assert f'class="callout callout-{callout_type}"' in result

    def test_empty_content(self):
        """Process callout with no content lines."""
        content = "> [!note] Just a title\n"
        result = process_callouts(content)
        assert '<div class="callout callout-note">' in result
        assert "Just a title" in result

    def test_mixed_case_type(self):
        """Process callout with mixed case type (should be normalized to lowercase)."""
        content = "> [!NoTe]\n> Content here."
        result = process_callouts(content)
        assert '<div class="callout callout-note">' in result

    def test_content_with_markdown(self):
        """Callout content can contain markdown (not rendered yet, just preserved)."""
        content = "> [!note]\n> Content with **bold** and *italic*."
        result = process_callouts(content)
        assert "Content with **bold** and *italic*." in result


class TestParseCallout:
    """Tests for parse_callout function."""

    def test_parse_basic_callout(self):
        """Parse basic callout without title or fold."""
        match = re.search(
            r"^> \[!(\w+)\]([+-])?[ \t]*(.*?)\n((?:> .*\n?)*)",
            "> [!note]\n> Content here.",
            re.MULTILINE
        )
        parsed = parse_callout(match)
        assert parsed["type"] == "note"
        assert parsed["fold"] is None
        assert parsed["title"] == "Note"
        assert parsed["content"] == "Content here."

    def test_parse_with_custom_title(self):
        """Parse callout with custom title."""
        match = re.search(
            r"^> \[!(\w+)\]([+-])?[ \t]*(.*?)\n((?:> .*\n?)*)",
            "> [!tip] My Custom Title\n> Tip content.",
            re.MULTILINE
        )
        parsed = parse_callout(match)
        assert parsed["type"] == "tip"
        assert parsed["title"] == "My Custom Title"
        assert parsed["content"] == "Tip content."

    def test_parse_collapsible_expanded(self):
        """Parse collapsible callout with + modifier."""
        match = re.search(
            r"^> \[!(\w+)\]([+-])?[ \t]*(.*?)\n((?:> .*\n?)*)",
            "> [!info]+ Title\n> Content.",
            re.MULTILINE
        )
        parsed = parse_callout(match)
        assert parsed["fold"] == "+"

    def test_parse_collapsible_collapsed(self):
        """Parse collapsible callout with - modifier."""
        match = re.search(
            r"^> \[!(\w+)\]([+-])?[ \t]*(.*?)\n((?:> .*\n?)*)",
            "> [!info]- Title\n> Content.",
            re.MULTILINE
        )
        parsed = parse_callout(match)
        assert parsed["fold"] == "-"

    def test_parse_multiline_content(self):
        """Parse callout with multiple content lines."""
        match = re.search(
            r"^> \[!(\w+)\]([+-])?[ \t]*(.*?)\n((?:> .*\n?)*)",
            "> [!note]\n> Line 1.\n> Line 2.\n> Line 3.",
            re.MULTILINE
        )
        parsed = parse_callout(match)
        assert "Line 1." in parsed["content"]
        assert "Line 2." in parsed["content"]
        assert "Line 3." in parsed["content"]


class TestGetCalloutIcon:
    """Tests for get_callout_icon function."""

    def test_note_icon(self):
        """Get icon for note callout."""
        icon = get_callout_icon("note")
        assert icon == "ℹ️"

    def test_warning_icon(self):
        """Get icon for warning callout."""
        icon = get_callout_icon("warning")
        assert icon == "⚠️"

    def test_tip_icon(self):
        """Get icon for tip callout."""
        icon = get_callout_icon("tip")
        assert icon == "💡"

    def test_unknown_type_default(self):
        """Unknown callout type returns default info icon."""
        icon = get_callout_icon("unknown_type")
        assert icon == "ℹ️"

    def test_all_types_have_icons(self):
        """All standard callout types have icons defined."""
        types = [
            "note", "abstract", "summary", "tldr", "info",
            "tip", "hint", "important",
            "success", "check", "done",
            "question", "help", "faq",
            "warning", "caution", "attention",
            "failure", "fail", "missing",
            "danger", "error", "bug",
            "example", "quote", "cite"
        ]
        for callout_type in types:
            icon = get_callout_icon(callout_type)
            assert icon is not None
            assert len(icon) > 0
