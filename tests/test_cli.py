import tempfile
from pathlib import Path

from typer.testing import CliRunner

from rockgarden import __version__
from rockgarden.cli import app

runner = CliRunner()


def test_version_flag():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_version_flag_short():
    result = runner.invoke(app, ["-v"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "build" in result.output
    assert "serve" in result.output
    assert "init" in result.output


def test_init_creates_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(
            app,
            ["init", tmpdir],
            input="My Test Site\ncontent\n_site\ny\n",
        )
        assert result.exit_code == 0
        config_path = Path(tmpdir) / "rockgarden.toml"
        assert config_path.exists()
        content = config_path.read_text()
        assert 'title = "My Test Site"' in content
        assert 'source = "content"' in content
        assert 'output = "_site"' in content


def test_init_adds_gitignore():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(
            app,
            ["init", tmpdir],
            input="Site\ncontent\n_site\ny\n",
        )
        assert result.exit_code == 0
        gitignore_path = Path(tmpdir) / ".gitignore"
        assert gitignore_path.exists()
        content = gitignore_path.read_text()
        assert "_site/" in content
        assert ".rockgarden/" in content


def test_init_skips_gitignore_when_declined():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(
            app,
            ["init", tmpdir],
            input="Site\ncontent\n_site\nn\n",
        )
        assert result.exit_code == 0
        gitignore_path = Path(tmpdir) / ".gitignore"
        assert not gitignore_path.exists()


def test_init_fails_if_config_exists():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "rockgarden.toml"
        config_path.write_text("[site]\n")
        result = runner.invoke(app, ["init", tmpdir])
        assert result.exit_code == 1
        assert "already exists" in result.output


def test_init_skips_gitignore_prompt_if_already_present():
    with tempfile.TemporaryDirectory() as tmpdir:
        gitignore_path = Path(tmpdir) / ".gitignore"
        gitignore_path.write_text("_site/\n.rockgarden/\n")
        result = runner.invoke(
            app,
            ["init", tmpdir],
            input="Site\ncontent\n_site\n",
        )
        assert result.exit_code == 0
        assert ".gitignore" not in result.output


def test_build_yaml_error_shows_hint(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "content"
    source.mkdir()
    bad_file = source / "bad.md"
    bad_file.write_text("---\ntitle: foo: bar: baz\n---\nHello\n")
    config = tmp_path / "rockgarden.toml"
    config.write_text('[site]\ntitle = "Test"\nsource = "content"\noutput = "_site"\n')
    result = runner.invoke(app, ["build", "--clean"])
    assert result.exit_code == 1
    assert "Invalid YAML in frontmatter" in result.output
    assert "Hint:" in result.output
    assert "Traceback" not in result.output


def test_build_unhandled_error_shows_type_and_message(tmp_path, monkeypatch):
    from unittest.mock import patch

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "content"
    source.mkdir()
    config = tmp_path / "rockgarden.toml"
    config.write_text('[site]\ntitle = "Test"\nsource = "content"\noutput = "_site"\n')

    side_effect = RuntimeError("something broke")
    with patch("rockgarden.cli.build_site", side_effect=side_effect):
        result = runner.invoke(app, ["build", "--clean"])
    assert result.exit_code == 1
    assert "RuntimeError: something broke" in result.output
    assert "Traceback" not in result.output
