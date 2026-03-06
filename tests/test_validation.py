"""Tests for config validation."""

from typer.testing import CliRunner

from rockgarden.cli import app
from rockgarden.validation import validate_config

runner = CliRunner()


# --- validate_config unit tests ---


def test_clean_config_no_issues():
    assert validate_config({}) == []


def test_unknown_top_level_section():
    issues = validate_config({"mistyped": {}})
    assert len(issues) == 1
    assert issues[0].level == "warning"
    assert "mistyped" in issues[0].message


def test_unknown_site_key():
    issues = validate_config({"site": {"titl": "Oops"}})
    assert any(
        i.level == "warning" and "[site]" in i.message and '"titl"' in i.message
        for i in issues
    )


def test_unknown_site_key_suggestion():
    issues = validate_config({"site": {"titl": "Oops"}})
    assert any('"title"' in i.message for i in issues)


def test_known_site_key_no_warning():
    issues = validate_config({"site": {"title": "My Site"}})
    assert issues == []


def test_invalid_timezone():
    issues = validate_config({"dates": {"timezone": "Bad/Zone"}})
    assert any(i.level == "error" and "Bad/Zone" in i.message for i in issues)


def test_valid_timezone_no_error():
    issues = validate_config({"dates": {"timezone": "America/New_York"}})
    assert not any(i.level == "error" for i in issues)


def test_source_dir_missing(tmp_path):
    issues = validate_config(
        {"site": {"source": "nonexistent"}},
        config_file_dir=tmp_path,
    )
    assert any(i.level == "warning" and "does not exist" in i.message for i in issues)


def test_source_dir_exists(tmp_path):
    src = tmp_path / "content"
    src.mkdir()
    issues = validate_config(
        {"site": {"source": "content"}},
        config_file_dir=tmp_path,
    )
    assert not any("does not exist" in i.message for i in issues)


def test_theme_dir_missing(tmp_path):
    issues = validate_config(
        {"theme": {"name": "mytheme"}},
        config_file_dir=tmp_path,
    )
    assert any(i.level == "warning" and "mytheme" in i.message for i in issues)


def test_theme_dir_exists_no_manifest(tmp_path):
    theme_dir = tmp_path / "_themes" / "mytheme"
    theme_dir.mkdir(parents=True)
    issues = validate_config(
        {"theme": {"name": "mytheme"}},
        config_file_dir=tmp_path,
    )
    assert not any("not found" in i.message for i in issues)


_REQUIRED_KEY_MANIFEST = (
    '[theme]\nname = "mytheme"\n\n'
    '[[theme.config]]\nkey = "show_sponsors"\ntype = "bool"\nrequired = true\n'
)

_OPTIONAL_KEY_MANIFEST = (
    '[theme]\nname = "mytheme"\n\n'
    '[[theme.config]]\nkey = "primary_color"\ntype = "string"\nrequired = false\n'
)


def test_theme_manifest_required_key_missing(tmp_path):
    theme_dir = tmp_path / "_themes" / "mytheme"
    theme_dir.mkdir(parents=True)
    (theme_dir / "theme.toml").write_text(_REQUIRED_KEY_MANIFEST)
    issues = validate_config(
        {"theme": {"name": "mytheme"}},
        config_file_dir=tmp_path,
    )
    assert any(i.level == "error" and "show_sponsors" in i.message for i in issues)


def test_theme_manifest_required_key_present_no_warning(tmp_path):
    theme_dir = tmp_path / "_themes" / "mytheme"
    theme_dir.mkdir(parents=True)
    (theme_dir / "theme.toml").write_text(_REQUIRED_KEY_MANIFEST)
    issues = validate_config(
        {"theme": {"name": "mytheme", "show_sponsors": True}},
        config_file_dir=tmp_path,
    )
    assert not any("show_sponsors" in i.message for i in issues)


def test_theme_manifest_declared_key_not_unknown(tmp_path):
    theme_dir = tmp_path / "_themes" / "mytheme"
    theme_dir.mkdir(parents=True)
    (theme_dir / "theme.toml").write_text(_OPTIONAL_KEY_MANIFEST)
    issues = validate_config(
        {"theme": {"name": "mytheme", "primary_color": "#fff"}},
        config_file_dir=tmp_path,
    )
    assert not any("primary_color" in i.message for i in issues)


# --- CLI validate command tests ---


def test_validate_clean_config(tmp_path):
    config = tmp_path / "rockgarden.toml"
    config.write_text('[site]\ntitle = "Test"\n')
    result = runner.invoke(app, ["validate", "--config", str(config)])
    assert result.exit_code == 0
    assert "No issues found" in result.output


def test_validate_unknown_key_exits_0(tmp_path):
    config = tmp_path / "rockgarden.toml"
    config.write_text('[site]\ntitl = "oops"\n')
    result = runner.invoke(app, ["validate", "--config", str(config)])
    assert result.exit_code == 0


def test_validate_bad_timezone_exits_1(tmp_path):
    config = tmp_path / "rockgarden.toml"
    config.write_text('[dates]\ntimezone = "Bad/Zone"\n')
    result = runner.invoke(app, ["validate", "--config", str(config)])
    assert result.exit_code == 1


def test_validate_missing_config_exits_1(tmp_path):
    result = runner.invoke(
        app, ["validate", "--config", str(tmp_path / "nonexistent.toml")]
    )
    assert result.exit_code == 1


def test_validate_toml_syntax_error_exits_1(tmp_path):
    config = tmp_path / "rockgarden.toml"
    config.write_text("this is not valid toml = = =\n")
    result = runner.invoke(app, ["validate", "--config", str(config)])
    assert result.exit_code == 1


def test_validate_command_in_help():
    result = runner.invoke(app, ["--help"])
    assert "validate" in result.output
