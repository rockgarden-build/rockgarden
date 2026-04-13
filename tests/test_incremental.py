"""Integration tests for incremental builds."""

from pathlib import Path

from rockgarden.config import Config
from rockgarden.output.builder import build_site


def _write_page(source: Path, slug: str, content: str = "") -> Path:
    page = source / f"{slug}.md"
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(content or f"# {slug}\n\nContent for {slug}.\n")
    return page


def _build(source: Path, output: Path, incremental: bool = True, **kwargs):
    config = Config.load(None)
    return build_site(
        config,
        source,
        output,
        project_root=source.parent,
        incremental=incremental,
        **kwargs,
    )


class TestIncrementalBuilds:
    def test_first_build_creates_manifest(self, tmp_path):
        source = tmp_path / "content"
        source.mkdir()
        _write_page(source, "about")
        output = tmp_path / "output"

        result = _build(source, output)
        manifest_path = source.parent / ".rockgarden" / "build-manifest.json"
        assert manifest_path.exists()
        assert result.skipped_count == 0

    def test_second_build_skips_unchanged(self, tmp_path):
        source = tmp_path / "content"
        source.mkdir()
        _write_page(source, "about")
        _write_page(source, "contact")
        output = tmp_path / "output"

        _build(source, output)
        result = _build(source, output)
        assert result.skipped_count == 2

    def test_edited_page_rebuilds(self, tmp_path):
        source = tmp_path / "content"
        source.mkdir()
        page = _write_page(source, "about")
        _write_page(source, "contact")
        output = tmp_path / "output"

        _build(source, output)

        page.write_text("# About\n\nUpdated content.\n")
        result = _build(source, output)
        assert result.skipped_count == 1

        html = (output / "about" / "index.html").read_text()
        assert "Updated content" in html

    def test_folder_meta_change_triggers_full_rebuild(self, tmp_path):
        source = tmp_path / "content"
        source.mkdir()
        (source / "blog").mkdir()
        _write_page(source, "blog/post-one")
        _write_page(source, "blog/post-two")
        output = tmp_path / "output"

        # Initial build with an unlisted blog folder.
        (source / "blog" / "_folder.md").write_text("---\nunlisted: true\n---\n")
        _build(source, output)

        # Flip the folder to visible; all pages must re-render because folder
        # metadata affects every page's nav.
        (source / "blog" / "_folder.md").write_text("---\nnav_order: 1\n---\n")
        result = _build(source, output)
        assert result.skipped_count == 0

    def test_config_change_triggers_full_rebuild(self, tmp_path):
        source = tmp_path / "content"
        source.mkdir()
        _write_page(source, "about")
        _write_page(source, "contact")
        output = tmp_path / "output"

        config_file = tmp_path / "rockgarden.toml"
        config_file.write_text("")
        _build(source, output, config_path=config_file)

        config_file.write_text('[site]\ntitle = "Changed"\n')
        result = _build(source, output, config_path=config_file)
        assert result.skipped_count == 0

    def test_deleted_output_dir_triggers_full_rebuild(self, tmp_path):
        source = tmp_path / "content"
        source.mkdir()
        _write_page(source, "about")
        output = tmp_path / "output"

        _build(source, output)

        import shutil

        shutil.rmtree(output)
        result = _build(source, output)
        assert result.skipped_count == 0

    def test_added_page_triggers_full_rebuild(self, tmp_path):
        source = tmp_path / "content"
        source.mkdir()
        _write_page(source, "about")
        output = tmp_path / "output"

        _build(source, output)

        _write_page(source, "new-page")
        result = _build(source, output)
        assert result.skipped_count == 0

    def test_removed_page_triggers_full_rebuild(self, tmp_path):
        source = tmp_path / "content"
        source.mkdir()
        _write_page(source, "about")
        page2 = _write_page(source, "contact")
        output = tmp_path / "output"

        _build(source, output)

        page2.unlink()
        result = _build(source, output)
        assert result.skipped_count == 0

    def test_non_incremental_build_ignores_manifest(self, tmp_path):
        source = tmp_path / "content"
        source.mkdir()
        _write_page(source, "about")
        output = tmp_path / "output"

        _build(source, output, incremental=True)
        result = _build(source, output, incremental=False)
        assert result.skipped_count == 0

    def test_non_incremental_build_does_not_write_manifest(self, tmp_path):
        source = tmp_path / "content"
        source.mkdir()
        _write_page(source, "about")
        output = tmp_path / "output"

        _build(source, output, incremental=False)
        manifest_path = source.parent / ".rockgarden" / "build-manifest.json"
        assert not manifest_path.exists()

    def test_renamed_page_cleans_stale_output(self, tmp_path):
        source = tmp_path / "content"
        source.mkdir()
        old_page = _write_page(source, "about")
        output = tmp_path / "output"

        _build(source, output)
        assert (output / "about" / "index.html").exists()

        old_page.rename(source / "about-us.md")
        _build(source, output)
        assert not (output / "about" / "index.html").exists()
        assert (output / "about-us" / "index.html").exists()
