"""Tests for theme export functionality."""

import tomllib

import pytest
from typer.testing import CliRunner

from rockgarden.cli import app
from rockgarden.theme import set_theme_name_in_config, validate_theme_name

runner = CliRunner()


class TestValidateThemeName:
    def test_valid_names(self):
        validate_theme_name("default")
        validate_theme_name("my-theme")
        validate_theme_name("my_theme")
        validate_theme_name("Theme123")

    def test_rejects_quotes(self):
        with pytest.raises(ValueError, match="Invalid theme name"):
            validate_theme_name('my"theme')

    def test_rejects_spaces(self):
        with pytest.raises(ValueError, match="Invalid theme name"):
            validate_theme_name("my theme")

    def test_rejects_special_chars(self):
        with pytest.raises(ValueError, match="Invalid theme name"):
            validate_theme_name("my/theme")


class TestSetThemeNameInConfig:
    def test_updates_existing_name(self, tmp_path):
        config = tmp_path / "rockgarden.toml"
        config.write_text('[site]\ntitle = "Test"\n\n[theme]\nname = "old"\n')
        set_theme_name_in_config(config, "new")
        content = config.read_text()
        assert 'name = "new"' in content
        assert 'name = "old"' not in content

    def test_inserts_under_existing_theme_section(self, tmp_path):
        config = tmp_path / "rockgarden.toml"
        config.write_text('[site]\ntitle = "Test"\n\n[theme]\ntoc = true\n')
        set_theme_name_in_config(config, "mytheme")
        content = config.read_text()
        assert 'name = "mytheme"' in content
        lines = content.splitlines()
        theme_idx = lines.index("[theme]")
        name_idx = next(i for i, line in enumerate(lines) if 'name = "mytheme"' in line)
        assert name_idx == theme_idx + 1

    def test_appends_new_theme_section(self, tmp_path):
        config = tmp_path / "rockgarden.toml"
        config.write_text('[site]\ntitle = "Test"\n')
        set_theme_name_in_config(config, "mytheme")
        content = config.read_text()
        assert "[theme]" in content
        assert 'name = "mytheme"' in content

    def test_ignores_name_key_in_array_of_tables(self, tmp_path):
        config = tmp_path / "rockgarden.toml"
        config.write_text(
            '[theme]\ntoc = true\n\n[[collections]]\nname = "characters"\n'
        )
        set_theme_name_in_config(config, "mytheme")
        parsed = tomllib.loads(config.read_text())
        assert parsed["theme"]["name"] == "mytheme"
        assert parsed["collections"][0]["name"] == "characters"

    def test_inserts_with_no_trailing_newline_on_section(self, tmp_path):
        config = tmp_path / "rockgarden.toml"
        config.write_text("[theme]")  # no trailing newline
        set_theme_name_in_config(config, "mytheme")
        parsed = tomllib.loads(config.read_text())
        assert parsed["theme"]["name"] == "mytheme"


class TestThemeExport:
    def test_creates_expected_files(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["theme", "export"])
        assert result.exit_code == 0, result.output
        dest = tmp_path / "_themes" / "default"
        assert (dest / "base.html").exists()
        assert (dest / "page.html").exists()
        assert (dest / "layouts" / "default.html").exists()
        assert (dest / "components").is_dir()
        assert (dest / "static" / "rockgarden.css").exists()
        assert (dest / "static-src" / "input.css").exists()
        assert (dest / "tailwind.config.js").exists()
        assert (dest / "package.json").exists()
        assert (dest / "theme.toml").exists()

    def test_custom_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["theme", "export", "--dir", "pyohio"])
        assert result.exit_code == 0, result.output
        assert (tmp_path / "_themes" / "pyohio" / "theme.toml").exists()

    def test_errors_if_dir_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "_themes" / "default").mkdir(parents=True)
        result = runner.invoke(app, ["theme", "export"])
        assert result.exit_code == 1
        assert "already exists" in result.output

    def test_rejects_invalid_name(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["theme", "export", "--dir", 'bad"name'])
        assert result.exit_code == 1
        assert "Invalid theme name" in result.output

    def test_updates_existing_config(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "rockgarden.toml").write_text('[site]\ntitle = "Test"\n')
        result = runner.invoke(app, ["theme", "export"])
        assert result.exit_code == 0, result.output
        assert 'name = "default"' in (tmp_path / "rockgarden.toml").read_text()

    def test_notes_missing_config(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["theme", "export"])
        assert result.exit_code == 0, result.output
        assert "No rockgarden.toml" in result.output
