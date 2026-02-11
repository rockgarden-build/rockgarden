"""Lucide icon loader.

Loads icons from a project-local override directory first, then falls
back to the bundled lucide.zip that ships with rockgarden.
"""

import re
import zipfile
from functools import lru_cache
from importlib.resources import files
from pathlib import Path

_BUNDLED_ZIP = files("rockgarden.icons") / "lucide.zip"
_SAFE_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")


@lru_cache(maxsize=256)
def _load_from_zip(name: str) -> str | None:
    """Load an icon from the bundled ZIP archive."""
    try:
        with zipfile.ZipFile(_BUNDLED_ZIP) as zf:
            return zf.read(f"{name}.svg").decode("utf-8").strip()
    except (KeyError, FileNotFoundError):
        return None


def load_lucide_icon(name: str, icons_dir: Path | None = None) -> str | None:
    """Load a Lucide SVG icon by name.

    Checks the project-local icons directory first (if configured),
    then falls back to the bundled ZIP.

    Args:
        name: Icon name (e.g., "info", "triangle-alert").
        icons_dir: Optional project-local icons directory.

    Returns:
        SVG markup string, or None if the icon doesn't exist.
    """
    if not _SAFE_NAME.match(name):
        return None
    if icons_dir:
        local_file = icons_dir / "lucide" / f"{name}.svg"
        if local_file.exists():
            return local_file.read_text(encoding="utf-8").strip()

    return _load_from_zip(name)
