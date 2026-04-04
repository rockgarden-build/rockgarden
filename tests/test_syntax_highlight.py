"""Tests for syntax highlighting in fenced code blocks."""

from rockgarden.render.markdown import render_markdown


class TestSyntaxHighlighting:
    def test_known_language_produces_highlighted_spans(self):
        md = '```python\nprint("hello")\n```\n'
        html = render_markdown(md)
        assert '<div class="highlight">' in html
        assert "<span" in html

    def test_unknown_language_falls_back_to_plain_code(self):
        md = "```unknownlang\nsome code\n```\n"
        html = render_markdown(md)
        assert '<code class="language-unknownlang">' in html
        assert "<pre>" in html
        assert "highlight" not in html

    def test_no_language_falls_back_to_plain_code(self):
        md = "```\nplain text\n```\n"
        html = render_markdown(md)
        assert "<pre><code>" in html
        assert "highlight" not in html

    def test_html_escaped_in_fallback(self):
        md = "```\n<script>alert('xss')</script>\n```\n"
        html = render_markdown(md)
        assert "&lt;script&gt;" in html
        assert "<script>" not in html

    def test_html_escaped_in_highlighted(self):
        md = '```html\n<script>alert("xss")</script>\n```\n'
        html = render_markdown(md)
        assert '<div class="highlight">' in html
        assert "<script>alert" not in html

    def test_multiple_languages(self):
        for lang in ["python", "javascript", "html", "css", "bash"]:
            md = f"```{lang}\ncode\n```\n"
            html = render_markdown(md)
            assert '<div class="highlight">' in html, f"Failed for {lang}"
