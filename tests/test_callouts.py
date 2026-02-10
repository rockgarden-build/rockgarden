"""Tests for callout processing."""

from rockgarden.obsidian.callouts import get_callout_icon, process_callouts
from rockgarden.render.markdown import render_markdown


def _render_and_process(md: str) -> str:
    """Render markdown then process callouts — the real pipeline order."""
    return process_callouts(render_markdown(md))


class TestProcessCallouts:
    """Tests for process_callouts operating on rendered HTML."""

    def test_basic_note(self):
        result = _render_and_process("> [!note]\n> This is a note.")
        assert '<div class="callout callout-note">' in result
        assert "This is a note." in result

    def test_gfm_uppercase(self):
        result = _render_and_process("> [!NOTE]\n> This is a note.")
        assert '<div class="callout callout-note">' in result
        assert "This is a note." in result

    def test_gfm_warning_uppercase(self):
        result = _render_and_process("> [!WARNING]\n> This is a warning.")
        assert '<div class="callout callout-warning">' in result
        assert "This is a warning." in result

    def test_obsidian_with_custom_title(self):
        result = _render_and_process("> [!tip] Custom Title\n> Tip content here.")
        assert '<div class="callout callout-tip">' in result
        assert "Custom Title" in result
        assert "Tip content here." in result

    def test_obsidian_without_custom_title(self):
        result = _render_and_process("> [!warning]\n> Warning content.")
        assert "Warning" in result
        assert "Warning content." in result

    def test_collapsible_expanded(self):
        result = _render_and_process("> [!note]+ Expandable Note\n> Content here.")
        assert '<details class="callout callout-note" open>' in result
        assert '<summary class="callout-title">' in result
        assert "Expandable Note" in result
        assert "Content here." in result

    def test_collapsible_collapsed(self):
        result = _render_and_process("> [!info]- Collapsible Info\n> Hidden content.")
        assert '<details class="callout callout-info">' in result
        details_tag = result.split("</details>")[0]
        assert " open" not in details_tag
        assert '<summary class="callout-title">' in result
        assert "Collapsible Info" in result
        assert "Hidden content." in result

    def test_multiline_content(self):
        md = "> [!note]\n> Line one.\n> Line two.\n> Line three."
        result = _render_and_process(md)
        assert "Line one." in result
        assert "Line two." in result
        assert "Line three." in result

    def test_multiple_callouts(self):
        content = (
            "> [!note]\n> First note.\n\n"
            "Some text in between.\n\n"
            "> [!warning]\n> A warning.\n"
        )
        result = _render_and_process(content)
        assert result.count('callout callout-note') == 1
        assert result.count('callout callout-warning') == 1
        assert "First note." in result
        assert "A warning." in result

    def test_all_standard_types(self):
        types = [
            "note", "abstract", "summary", "tldr", "info",
            "tip", "hint", "important",
            "success", "check", "done",
            "question", "help", "faq",
            "warning", "caution", "attention",
            "failure", "fail", "missing",
            "danger", "error", "bug",
            "example", "quote", "cite",
        ]
        for callout_type in types:
            result = _render_and_process(f"> [!{callout_type}]\n> Content.")
            assert f'callout callout-{callout_type}' in result

    def test_empty_content(self):
        result = _render_and_process("> [!note] Just a title\n")
        assert '<div class="callout callout-note">' in result
        assert "Just a title" in result

    def test_mixed_case_type(self):
        result = _render_and_process("> [!NoTe]\n> Content here.")
        assert '<div class="callout callout-note">' in result

    def test_content_with_bold_and_italic(self):
        result = _render_and_process("> [!note]\n> Content with **bold** and *italic*.")
        assert "<strong>bold</strong>" in result
        assert "<em>italic</em>" in result

    def test_content_with_list(self):
        result = _render_and_process("> [!note]\n> Some text\n> - item 1\n> - item 2")
        assert "<li>item 1</li>" in result
        assert "<li>item 2</li>" in result

    def test_content_with_heading(self):
        result = _render_and_process("> [!quote]\n> ## A Heading\n> Some content")
        assert "<h2>A Heading</h2>" in result
        assert "Some content" in result

    def test_content_with_link(self):
        result = _render_and_process("> [!note]\n> See [page](page.html) for details")
        assert '<a href="page.html">page</a>' in result

    def test_content_with_inline_code(self):
        result = _render_and_process("> [!note]\n> Use `code` here")
        assert "<code>code</code>" in result

    def test_content_with_separate_paragraphs(self):
        result = _render_and_process("> [!note]\n> First para\n>\n> Second para")
        assert "First para" in result
        assert "Second para" in result

    def test_regular_blockquote_unchanged(self):
        result = _render_and_process("> Just a regular blockquote\n> with more text.")
        assert "<blockquote>" in result
        assert "callout" not in result

    def test_preserves_surrounding_content(self):
        content = "Before\n\n> [!note]\n> Note content.\n\nAfter\n"
        result = _render_and_process(content)
        assert "Before" in result
        assert '<div class="callout callout-note">' in result
        assert "After" in result


class TestGetCalloutIcon:
    """Tests for get_callout_icon function."""

    def test_note_icon(self):
        assert get_callout_icon("note") == "ℹ️"

    def test_warning_icon(self):
        assert get_callout_icon("warning") == "⚠️"

    def test_tip_icon(self):
        assert get_callout_icon("tip") == "💡"

    def test_unknown_type_default(self):
        assert get_callout_icon("unknown_type") == "ℹ️"

    def test_all_types_have_icons(self):
        types = [
            "note", "abstract", "summary", "tldr", "info",
            "tip", "hint", "important",
            "success", "check", "done",
            "question", "help", "faq",
            "warning", "caution", "attention",
            "failure", "fail", "missing",
            "danger", "error", "bug",
            "example", "quote", "cite",
        ]
        for callout_type in types:
            icon = get_callout_icon(callout_type)
            assert icon is not None
            assert len(icon) > 0
