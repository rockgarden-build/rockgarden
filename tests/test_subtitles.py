"""Tests for subtitle support in nav and search."""

import json
from pathlib import Path

from rockgarden.config import Config, FolderSortOverride, NavConfig, SiteConfig
from rockgarden.content import FolderMeta, Page
from rockgarden.nav import build_nav_tree
from rockgarden.nav.sort import resolve_show_subtitles
from rockgarden.output.builder import build_site
from rockgarden.output.search import build_search_index


def make_page(slug: str, **frontmatter) -> Page:
    return Page(
        source_path=Path(f"/vault/{slug}.md"),
        slug=slug,
        frontmatter=frontmatter,
        content="",
    )


def make_meta(folder_path: str, **fields) -> FolderMeta:
    return FolderMeta(
        source_path=Path(f"/vault/{folder_path}/_folder.md"),
        folder_path=folder_path,
        frontmatter=dict(fields),
    )


def find(node, name):
    return next(c for c in node.children if c.name == name)


class TestPageSubtitle:
    def test_from_frontmatter(self):
        assert make_page("a", subtitle="Sub").subtitle == "Sub"

    def test_missing_is_empty(self):
        assert make_page("a").subtitle == ""

    def test_null_is_empty(self):
        assert make_page("a", subtitle=None).subtitle == ""


class TestResolveShowSubtitles:
    def test_default_true(self):
        assert resolve_show_subtitles("logs", NavConfig()) is True

    def test_global_false(self):
        assert resolve_show_subtitles("logs", NavConfig(show_subtitles=False)) is False

    def test_config_override(self):
        config = NavConfig(overrides={"logs": FolderSortOverride(show_subtitles=False)})
        assert resolve_show_subtitles("logs", config) is False
        assert resolve_show_subtitles("other", config) is True

    def test_folder_meta_beats_config(self):
        config = NavConfig(show_subtitles=False)
        assert resolve_show_subtitles(
            "logs", config, {"logs": make_meta("logs", show_subtitles=True)}
        )


class TestNavSubtitles:
    def test_page_subtitle_on_node(self):
        tree = build_nav_tree([make_page("logs/s1", subtitle="The Elves Arrive")])
        assert find(find(tree, "logs"), "s1").subtitle == "The Elves Arrive"

    def test_global_off(self):
        tree = build_nav_tree(
            [make_page("logs/s1", subtitle="X")],
            config=NavConfig(show_subtitles=False),
        )
        assert find(find(tree, "logs"), "s1").subtitle == ""

    def test_folder_meta_off_inherits_to_descendants(self):
        pages = [
            make_page("docs/a", subtitle="A"),
            make_page("docs/sub/b", subtitle="B"),
        ]
        metas = {"docs": make_meta("docs", show_subtitles=False)}
        tree = build_nav_tree(pages, folder_metas=metas)
        docs = find(tree, "docs")
        assert find(docs, "a").subtitle == ""
        assert find(find(docs, "sub"), "b").subtitle == ""

    def test_descendant_setting_beats_ancestor(self):
        pages = [
            make_page("docs/a", subtitle="A"),
            make_page("docs/sub/b", subtitle="B"),
        ]
        metas = {
            "docs": make_meta("docs", show_subtitles=False),
            "docs/sub": make_meta("docs/sub", show_subtitles=True),
        }
        tree = build_nav_tree(pages, folder_metas=metas)
        docs = find(tree, "docs")
        assert find(docs, "a").subtitle == ""
        assert find(find(docs, "sub"), "b").subtitle == "B"

    def test_folder_subtitle_from_index_page(self):
        pages = [make_page("logs/index", subtitle="Index Sub"), make_page("logs/a")]
        tree = build_nav_tree(pages)
        assert find(tree, "logs").subtitle == "Index Sub"

    def test_folder_meta_subtitle_beats_index_page(self):
        pages = [make_page("logs/index", subtitle="Index Sub"), make_page("logs/a")]
        metas = {"logs": make_meta("logs", subtitle="Meta Sub")}
        tree = build_nav_tree(pages, folder_metas=metas)
        assert find(tree, "logs").subtitle == "Meta Sub"


class TestSearchSubtitles:
    def test_index_includes_subtitle(self):
        index = build_search_index([make_page("a", subtitle="Sub")])
        assert index[0]["subtitle"] == "Sub"

    def test_index_omits_empty_subtitle(self):
        index = build_search_index([make_page("a")])
        assert "subtitle" not in index[0]


def test_build_renders_nav_and_search_subtitle(tmp_path):
    source = tmp_path / "content"
    (source / "logs").mkdir(parents=True)
    (source / "logs" / "s1.md").write_text(
        "---\ntitle: Session 1\nsubtitle: The Elves Arrive\n---\n\nBody.\n"
    )
    output = tmp_path / "output"
    config = Config(site=SiteConfig(source=source, output=output))
    build_site(config, source, output)

    html = (output / "logs" / "s1" / "index.html").read_text()
    assert '<span class="nav-subtitle' in html
    assert "The Elves Arrive</span>" in html

    index = json.loads((output / "search-index.json").read_text())
    assert index[0]["subtitle"] == "The Elves Arrive"
