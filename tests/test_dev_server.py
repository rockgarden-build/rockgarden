"""Integration tests for the dev command."""

from typer.testing import CliRunner

from rockgarden.cli import app

runner = CliRunner()


def test_dev_command_exists():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "dev" in result.output


def test_dev_help():
    result = runner.invoke(app, ["dev", "--help"])
    assert result.exit_code == 0
    assert "live reload" in result.output.lower()
    assert "--port" in result.output
    assert "--source" in result.output
    assert "--output" in result.output
    assert "--config" in result.output
    assert "--clean" in result.output
