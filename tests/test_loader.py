"""Tests for content loader folder note detection."""

from pathlib import Path

import pytest

from rockgarden.content.loader import load_content, load_page


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

    def test_conflict_emits_warning(self, source_dir, capsys):
        """Conflict between folder note and index.md should emit a warning."""
        _write_page(source_dir, "Fairshore/Fairshore.md")
        _write_page(source_dir, "Fairshore/index.md")

        load_content(source_dir, [])
        captured = capsys.readouterr()
        assert "index.md" in captured.err
        assert "folder page" in captured.err
