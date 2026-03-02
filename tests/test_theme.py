import os
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from rockgarden.cli import app
from rockgarden.theme import set_theme_name_in_config, validate_theme_name

runner = CliRunner()


# ---------------------------------------------------------------------------
# validate_theme_name
# ---------------------------------------------------------------------------


def test_validate_theme_name_valid():
    validate_theme_name("default")
    validate_theme_name("my-theme")
    validate_theme_name("my_theme")
    validate_theme_name("Theme123")


def test_validate_theme_name_rejects_quotes():
    with pytest.raises(ValueError, match="Invalid theme name"):
        validate_theme_name('my"theme')


def test_validate_theme_name_rejects_spaces():
    with pytest.raises(ValueError, match="Invalid theme name"):
        validate_theme_name("my theme")


def test_validate_theme_name_rejects_special_chars():
    with pytest.raises(ValueError, match="Invalid theme name"):
        validate_theme_name("my/theme")


# ---------------------------------------------------------------------------
# set_theme_name_in_config
# ---------------------------------------------------------------------------


def test_set_theme_name_updates_existing_name(tmp_path):
    config = tmp_path / "rockgarden.toml"
    config.write_text('[site]\ntitle = "Test"\n\n[theme]\nname = "old"\n')
    set_theme_name_in_config(config, "new")
    content = config.read_text()
    assert 'name = "new"' in content
    assert 'name = "old"' not in content


def test_set_theme_name_inserts_under_existing_theme_section(tmp_path):
    config = tmp_path / "rockgarden.toml"
    config.write_text('[site]\ntitle = "Test"\n\n[theme]\ntoc = true\n')
    set_theme_name_in_config(config, "mytheme")
    content = config.read_text()
    assert 'name = "mytheme"' in content
    lines = content.splitlines()
    theme_idx = lines.index("[theme]")
    name_idx = next(i for i, l in enumerate(lines) if 'name = "mytheme"' in l)
    assert name_idx == theme_idx + 1


def test_set_theme_name_appends_new_theme_section(tmp_path):
    config = tmp_path / "rockgarden.toml"
    config.write_text('[site]\ntitle = "Test"\n')
    set_theme_name_in_config(config, "mytheme")
    content = config.read_text()
    assert "[theme]" in content
    assert 'name = "mytheme"' in content


# ---------------------------------------------------------------------------
# theme export CLI command
# ---------------------------------------------------------------------------


def test_theme_export_creates_files(tmp_path):
    original = Path.cwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["theme", "export"])
        assert result.exit_code == 0, result.output
        dest = tmp_path / "_themes" / "default"
        assert dest.exists()
        assert (dest / "base.html").exists()
        assert (dest / "page.html").exists()
        assert (dest / "layouts" / "default.html").exists()
        assert (dest / "components").is_dir()
        assert (dest / "static" / "rockgarden.css").exists()
        assert (dest / "static-src" / "input.css").exists()
        assert (dest / "tailwind.config.js").exists()
        assert (dest / "package.json").exists()
        assert (dest / "theme.toml").exists()
    finally:
        os.chdir(original)


def test_theme_export_custom_dir(tmp_path):
    original = Path.cwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["theme", "export", "--dir", "pyohio"])
        assert result.exit_code == 0, result.output
        assert (tmp_path / "_themes" / "pyohio").exists()
        assert (tmp_path / "_themes" / "pyohio" / "theme.toml").exists()
    finally:
        os.chdir(original)


def test_theme_export_errors_if_dir_exists(tmp_path):
    original = Path.cwd()
    try:
        os.chdir(tmp_path)
        (tmp_path / "_themes" / "default").mkdir(parents=True)
        result = runner.invoke(app, ["theme", "export"])
        assert result.exit_code == 1
        assert "already exists" in result.output
    finally:
        os.chdir(original)


def test_theme_export_rejects_invalid_name(tmp_path):
    original = Path.cwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["theme", "export", "--dir", 'bad"name'])
        assert result.exit_code == 1
        assert "Invalid theme name" in result.output
    finally:
        os.chdir(original)


def test_theme_export_updates_config(tmp_path):
    original = Path.cwd()
    try:
        os.chdir(tmp_path)
        (tmp_path / "rockgarden.toml").write_text('[site]\ntitle = "Test"\n')
        result = runner.invoke(app, ["theme", "export"])
        assert result.exit_code == 0, result.output
        config_content = (tmp_path / "rockgarden.toml").read_text()
        assert 'name = "default"' in config_content
    finally:
        os.chdir(original)


def test_theme_export_notes_missing_config(tmp_path):
    original = Path.cwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["theme", "export"])
        assert result.exit_code == 0, result.output
        assert "No rockgarden.toml" in result.output
    finally:
        os.chdir(original)
