"""Tests for build manifest."""

import json

from rockgarden.output.manifest import (
    BuildManifest,
    PageManifestEntry,
    compute_folder_meta_hash,
    hash_directory,
    hash_file,
)


class TestHashFile:
    def test_consistent_hash(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("hello world")
        assert hash_file(f) == hash_file(f)

    def test_different_content_different_hash(self, tmp_path):
        f1 = tmp_path / "a.md"
        f1.write_text("hello")
        f2 = tmp_path / "b.md"
        f2.write_text("world")
        assert hash_file(f1) != hash_file(f2)


class TestHashDirectory:
    def test_stable_hash(self, tmp_path):
        (tmp_path / "a.txt").write_text("aaa")
        (tmp_path / "b.txt").write_text("bbb")
        assert hash_directory(tmp_path) == hash_directory(tmp_path)

    def test_changes_when_file_changes(self, tmp_path):
        (tmp_path / "a.txt").write_text("aaa")
        h1 = hash_directory(tmp_path)
        (tmp_path / "a.txt").write_text("modified")
        h2 = hash_directory(tmp_path)
        assert h1 != h2

    def test_changes_when_file_added(self, tmp_path):
        (tmp_path / "a.txt").write_text("aaa")
        h1 = hash_directory(tmp_path)
        (tmp_path / "b.txt").write_text("bbb")
        h2 = hash_directory(tmp_path)
        assert h1 != h2

    def test_empty_dir(self, tmp_path):
        h = hash_directory(tmp_path)
        assert isinstance(h, str) and len(h) == 64

    def test_nonexistent_dir(self, tmp_path):
        h = hash_directory(tmp_path / "missing")
        assert isinstance(h, str) and len(h) == 64


class TestBuildManifest:
    def _make_manifest(self):
        return BuildManifest(
            config_hash="cfg123",
            template_hash="tpl456",
            macro_hash="mac789",
            output_dir="/tmp/out",
            page_count=2,
            pages={
                "about": PageManifestEntry(
                    content_hash="hash_about", output_path="about/index.html"
                ),
                "blog/post": PageManifestEntry(
                    content_hash="hash_post", output_path="blog/post/index.html"
                ),
            },
        )

    def test_load_missing_file(self, tmp_path):
        assert BuildManifest.load(tmp_path / "missing.json") is None

    def test_load_invalid_json(self, tmp_path):
        f = tmp_path / "manifest.json"
        f.write_text("not json{{{")
        assert BuildManifest.load(f) is None

    def test_load_wrong_version(self, tmp_path):
        f = tmp_path / "manifest.json"
        f.write_text(json.dumps({"version": 999}))
        assert BuildManifest.load(f) is None

    def test_save_and_load_round_trip(self, tmp_path):
        m = self._make_manifest()
        path = tmp_path / "manifest.json"
        m.save(path)

        loaded = BuildManifest.load(path)
        assert loaded is not None
        assert loaded.config_hash == "cfg123"
        assert loaded.template_hash == "tpl456"
        assert loaded.macro_hash == "mac789"
        assert loaded.output_dir == "/tmp/out"
        assert loaded.page_count == 2
        assert loaded.pages["about"].content_hash == "hash_about"
        assert loaded.pages["blog/post"].output_path == "blog/post/index.html"

    def test_is_page_dirty_unknown_slug(self, tmp_path):
        m = self._make_manifest()
        assert m.is_page_dirty("unknown", "anyhash", tmp_path) is True

    def test_is_page_dirty_changed_hash(self, tmp_path):
        m = self._make_manifest()
        (tmp_path / "about" / "index.html").parent.mkdir(parents=True)
        (tmp_path / "about" / "index.html").write_text("<html>")
        assert m.is_page_dirty("about", "different_hash", tmp_path) is True

    def test_is_page_dirty_missing_output(self, tmp_path):
        m = self._make_manifest()
        assert m.is_page_dirty("about", "hash_about", tmp_path) is True

    def test_is_page_clean(self, tmp_path):
        m = self._make_manifest()
        (tmp_path / "about" / "index.html").parent.mkdir(parents=True)
        (tmp_path / "about" / "index.html").write_text("<html>")
        assert m.is_page_dirty("about", "hash_about", tmp_path) is False

    def test_needs_full_rebuild_config_changed(self):
        m = self._make_manifest()
        assert m.needs_full_rebuild("CHANGED", "tpl456", "mac789", "/tmp/out", 2)

    def test_needs_full_rebuild_template_changed(self):
        m = self._make_manifest()
        assert m.needs_full_rebuild("cfg123", "CHANGED", "mac789", "/tmp/out", 2)

    def test_needs_full_rebuild_macro_changed(self):
        m = self._make_manifest()
        assert m.needs_full_rebuild("cfg123", "tpl456", "CHANGED", "/tmp/out", 2)

    def test_needs_full_rebuild_output_dir_changed(self):
        m = self._make_manifest()
        assert m.needs_full_rebuild("cfg123", "tpl456", "mac789", "/tmp/other", 2)

    def test_needs_full_rebuild_page_count_changed(self):
        m = self._make_manifest()
        assert m.needs_full_rebuild("cfg123", "tpl456", "mac789", "/tmp/out", 5)

    def test_needs_full_rebuild_output_dir_missing(self, tmp_path):
        m = BuildManifest(
            config_hash="c",
            template_hash="t",
            macro_hash="m",
            output_dir=str(tmp_path / "missing"),
            page_count=0,
        )
        assert m.needs_full_rebuild("c", "t", "m", str(tmp_path / "missing"), 0)

    def test_no_full_rebuild_when_unchanged(self, tmp_path):
        out = tmp_path / "out"
        out.mkdir()
        m = BuildManifest(
            config_hash="c",
            template_hash="t",
            macro_hash="m",
            output_dir=str(out),
            page_count=3,
        )
        assert not m.needs_full_rebuild("c", "t", "m", str(out), 3)


class TestComputeFolderMetaHash:
    def test_includes_folder_md_content(self, tmp_path):
        (tmp_path / "blog").mkdir()
        (tmp_path / "blog" / "_folder.md").write_text("---\nnav_order: 1\n---\n")
        h1 = compute_folder_meta_hash(tmp_path, [])

        (tmp_path / "blog" / "_folder.md").write_text("---\nnav_order: 2\n---\n")
        h2 = compute_folder_meta_hash(tmp_path, [])
        assert h1 != h2

    def test_skips_ignored_directories(self, tmp_path):
        (tmp_path / "blog").mkdir()
        (tmp_path / "blog" / "_folder.md").write_text("---\nnav_order: 1\n---\n")
        (tmp_path / ".obsidian").mkdir()
        (tmp_path / ".obsidian" / "_folder.md").write_text("---\nnav_order: 1\n---\n")

        h1 = compute_folder_meta_hash(tmp_path, [".obsidian"])

        # Changing an ignored _folder.md must not affect the hash.
        (tmp_path / ".obsidian" / "_folder.md").write_text("---\nnav_order: 99\n---\n")
        h2 = compute_folder_meta_hash(tmp_path, [".obsidian"])
        assert h1 == h2

    def test_empty_source(self, tmp_path):
        h = compute_folder_meta_hash(tmp_path, [])
        assert isinstance(h, str) and len(h) == 64
