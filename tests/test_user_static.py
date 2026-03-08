"""Tests for user-level _static/ directory support."""

from pathlib import Path

from rockgarden.output.builder import copy_user_static_files


def test_no_static_dir(tmp_path: Path) -> None:
    output = tmp_path / "output"
    output.mkdir()
    copy_user_static_files(tmp_path, output)
    assert list(output.iterdir()) == []


def test_copies_single_file(tmp_path: Path) -> None:
    static = tmp_path / "_static"
    static.mkdir()
    (static / "_redirects").write_text("/old /new 301\n")

    output = tmp_path / "output"
    output.mkdir()
    copy_user_static_files(tmp_path, output)

    assert (output / "_redirects").read_text() == "/old /new 301\n"


def test_copies_nested_directories(tmp_path: Path) -> None:
    static = tmp_path / "_static"
    (static / "subdir").mkdir(parents=True)
    (static / "subdir" / "file.txt").write_text("nested")

    output = tmp_path / "output"
    output.mkdir()
    copy_user_static_files(tmp_path, output)

    assert (output / "subdir" / "file.txt").read_text() == "nested"


def test_overwrites_existing_output(tmp_path: Path) -> None:
    output = tmp_path / "output"
    output.mkdir()
    (output / "robots.txt").write_text("old")

    static = tmp_path / "_static"
    static.mkdir()
    (static / "robots.txt").write_text("new")

    copy_user_static_files(tmp_path, output)
    assert (output / "robots.txt").read_text() == "new"


def test_preserves_existing_output_files(tmp_path: Path) -> None:
    output = tmp_path / "output"
    output.mkdir()
    (output / "index.html").write_text("<html>")

    static = tmp_path / "_static"
    static.mkdir()
    (static / "_redirects").write_text("/old /new 301\n")

    copy_user_static_files(tmp_path, output)

    assert (output / "index.html").read_text() == "<html>"
    assert (output / "_redirects").exists()
