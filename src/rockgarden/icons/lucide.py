"""Lucide icon loader."""

from importlib.resources import files

_ICONS_DIR = files("rockgarden.icons") / "svg" / "lucide"


def load_lucide_icon(name: str) -> str | None:
    """Load a Lucide SVG icon by name.

    Args:
        name: Icon name (e.g., "info", "triangle-alert").

    Returns:
        SVG markup string, or None if the icon doesn't exist.
    """
    resource = _ICONS_DIR / f"{name}.svg"
    try:
        return resource.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
