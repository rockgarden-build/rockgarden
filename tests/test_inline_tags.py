"""Tests for inline tag extraction and rendering."""

from rockgarden.config import Config, SiteConfig
from rockgarden.obsidian.inline_tags import (
    expand_hierarchical_tags,
    extract_inline_tags,
)
from rockgarden.output.builder import build_site


class TestExtractInlineTags:
    def test_basic_tag(self):
        content, tags = extract_inline_tags("Hello #python world")
        assert tags == ["python"]
        assert "[#python](" in content

    def test_multiple_tags(self):
        content, tags = extract_inline_tags("Use #python and #rust")
        assert tags == ["python", "rust"]

    def test_nested_tag(self):
        content, tags = extract_inline_tags("Status: #project/active")
        assert tags == ["project/active"]
        assert "[#project/active](" in content

    def test_not_in_code_span(self):
        content, tags = extract_inline_tags("Use `#python` for scripting")
        assert tags == []
        assert "`#python`" in content

    def test_not_in_fenced_block(self):
        content, tags = extract_inline_tags("```\n#python\n```")
        assert tags == []

    def test_not_a_heading(self):
        content, tags = extract_inline_tags("# Heading\n\nSome text")
        assert tags == []

    def test_not_a_number(self):
        content, tags = extract_inline_tags("Issue #123 is fixed")
        assert tags == []

    def test_tag_at_start_of_line(self):
        content, tags = extract_inline_tags("#python is great")
        assert tags == ["python"]

    def test_tag_with_hyphens(self):
        content, tags = extract_inline_tags("Use #my-tag here")
        assert tags == ["my-tag"]

    def test_tag_link_url(self):
        content, tags = extract_inline_tags("Hello #python", base_path="/docs")
        assert "[#python](/docs/tags/python/)" in content

    def test_tag_link_no_clean_urls(self):
        content, tags = extract_inline_tags("Hello #python", clean_urls=False)
        assert "[#python](/tags/python.html)" in content

    def test_no_tags(self):
        content, tags = extract_inline_tags("No tags here")
        assert tags == []
        assert content == "No tags here"

    def test_tag_after_punctuation(self):
        content, tags = extract_inline_tags("see: #python")
        assert tags == ["python"]

    def test_tag_not_inside_word(self):
        content, tags = extract_inline_tags("foo#bar is not a tag")
        assert tags == []

    def test_not_in_anchor_link(self):
        content, tags = extract_inline_tags("[Jump](#introduction)")
        assert tags == []
        assert content == "[Jump](#introduction)"

    def test_not_in_html_entity(self):
        content, tags = extract_inline_tags("Freemen&#x27;s Wood")
        assert tags == []
        assert content == "Freemen&#x27;s Wood"

    def test_not_in_numeric_html_entity(self):
        content, tags = extract_inline_tags("&#xABCD;")
        assert tags == []

    def test_tag_after_html_entity_still_works(self):
        content, tags = extract_inline_tags("Tom&#x27;s #python notes")
        assert tags == ["python"]

    def test_not_in_markdown_link_text(self):
        content, tags = extract_inline_tags("[text with #python](http://example.com)")
        assert tags == []

    def test_tag_outside_link_still_works(self):
        content, tags = extract_inline_tags("[link](#anchor) and #python")
        assert tags == ["python"]
        assert "[link](#anchor)" in content


class TestExpandHierarchicalTags:
    def test_flat_tags_unchanged(self):
        assert expand_hierarchical_tags(["python", "rust"]) == ["python", "rust"]

    def test_nested_expands(self):
        result = expand_hierarchical_tags(["project/active"])
        assert "project/active" in result
        assert "project" in result

    def test_deep_nesting(self):
        result = expand_hierarchical_tags(["a/b/c"])
        assert set(result) == {"a", "a/b", "a/b/c"}

    def test_dedup(self):
        result = expand_hierarchical_tags(["project/a", "project/b"])
        assert result.count("project") == 1

    def test_empty(self):
        assert expand_hierarchical_tags([]) == []


class TestInlineTagsIntegration:
    def test_inline_tags_merged_with_frontmatter(self, tmp_path):
        source = tmp_path / "content"
        source.mkdir()
        (source / "page.md").write_text(
            "---\ntags: [existing]\n---\n# Hello\n\nSee #python for details.\n"
        )
        output = tmp_path / "output"
        config = Config(site=SiteConfig(source=source, output=output))
        build_site(config, source, output)
        # Both tag pages should exist
        assert (output / "tags" / "existing" / "index.html").exists()
        assert (output / "tags" / "python" / "index.html").exists()

    def test_hierarchical_tag_pages_generated(self, tmp_path):
        source = tmp_path / "content"
        source.mkdir()
        (source / "page.md").write_text("---\ntags: [project/active]\n---\n# Hello\n")
        output = tmp_path / "output"
        config = Config(site=SiteConfig(source=source, output=output))
        build_site(config, source, output)
        assert (output / "tags" / "project-active" / "index.html").exists()
        assert (output / "tags" / "project" / "index.html").exists()

    def test_inline_tag_renders_as_link(self, tmp_path):
        source = tmp_path / "content"
        source.mkdir()
        (source / "page.md").write_text("# Hello\n\nSee #python for details.\n")
        output = tmp_path / "output"
        config = Config(site=SiteConfig(source=source, output=output))
        build_site(config, source, output)
        html = (output / "page" / "index.html").read_text()
        assert "/tags/python/" in html
