"""Tests for broken link handling."""

from rockgarden.config import Config
from rockgarden.obsidian.wikilinks import process_wikilinks
from rockgarden.output.builder import BuildResult, build_site
from rockgarden.render.markdown import render_markdown


class TestProcessWikilinks:
    """Test that process_wikilinks tracks broken links."""

    def test_returns_tuple_with_content_and_broken_links(self):
        """Should return tuple of (content, broken_links)."""
        content = "Link to [[Target]]"
        resolver = lambda x: None  # All links fail

        result, broken = process_wikilinks(content, resolver)

        assert isinstance(result, str)
        assert isinstance(broken, list)

    def test_tracks_single_broken_link(self):
        """Should track a single broken link."""
        content = "Link to [[NonExistent]]"
        resolver = lambda x: None

        _, broken = process_wikilinks(content, resolver)

        assert len(broken) == 1
        assert broken[0] == ("NonExistent", "NonExistent")

    def test_tracks_multiple_broken_links(self):
        """Should track multiple broken links."""
        content = "Link to [[First]] and [[Second]]"
        resolver = lambda x: None

        _, broken = process_wikilinks(content, resolver)

        assert len(broken) == 2
        assert broken[0] == ("First", "First")
        assert broken[1] == ("Second", "Second")

    def test_tracks_broken_link_with_display_text(self):
        """Should track broken link with custom display text."""
        content = "Link to [[Target|Display Text]]"
        resolver = lambda x: None

        _, broken = process_wikilinks(content, resolver)

        assert len(broken) == 1
        assert broken[0] == ("Target", "Display Text")

    def test_does_not_track_resolved_links(self):
        """Should not track links that resolve successfully."""
        content = "Link to [[Valid]]"
        resolver = lambda x: "/valid/" if x == "Valid" else None

        _, broken = process_wikilinks(content, resolver)

        assert len(broken) == 0

    def test_tracks_only_broken_links_in_mixed_content(self):
        """Should track only broken links when some resolve."""
        content = "Link to [[Valid]] and [[Broken]]"
        resolver = lambda x: "/valid/" if x == "Valid" else None

        _, broken = process_wikilinks(content, resolver)

        assert len(broken) == 1
        assert broken[0] == ("Broken", "Broken")

    def test_converts_broken_link_to_special_marker(self):
        """Should convert broken links to BROKEN:: marker in content."""
        content = "Link to [[NonExistent]]"
        resolver = lambda x: None

        result, _ = process_wikilinks(content, resolver)

        assert "[NonExistent](BROKEN::NonExistent)" in result

    def test_preserves_broken_links_in_code_blocks(self):
        """Should not process wiki-links inside code blocks."""
        content = "Normal [[Broken]]\n```\n[[InCode]]\n```"
        resolver = lambda x: None

        result, broken = process_wikilinks(content, resolver)

        assert len(broken) == 1
        assert broken[0] == ("Broken", "Broken")
        assert "[[InCode]]" in result  # Preserved in code block


class TestRenderMarkdownBrokenLinks:
    """Test that render_markdown handles broken link markers."""

    def test_converts_broken_marker_to_html(self):
        """Should convert BROKEN:: marker to broken link HTML."""
        markdown = "[Target](BROKEN::Target)"

        html = render_markdown(markdown)

        assert '<a class="internal-link broken"' in html
        assert 'data-target="Target"' in html
        assert ">Target</a>" in html

    def test_escapes_html_in_target_attribute(self):
        """Should HTML-escape the data-target attribute."""
        markdown = '[Malicious](BROKEN::Target"onclick="alert())'

        html = render_markdown(markdown)

        assert 'data-target="Target&quot;onclick=&quot;alert()' in html
        assert "onclick=" not in html or "&quot;onclick=" in html

    def test_handles_broken_link_with_spaces(self):
        """Should handle broken links with spaces in target."""
        markdown = "[Missing Page](BROKEN::Missing%20Page)"

        html = render_markdown(markdown)

        assert '<a class="internal-link broken"' in html
        assert 'data-target="Missing Page"' in html

    def test_does_not_add_href_to_broken_links(self):
        """Should not add href attribute to broken links."""
        markdown = "[Target](BROKEN::Target)"

        html = render_markdown(markdown)

        # Should have class but no href
        assert '<a class="internal-link broken"' in html
        assert "href=" not in html

    def test_preserves_normal_links(self):
        """Should not affect normal markdown links."""
        markdown = "[Normal](/path/to/page/)"

        html = render_markdown(markdown)

        assert 'href="/path/to/page/"' in html
        assert "broken" not in html


class TestBuildSiteBrokenLinks:
    """Test that build_site collects and reports broken links."""

    def test_returns_build_result_with_broken_links(self, tmp_path):
        """Should return BuildResult with broken links dict."""
        # Create test vault
        source = tmp_path / "source"
        source.mkdir()
        (source / "page.md").write_text("Link to [[NonExistent]]")

        output = tmp_path / "output"
        config = Config.load(None)

        result = build_site(config, source, output)

        assert isinstance(result, BuildResult)
        assert hasattr(result, "page_count")
        assert hasattr(result, "broken_links")

    def test_tracks_broken_links_by_filename(self, tmp_path):
        """Should track broken links by source filename."""
        source = tmp_path / "source"
        source.mkdir()
        (source / "page-a.md").write_text("Link to [[Missing]]")

        output = tmp_path / "output"
        config = Config.load(None)

        result = build_site(config, source, output)

        assert "page-a.md" in result.broken_links
        assert "Missing" in result.broken_links["page-a.md"]

    def test_tracks_multiple_broken_links_per_page(self, tmp_path):
        """Should track multiple broken links in one page."""
        source = tmp_path / "source"
        source.mkdir()
        (source / "page.md").write_text("Links: [[First]] and [[Second]]")

        output = tmp_path / "output"
        config = Config.load(None)

        result = build_site(config, source, output)

        assert "page.md" in result.broken_links
        assert len(result.broken_links["page.md"]) == 2
        assert "First" in result.broken_links["page.md"]
        assert "Second" in result.broken_links["page.md"]

    def test_does_not_track_pages_without_broken_links(self, tmp_path):
        """Should not include pages with no broken links."""
        source = tmp_path / "source"
        source.mkdir()
        (source / "page-a.md").write_text("Link to [[page-b]]")
        (source / "page-b.md").write_text("# Page B")

        output = tmp_path / "output"
        config = Config.load(None)

        result = build_site(config, source, output)

        assert len(result.broken_links) == 0

    def test_tracks_broken_links_across_multiple_pages(self, tmp_path):
        """Should track broken links across multiple pages."""
        source = tmp_path / "source"
        source.mkdir()
        (source / "page-a.md").write_text("Link to [[Missing1]]")
        (source / "page-b.md").write_text("Link to [[Missing2]]")

        output = tmp_path / "output"
        config = Config.load(None)

        result = build_site(config, source, output)

        assert "page-a.md" in result.broken_links
        assert "page-b.md" in result.broken_links
        assert result.broken_links["page-a.md"] == ["Missing1"]
        assert result.broken_links["page-b.md"] == ["Missing2"]
