from typer.testing import CliRunner

from rockgarden import __version__
from rockgarden.cli import app

runner = CliRunner()


def test_version():
    assert __version__ == "0.2.2"


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "build" in result.output
    assert "serve" in result.output
