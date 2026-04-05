"""Tests for the file watcher."""

from watchfiles import Change

from rockgarden.server.watcher import classify_changes


def test_classify_content_only_change(tmp_path):
    source = tmp_path / "content"
    source.mkdir()
    changes = {(Change.modified, str(source / "page.md"))}
    assert classify_changes(changes, source) is False


def test_classify_template_change_triggers_full(tmp_path):
    source = tmp_path / "content"
    source.mkdir()
    templates = tmp_path / "_templates"
    templates.mkdir()
    changes = {(Change.modified, str(templates / "page.html"))}
    assert classify_changes(changes, source) is True


def test_classify_config_change_triggers_full(tmp_path):
    source = tmp_path / "content"
    source.mkdir()
    changes = {(Change.modified, str(tmp_path / "rockgarden.toml"))}
    assert classify_changes(changes, source) is True


def test_classify_mixed_changes(tmp_path):
    source = tmp_path / "content"
    source.mkdir()
    changes = {
        (Change.modified, str(source / "page.md")),
        (Change.modified, str(tmp_path / "_macros" / "macro.html")),
    }
    assert classify_changes(changes, source) is True


def test_classify_macro_change_triggers_full(tmp_path):
    source = tmp_path / "content"
    source.mkdir()
    changes = {(Change.modified, str(tmp_path / "_macros" / "nav.html"))}
    assert classify_changes(changes, source) is True
