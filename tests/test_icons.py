"""Tests for icon resolution."""

from rockgarden.icons import configure_icons_dir, resolve_icon
from rockgarden.icons.lucide import load_lucide_icon
from rockgarden.obsidian.callouts import CALLOUT_ICONS


class TestResolveIcon:
    """Tests for the icon resolver."""

    def test_valid_lucide_ref(self):
        svg = resolve_icon("lucide:info")
        assert svg is not None
        assert "<svg" in svg
        assert "currentColor" in svg

    def test_unknown_icon_name(self):
        assert resolve_icon("lucide:nonexistent-zzz-xyz") is None

    def test_unknown_library(self):
        assert resolve_icon("fakelib:info") is None

    def test_invalid_format_no_colon(self):
        assert resolve_icon("justAName") is None

    def test_empty_string(self):
        assert resolve_icon("") is None

    def test_all_callout_icons_resolve(self):
        for callout_type, ref in CALLOUT_ICONS.items():
            svg = resolve_icon(ref)
            assert svg is not None, f"{callout_type} -> {ref} failed"
            assert "<svg" in svg

    def test_svg_has_viewbox(self):
        svg = resolve_icon("lucide:info")
        assert 'viewBox="0 0 24 24"' in svg

    def test_icons_beyond_original_twelve(self):
        """ZIP bundle contains the full Lucide set, not just 12 icons."""
        extras = ["settings", "award", "bell", "camera", "database", "globe"]
        for name in extras:
            svg = resolve_icon(f"lucide:{name}")
            assert svg is not None, f"lucide:{name} should be in the full set"
            assert "<svg" in svg


class TestLoadLucideIcon:
    """Tests for the lucide loader directly."""

    def test_load_from_zip(self):
        svg = load_lucide_icon("info")
        assert svg is not None
        assert "<svg" in svg

    def test_load_nonexistent(self):
        assert load_lucide_icon("not-a-real-icon-xyz") is None


class TestProjectLocalOverride:
    """Tests for project-local icon override via icons_dir."""

    def test_override_takes_precedence(self, tmp_path):
        override_dir = tmp_path / "lucide"
        override_dir.mkdir()
        (override_dir / "info.svg").write_text('<svg id="custom">override</svg>')

        svg = load_lucide_icon("info", icons_dir=tmp_path)
        assert svg == '<svg id="custom">override</svg>'

    def test_falls_back_to_zip_when_not_overridden(self, tmp_path):
        override_dir = tmp_path / "lucide"
        override_dir.mkdir()
        # No info.svg in override dir
        svg = load_lucide_icon("info", icons_dir=tmp_path)
        assert svg is not None
        assert "<svg" in svg
        assert "custom" not in svg

    def test_configure_icons_dir_wires_through(self, tmp_path):
        override_dir = tmp_path / "lucide"
        override_dir.mkdir()
        (override_dir / "info.svg").write_text('<svg id="configured">test</svg>')

        try:
            configure_icons_dir(tmp_path)
            svg = resolve_icon("lucide:info")
            assert svg == '<svg id="configured">test</svg>'
        finally:
            configure_icons_dir(None)
