"""Tests for GFM footnote rendering."""

from rockgarden.render.markdown import render_markdown


class TestFootnotes:
    def test_single_footnote(self):
        md = "Text with a footnote[^1].\n\n[^1]: Footnote content.\n"
        html = render_markdown(md)
        assert 'class="footnote-ref"' in html
        assert 'href="#fn1"' in html
        assert "Footnote content." in html

    def test_footnote_backlink(self):
        md = "Text[^1].\n\n[^1]: Note.\n"
        html = render_markdown(md)
        assert 'class="footnote-backref"' in html
        assert 'href="#fnref1"' in html

    def test_multiple_footnotes(self):
        md = "First[^1] and second[^2].\n\n[^1]: Note one.\n[^2]: Note two.\n"
        html = render_markdown(md)
        assert 'href="#fn1"' in html
        assert 'href="#fn2"' in html
        assert "Note one." in html
        assert "Note two." in html

    def test_footnote_section_structure(self):
        md = "Text[^1].\n\n[^1]: Note.\n"
        html = render_markdown(md)
        assert '<section class="footnotes">' in html
        assert '<ol class="footnotes-list">' in html
        assert 'class="footnote-item"' in html

    def test_named_footnote(self):
        md = "Text[^note].\n\n[^note]: Named footnote.\n"
        html = render_markdown(md)
        assert "Named footnote." in html
        assert 'class="footnote-ref"' in html

    def test_multiline_footnote(self):
        md = "Text[^1].\n\n[^1]: First line.\n    Second line.\n"
        html = render_markdown(md)
        assert "First line." in html
        assert "Second line." in html

    def test_no_footnotes_in_regular_text(self):
        html = render_markdown("Just regular text.\n")
        assert "footnote" not in html
