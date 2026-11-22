"""Tests for sort resolution."""

from pathlib import Path

from rockgarden.config import FolderSortOverride, NavConfig
from rockgarden.content import FolderMeta
from rockgarden.nav.sort import resolve_sort


def metas(**by_path: dict) -> dict[str, FolderMeta]:
    """Build a folder_metas map from {path: frontmatter}."""
    return {
        path: FolderMeta(
            source_path=Path(f"/vault/{path}/_folder.md"),
            folder_path=path,
            frontmatter=fm,
        )
        for path, fm in by_path.items()
    }


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
        result = resolve_sort("blog", config, metas(blog=fm))
        assert result.sort == "date"
        assert result.reverse is True

    def test_frontmatter_partial_sort_only(self):
        config = NavConfig(
            reverse=True,
            overrides={"blog": FolderSortOverride(reverse=False)},
        )
        fm = {"sort": "date"}
        result = resolve_sort("blog", config, metas(blog=fm))
        assert result.sort == "date"
        assert result.reverse is False  # from config override

    def test_frontmatter_partial_reverse_only(self):
        config = NavConfig(sort="alphabetical")
        fm = {"sort_reverse": True}
        result = resolve_sort("docs", config, metas(docs=fm))
        assert result.sort == "alphabetical"  # from global
        assert result.reverse is True

    def test_normalizes_slashes(self):
        config = NavConfig(
            overrides={"blog": FolderSortOverride(sort="date")},
        )
        result = resolve_sort("/blog/", config)
        assert result.sort == "date"


class TestResolveSortInheritance:
    def test_folder_meta_inherits_to_descendants(self):
        m = metas(blog={"sort": "alphabetical", "sort_reverse": True})
        result = resolve_sort("blog/2025/q1", NavConfig(), m)
        assert result.sort == "alphabetical"
        assert result.reverse is True

    def test_config_override_inherits_to_descendants(self):
        config = NavConfig(overrides={"blog": FolderSortOverride(sort="date")})
        assert resolve_sort("blog/2025", config).sort == "date"

    def test_deeper_setting_wins(self):
        m = metas(blog={"sort": "alphabetical"}, **{"blog/2025": {"sort": "date"}})
        assert resolve_sort("blog/2025", NavConfig(), m).sort == "date"
        assert resolve_sort("blog/2024", NavConfig(), m).sort == "alphabetical"

    def test_deeper_config_override_beats_ancestor_folder_meta(self):
        config = NavConfig(overrides={"blog/2025": FolderSortOverride(sort="date")})
        m = metas(blog={"sort": "alphabetical"})
        assert resolve_sort("blog/2025", config, m).sort == "date"

    def test_prefix_is_not_ancestor(self):
        m = metas(blog={"sort": "date"})
        assert resolve_sort("blogroll", NavConfig(), m).sort == "files-first"
