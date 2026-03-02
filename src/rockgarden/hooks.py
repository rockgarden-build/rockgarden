"""Build hook execution."""

import os
import subprocess
from pathlib import Path


class HookError(Exception):
    """Raised when a build hook command fails."""

    def __init__(self, stage: str, command: str, returncode: int):
        self.stage = stage
        self.command = command
        self.returncode = returncode
        super().__init__(
            f"Hook failed at {stage}: {command!r} (exit code {returncode})"
        )


def run_hooks(
    commands: list[str],
    stage: str,
    cwd: Path,
    env_vars: dict[str, str] | None = None,
) -> None:
    """Execute hook commands sequentially.

    Args:
        commands: Shell commands to execute.
        stage: Hook stage name (for logging and error messages).
        cwd: Working directory for command execution.
        env_vars: Additional environment variables to pass to hooks.

    Raises:
        HookError: If any command exits with a non-zero status.
    """
    if not commands:
        return

    env = {**os.environ, **(env_vars or {})}

    for cmd in commands:
        print(f"[{stage}] Running: {cmd}")
        result = subprocess.run(cmd, shell=True, cwd=cwd, env=env)
        if result.returncode != 0:
            raise HookError(stage, cmd, result.returncode)
