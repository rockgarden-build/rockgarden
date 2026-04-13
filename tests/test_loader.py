"""Tests for content loader folder note detection."""

from pathlib import Path

import pytest

from rockgarden.content.loader import load_content, load_folder_metas, load_page


@pytest.fixture
def source_dir(tmp_path):
    """Create a temporary source directory."""
    return tmp_path / "source"


def _write_page(source: Path, rel_path: str, content: str = "") -> Path:
    """Write a markdown file and return its path."""
    path = source / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


class TestFolderNoteSlugRewrite:
    def test_basic_folder_note(self, source_dir):
        """Fairshore/Fairshore.md should get slug rewritten to index."""
        path = _write_page(source_dir, "Fairshore/Fairshore.md")
        page = load_page(path, source_dir)
        assert page.slug == "fairshore/index"

    def test_source_path_preserved(self, source_dir):
        """Source path should remain the original file path."""
        path = _write_page(source_dir, "Fairshore/Fairshore.md")
        page = load_page(path, source_dir)
        assert page.source_path == path

    def test_root_page_not_detected(self, source_dir):
        """A page at the source root should not be treated as a folder note."""
        path = _write_page(source_dir, "about.md")
        page = load_page(path, source_dir)
        assert page.slug == "about"

    def test_non_matching_not_rewritten(self, source_dir):
        """A page whose name differs from parent folder is not rewritten."""
        path = _write_page(source_dir, "Fairshore/The Salty Dog.md")
        page = load_page(path, source_dir)
        assert page.slug == "fairshore/the-salty-dog"

    def test_custom_slug_overrides(self, source_dir):
        """Custom slug in frontmatter bypasses folder note detection."""
        path = _write_page(
            source_dir,
            "Fairshore/Fairshore.md",
            "---\nslug: my-custom-slug\n---\n",
        )
        page = load_page(path, source_dir)
        assert page.slug == "my-custom-slug"

    def test_nested_folder_note(self, source_dir):
        """Deeply nested folder note: a/a/a.md -> a/a/index."""
        (source_dir / "a" / "a").mkdir(parents=True, exist_ok=True)
        path = _write_page(source_dir, "a/a/a.md")
        page = load_page(path, source_dir)
        assert page.slug == "a/a/index"

    def test_index_md_not_rewritten(self, source_dir):
        """An actual index.md should not be double-rewritten."""
        path = _write_page(source_dir, "Fairshore/index.md")
        page = load_page(path, source_dir)
        assert page.slug == "fairshore/index"


class TestFolderNoteConflict:
    def test_index_md_wins_over_folder_note(self, source_dir):
        """When both folder note and index.md exist, index.md wins."""
        _write_page(source_dir, "Fairshore/Fairshore.md", "folder note content")
        _write_page(source_dir, "Fairshore/index.md", "index content")

        pages = load_content(source_dir, [])
        index_pages = [p for p in pages if p.slug == "fairshore/index"]
        assert len(index_pages) == 1
        assert index_pages[0].source_path.name == "index.md"

        folder_notes = [p for p in pages if p.source_path.name == "Fairshore.md"]
        assert len(folder_notes) == 1
        assert folder_notes[0].slug == "fairshore/fairshore"

    def test_conflict_emits_warning(self, source_dir, caplog):
        """Conflict between folder note and index.md should emit a warning."""
        _write_page(source_dir, "Fairshore/Fairshore.md")
        _write_page(source_dir, "Fairshore/index.md")

        with caplog.at_level("WARNING", logger="rockgarden.content.loader"):
            load_content(source_dir, [])
        assert "index.md" in caplog.text
        assert "folder page" in caplog.text


class TestFolderMetaLoading:
    def test_folder_md_not_loaded_as_page(self, source_dir):
        """`_folder.md` files should not appear in loaded pages."""
        _write_page(source_dir, "blog/_folder.md", "---\nnav_order: 1\n---\n")
        _write_page(source_dir, "blog/post.md", "# Post")

        pages = load_content(source_dir, [])
        slugs = [p.slug for p in pages]
        assert "blog/_folder" not in slugs
        assert "blog/post" in slugs

    def test_folder_md_metadata_loaded(self, source_dir):
        """`_folder.md` frontmatter is loaded into FolderMeta."""
        _write_page(
            source_dir,
            "blog/_folder.md",
            "---\nnav_order: 2\nlabel: Blog Posts\nsort: alphabetical\n---\n",
        )
        _write_page(source_dir, "blog/post.md", "# Post")

        metas = load_folder_metas(source_dir, [])
        assert "blog" in metas
        assert metas["blog"].nav_order == 2
        assert metas["blog"].label == "Blog Posts"
        assert metas["blog"].sort == "alphabetical"

    def test_root_folder_meta(self, source_dir):
        """A `_folder.md` at the source root is keyed by empty string."""
        _write_page(source_dir, "_folder.md", "---\nlabel: Site\n---\n")

        metas = load_folder_metas(source_dir, [])
        assert "" in metas
        assert metas[""].label == "Site"

    def test_nested_folder_meta(self, source_dir):
        """Folder metas are keyed by forward-slash-joined folder path."""
        _write_page(source_dir, "a/b/c/_folder.md", "---\nnav_order: 3\n---\n")

        metas = load_folder_metas(source_dir, [])
        assert "a/b/c" in metas
        assert metas["a/b/c"].nav_order == 3

    def test_empty_folder_meta(self, source_dir):
        """`_folder.md` with no frontmatter loads as empty FolderMeta."""
        _write_page(source_dir, "blog/_folder.md", "just a body, no frontmatter")

        metas = load_folder_metas(source_dir, [])
        assert "blog" in metas
        assert metas["blog"].nav_order is None
        assert metas["blog"].unlisted is False
