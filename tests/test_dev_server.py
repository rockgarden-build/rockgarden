"""Integration tests for the dev command."""

import re

from typer.testing import CliRunner

from rockgarden.cli import app

runner = CliRunner()

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


def test_dev_command_exists():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "dev" in result.output


def test_dev_help():
    result = runner.invoke(app, ["dev", "--help"])
    assert result.exit_code == 0
    output = _strip_ansi(result.output)
    assert "live reload" in output.lower()
    assert "--port" in output
    assert "--source" in output
    assert "--output" in output
    assert "--config" in output
    assert "--clean" in output
