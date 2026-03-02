"""Tests for table of contents extraction."""

from rockgarden.nav.toc import TocEntry, extract_toc
from rockgarden.render.markdown import render_markdown


def _render_and_extract(md: str, **kwargs) -> tuple[str, list[TocEntry]]:
    """Render markdown then extract TOC — the real pipeline order."""
    return extract_toc(render_markdown(md), **kwargs)


class TestIdGeneration:
    """Tests for heading ID generation."""

    def test_simple_heading(self):
        html, _ = extract_toc("<h2>Hello World</h2>")
        assert 'id="hello-world"' in html

    def test_special_characters_stripped(self):
        html, _ = extract_toc("<h2>Hello, World! How's it?</h2>")
        assert 'id="hello-world-hows-it"' in html

    def test_unicode_preserved(self):
        html, _ = extract_toc("<h2>Héllo Wörld</h2>")
        assert 'id="héllo-wörld"' in html

    def test_multiple_spaces_collapsed(self):
        html, _ = extract_toc("<h2>Hello   World</h2>")
        assert 'id="hello-world"' in html

    def test_existing_id_preserved(self):
        html, _ = extract_toc('<h2 id="custom">Hello</h2>')
        assert 'id="custom"' in html
        assert html.count("id=") == 1


class TestDeduplication:
    """Tests for duplicate heading ID deduplication."""

    def test_duplicate_headings(self):
        html, entries = extract_toc("<h2>Foo</h2><h2>Foo</h2><h2>Foo</h2>")
        assert 'id="foo"' in html
        assert 'id="foo-1"' in html
        assert 'id="foo-2"' in html
        assert len(entries) == 3

    def test_duplicate_ids_in_entries(self):
        _, entries = extract_toc("<h2>Foo</h2><h2>Foo</h2>")
        assert entries[0].id == "foo"
        assert entries[1].id == "foo-1"


class TestNesting:
    """Tests for TOC tree nesting."""

    def test_flat_h2s(self):
        html_str = "<h2>A</h2><h2>B</h2><h2>C</h2>"
        _, entries = extract_toc(html_str)
        assert len(entries) == 3
        assert all(e.children == [] for e in entries)

    def test_h2_with_h3_children(self):
        html_str = "<h2>Parent</h2><h3>Child 1</h3><h3>Child 2</h3>"
        _, entries = extract_toc(html_str)
        assert len(entries) == 1
        assert entries[0].text == "Parent"
        assert len(entries[0].children) == 2
        assert entries[0].children[0].text == "Child 1"
        assert entries[0].children[1].text == "Child 2"

    def test_deep_nesting(self):
        html_str = "<h2>L2</h2><h3>L3</h3><h4>L4</h4>"
        _, entries = extract_toc(html_str)
        assert len(entries) == 1
        assert len(entries[0].children) == 1
        assert len(entries[0].children[0].children) == 1
        assert entries[0].children[0].children[0].text == "L4"

    def test_sibling_after_nested(self):
        html_str = "<h2>A</h2><h3>A.1</h3><h2>B</h2>"
        _, entries = extract_toc(html_str)
        assert len(entries) == 2
        assert entries[0].text == "A"
        assert len(entries[0].children) == 1
        assert entries[1].text == "B"
        assert entries[1].children == []


class TestInlineMarkup:
    """Tests for headings with inline HTML markup."""

    def test_strong_stripped(self):
        _, entries = extract_toc("<h2><strong>Bold Heading</strong></h2>")
        assert entries[0].text == "Bold Heading"

    def test_code_stripped(self):
        _, entries = extract_toc("<h2>The <code>foo</code> function</h2>")
        assert entries[0].text == "The foo function"

    def test_link_stripped(self):
        _, entries = extract_toc('<h2><a href="/bar">Link Text</a></h2>')
        assert entries[0].text == "Link Text"

    def test_nested_markup(self):
        _, entries = extract_toc("<h2><em><strong>Bold Italic</strong></em></h2>")
        assert entries[0].text == "Bold Italic"


class TestLevelFiltering:
    """Tests for min/max level filtering."""

    def test_h1_excluded_by_default(self):
        _, entries = extract_toc("<h1>Title</h1><h2>Section</h2>")
        assert len(entries) == 1
        assert entries[0].text == "Section"

    def test_h5_excluded_by_default(self):
        _, entries = extract_toc("<h2>Section</h2><h5>Deep</h5>")
        assert len(entries) == 1
        assert entries[0].text == "Section"

    def test_custom_max_depth(self):
        _, entries = extract_toc("<h2>A</h2><h3>B</h3><h4>C</h4>", max_level=3)
        assert len(entries) == 1
        assert len(entries[0].children) == 1
        assert entries[0].children[0].children == []

    def test_h5_h6_with_max_6(self):
        _, entries = extract_toc("<h2>A</h2><h5>B</h5><h6>C</h6>", max_level=6)
        assert len(entries) == 1
        assert entries[0].text == "A"


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_html(self):
        html, entries = extract_toc("")
        assert html == ""
        assert entries == []

    def test_no_headings(self):
        html, entries = extract_toc("<p>Just a paragraph.</p>")
        assert entries == []
        assert "<p>Just a paragraph.</p>" in html

    def test_single_heading(self):
        _, entries = extract_toc("<h2>Only One</h2>")
        assert len(entries) == 1
        assert entries[0].text == "Only One"

    def test_surrounding_content_preserved(self):
        html, _ = extract_toc("<p>Before</p><h2>Heading</h2><p>After</p>")
        assert "<p>Before</p>" in html
        assert "<p>After</p>" in html
        assert 'id="heading"' in html


class TestIntegration:
    """Integration tests: markdown → render → TOC extraction."""

    def test_markdown_headings(self):
        md = "## Introduction\n\nSome text.\n\n### Details\n\nMore text.\n"
        html, entries = _render_and_extract(md)
        assert 'id="introduction"' in html
        assert 'id="details"' in html
        assert len(entries) == 1
        assert entries[0].text == "Introduction"
        assert len(entries[0].children) == 1
        assert entries[0].children[0].text == "Details"

    def test_heading_with_inline_code(self):
        md = "## The `render` method\n"
        html, entries = _render_and_extract(md)
        assert entries[0].text == "The render method"
        assert "id=" in html

    def test_heading_with_bold(self):
        md = "## **Important** Section\n"
        _, entries = _render_and_extract(md)
        assert entries[0].text == "Important Section"

    def test_multiple_same_headings(self):
        md = "## Section\n\nText.\n\n## Section\n\nMore text.\n"
        html, entries = _render_and_extract(md)
        assert len(entries) == 2
        assert entries[0].id == "section"
        assert entries[1].id == "section-1"

    def test_ids_injected_for_anchor_links(self):
        md = "## Heading\n\nSome paragraph.\n"
        html, _ = _render_and_extract(md)
        assert '<h2 id="heading">' in html

    def test_html_entities_unescaped_in_toc_text(self):
        """HTML entities in headings should be unescaped in TOC text."""
        md = "## Expectations & Assumptions\n"
        _, entries = _render_and_extract(md)
        assert entries[0].text == "Expectations & Assumptions"
