"""Tests for build hooks."""

import json
import sys
from datetime import datetime

import pytest

from rockgarden.config import Config
from rockgarden.content.models import Page
from rockgarden.hooks import HookError, run_hooks
from rockgarden.output.builder import export_content_json


def _py(script: str) -> str:
    """Build a python -c command string."""
    import shlex

    return f'{shlex.quote(sys.executable)} -c "{script}"'


class TestRunHooks:
    def test_empty_commands_is_noop(self, tmp_path):
        run_hooks([], "pre_build", cwd=tmp_path)

    def test_single_command_executes(self, tmp_path):
        marker = tmp_path / "marker.txt"
        script = f"from pathlib import Path; Path('{marker}').write_text('ok')"
        run_hooks([_py(script)], "pre_build", cwd=tmp_path)
        assert marker.read_text() == "ok"

    def test_commands_run_sequentially(self, tmp_path):
        log = tmp_path / "log.txt"
        cmd1 = _py(f"from pathlib import Path; Path('{log}').write_text('first\\n')")
        cmd2 = _py(
            "from pathlib import Path; "
            f"p = Path('{log}'); "
            "p.write_text(p.read_text() + 'second\\n')"
        )
        run_hooks([cmd1, cmd2], "pre_build", cwd=tmp_path)
        assert log.read_text() == "first\nsecond\n"

    def test_failure_raises_hook_error(self, tmp_path):
        with pytest.raises(HookError) as exc_info:
            run_hooks(
                [_py("raise SystemExit(42)")],
                "post_build",
                cwd=tmp_path,
            )
        assert exc_info.value.stage == "post_build"
        assert exc_info.value.returncode == 42

    def test_failure_aborts_remaining_commands(self, tmp_path):
        marker = tmp_path / "should_not_exist.txt"
        cmd_fail = _py("raise SystemExit(1)")
        cmd_write = _py(f"from pathlib import Path; Path('{marker}').write_text('bad')")
        with pytest.raises(HookError):
            run_hooks(
                [cmd_fail, cmd_write],
                "pre_build",
                cwd=tmp_path,
            )
        assert not marker.exists()

    def test_cwd_is_respected(self, tmp_path):
        script = (
            "from pathlib import Path; import os; "
            "Path('cwd_marker.txt').write_text(os.getcwd())"
        )
        run_hooks([_py(script)], "pre_build", cwd=tmp_path)
        marker = tmp_path / "cwd_marker.txt"
        assert marker.read_text() == str(tmp_path)

    def test_env_vars_passed_to_hooks(self, tmp_path):
        marker = tmp_path / "env_marker.txt"
        script = (
            "import os; from pathlib import Path; "
            f"Path('{marker}').write_text("
            "os.environ['ROCKGARDEN_SOURCE'])"
        )
        run_hooks(
            [_py(script)],
            "pre_build",
            cwd=tmp_path,
            env_vars={"ROCKGARDEN_SOURCE": "/fake/source"},
        )
        assert marker.read_text() == "/fake/source"


class TestHooksConfig:
    def test_default_hooks_are_empty(self):
        config = Config()
        assert config.hooks.pre_build == []
        assert config.hooks.post_collect == []
        assert config.hooks.post_build == []

    def test_hooks_loaded_from_toml(self, tmp_path):
        config_file = tmp_path / "rockgarden.toml"
        config_file.write_text(
            '[hooks]\npre_build = ["echo hello"]\npost_build = ["echo done"]\n'
        )
        config = Config.load(config_file)
        assert config.hooks.pre_build == ["echo hello"]
        assert config.hooks.post_collect == []
        assert config.hooks.post_build == ["echo done"]


class TestContentJsonExport:
    def test_content_json_written(self, tmp_path):
        pages = [
            Page(
                source_path=tmp_path / "content" / "hello.md",
                slug="hello",
                frontmatter={
                    "title": "Hello World",
                    "tags": ["test", "demo"],
                },
                content="# Hello",
            ),
        ]
        result_path = export_content_json(
            pages, tmp_path, clean_urls=True, base_path=""
        )
        assert result_path.exists()

        data = json.loads(result_path.read_text())
        assert len(data["pages"]) == 1
        assert data["pages"][0]["slug"] == "hello"
        assert data["pages"][0]["title"] == "Hello World"
        assert data["pages"][0]["tags"] == ["test", "demo"]
        assert data["pages"][0]["url"] == "/hello/"
        assert data["pages"][0]["source_path"] == "content/hello.md"
        assert data["collections"] == {}

    def test_content_json_in_rockgarden_dir(self, tmp_path):
        result_path = export_content_json([], tmp_path, clean_urls=True, base_path="")
        assert result_path.parent.name == ".rockgarden"
        assert result_path.name == "content.json"

    def test_content_json_handles_dates(self, tmp_path):
        pages = [
            Page(
                source_path=tmp_path / "content" / "dated.md",
                slug="dated",
                frontmatter={},
                content="",
                modified=datetime(2026, 1, 15, 12, 0, 0),
            ),
        ]
        result_path = export_content_json(
            pages, tmp_path, clean_urls=True, base_path=""
        )
        data = json.loads(result_path.read_text())
        assert data["pages"][0]["modified"] == "2026-01-15T12:00:00"
        assert data["pages"][0]["created"] is None
