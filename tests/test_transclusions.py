"""Tests for note transclusion processing."""

from rockgarden.obsidian.transclusions import process_note_transclusions


def _resolver(target: str) -> str | None:
    notes = {
        "Note A": "<p>Content of Note A</p>",
        "Note B": "<p>Content of Note B</p>",
    }
    return notes.get(target)


class TestProcessNoteTransclusions:
    def test_basic_transclusion(self):
        content = "Before\n![[Note A]]\nAfter"
        result = process_note_transclusions(content, _resolver)
        assert '<div class="transclusion"><p>Content of Note A</p></div>' in result
        assert "Before" in result
        assert "After" in result

    def test_unresolved_left_unchanged(self):
        content = "![[Missing Note]]"
        result = process_note_transclusions(content, _resolver)
        assert result == "![[Missing Note]]"

    def test_media_embed_left_unchanged(self):
        content = "![[image.png]]"
        result = process_note_transclusions(content, _resolver)
        assert result == "![[image.png]]"

    def test_heading_ref_resolved_by_name(self):
        """Heading ref stripped for lookup; full note content returned."""
        content = "![[Note A#Some Heading]]"
        result = process_note_transclusions(content, _resolver)
        assert '<div class="transclusion"><p>Content of Note A</p></div>' in result

    def test_md_extension_stripped(self):
        def resolver_with_md(target: str) -> str | None:
            if target == "My Note":
                return "<p>note content</p>"
            return None

        content = "![[My Note.md]]"
        # .md stripping happens in builder resolver, not here — raw target passed through
        # This test confirms the pattern matches and passes target as-is to resolver
        result = process_note_transclusions(content, resolver_with_md)
        # resolver receives "My Note.md" (builder strips .md, not this function)
        assert result == "![[My Note.md]]"  # resolver returned None for "My Note.md"

    def test_code_block_preserved(self):
        content = "```\n![[Note A]]\n```"
        result = process_note_transclusions(content, _resolver)
        assert "![[Note A]]" in result
        assert "transclusion" not in result

    def test_inline_code_preserved(self):
        content = "Use `![[Note A]]` syntax"
        result = process_note_transclusions(content, _resolver)
        assert "`![[Note A]]`" in result
        assert "transclusion" not in result

    def test_multiple_transclusions(self):
        content = "![[Note A]]\n\n![[Note B]]"
        result = process_note_transclusions(content, _resolver)
        assert "Content of Note A" in result
        assert "Content of Note B" in result

    def test_cycle_detection_via_resolver(self):
        """Cycle detection is the resolver's responsibility; returning None leaves embed unchanged."""
        call_count = 0

        def cycle_resolver(target: str) -> str | None:
            nonlocal call_count
            call_count += 1
            return None  # simulates cycle detected

        content = "![[Note A]]"
        result = process_note_transclusions(content, cycle_resolver)
        assert result == "![[Note A]]"
        assert call_count == 1
