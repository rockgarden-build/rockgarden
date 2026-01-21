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
        assert "_site/" in gitignore_path.read_text()


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
        gitignore_path.write_text("_site/\n")
        result = runner.invoke(
            app,
            ["init", tmpdir],
            input="Site\ncontent\n_site\n",
        )
        assert result.exit_code == 0
        assert "Add '_site/' to .gitignore?" not in result.output
