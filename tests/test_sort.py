"""Tests for sort resolution."""

from rockgarden.config import FolderSortOverride, NavConfig
from rockgarden.nav.sort import resolve_sort


class TestResolveSort:
    def test_global_defaults(self):
        config = NavConfig()
        result = resolve_sort("blog", config)
        assert result.sort == "files-first"
        assert result.reverse is False

    def test_global_custom(self):
        config = NavConfig(sort="alphabetical", reverse=True)
        result = resolve_sort("blog", config)
        assert result.sort == "alphabetical"
        assert result.reverse is True

    def test_config_override(self):
        config = NavConfig(
            sort="files-first",
            reverse=False,
            overrides={"blog": FolderSortOverride(sort="date", reverse=True)},
        )
        result = resolve_sort("blog", config)
        assert result.sort == "date"
        assert result.reverse is True

    def test_config_override_partial_sort_only(self):
        config = NavConfig(
            reverse=True,
            overrides={"blog": FolderSortOverride(sort="alphabetical")},
        )
        result = resolve_sort("blog", config)
        assert result.sort == "alphabetical"
        assert result.reverse is True  # inherited from global

    def test_config_override_partial_reverse_only(self):
        config = NavConfig(
            sort="folders-first",
            overrides={"blog": FolderSortOverride(reverse=True)},
        )
        result = resolve_sort("blog", config)
        assert result.sort == "folders-first"  # inherited from global
        assert result.reverse is True

    def test_config_override_unmatched_folder(self):
        config = NavConfig(
            overrides={"blog": FolderSortOverride(sort="date")},
        )
        result = resolve_sort("docs", config)
        assert result.sort == "files-first"

    def test_frontmatter_overrides_config(self):
        config = NavConfig(
            overrides={"blog": FolderSortOverride(sort="alphabetical", reverse=False)},
        )
        fm = {"sort": "date", "sort_reverse": True}
        result = resolve_sort("blog", config, fm)
        assert result.sort == "date"
        assert result.reverse is True

    def test_frontmatter_partial_sort_only(self):
        config = NavConfig(
            reverse=True,
            overrides={"blog": FolderSortOverride(reverse=False)},
        )
        fm = {"sort": "date"}
        result = resolve_sort("blog", config, fm)
        assert result.sort == "date"
        assert result.reverse is False  # from config override

    def test_frontmatter_partial_reverse_only(self):
        config = NavConfig(sort="alphabetical")
        fm = {"sort_reverse": True}
        result = resolve_sort("docs", config, fm)
        assert result.sort == "alphabetical"  # from global
        assert result.reverse is True

    def test_normalizes_slashes(self):
        config = NavConfig(
            overrides={"blog": FolderSortOverride(sort="date")},
        )
        result = resolve_sort("/blog/", config)
        assert result.sort == "date"
