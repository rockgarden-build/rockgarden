"""Tests for icon resolution."""

from rockgarden.icons import resolve_icon
from rockgarden.obsidian.callouts import CALLOUT_ICONS


class TestResolveIcon:
    """Tests for the icon resolver."""

    def test_valid_lucide_ref(self):
        svg = resolve_icon("lucide:info")
        assert svg is not None
        assert "<svg" in svg
        assert "currentColor" in svg

    def test_unknown_icon_name(self):
        assert resolve_icon("lucide:nonexistent") is None

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

    def test_each_bundled_icon_loads(self):
        names = [
            "info", "clipboard-list", "lightbulb", "flame",
            "check", "circle-help", "triangle-alert", "x",
            "zap", "bug", "list", "quote",
        ]
        for name in names:
            svg = resolve_icon(f"lucide:{name}")
            assert svg is not None, f"lucide:{name} failed to load"
            assert "<svg" in svg
