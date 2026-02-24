"""Build info gathering for footer display."""

import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from rockgarden import __version__


@dataclass
class BuildInfo:
    """Build metadata for display in site footer."""

    build_time: datetime
    version: str = __version__
    git_commit: str | None = None
    git_message: str | None = None
    git_author: str | None = None
    git_date: str | None = None


def get_build_info(
    site_root: Path | None = None, include_git: bool = False
) -> BuildInfo:
    """Gather build info including timestamp and optional git details.

    Args:
        site_root: Root directory of the site (for git lookups).
        include_git: Whether to include git commit info.

    Returns:
        BuildInfo with build timestamp and optional git info.
    """
    build_time = datetime.now()
    git_commit = None
    git_message = None
    git_author = None
    git_date = None

    if include_git:
        cwd = str(site_root) if site_root else None
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H%n%s%n%an%n%aI"],
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=5,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if len(lines) >= 4:
                    git_commit = lines[0]
                    git_message = lines[1]
                    git_author = lines[2]
                    git_date = lines[3]
        except (OSError, subprocess.TimeoutExpired):
            pass

    return BuildInfo(
        build_time=build_time,
        git_commit=git_commit,
        git_message=git_message,
        git_author=git_author,
        git_date=git_date,
    )
