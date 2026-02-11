"""Icon reference resolver.

Parses "library:name" references and dispatches to the appropriate
library loader. Currently supports Lucide; new libraries can be added
by registering a loader function in _LIBRARY_LOADERS.
"""

from pathlib import Path

from rockgarden.icons.lucide import load_lucide_icon

_icons_dir: Path | None = None


def configure_icons_dir(path: Path | None) -> None:
    """Set the project-local icons directory for override lookups."""
    global _icons_dir
    _icons_dir = path


def resolve_icon(ref: str) -> str | None:
    """Resolve a "library:name" icon reference to inline SVG.

    Args:
        ref: Icon reference (e.g., "lucide:info").

    Returns:
        SVG markup string, or None if the library or icon is not found.
    """
    if ":" not in ref:
        return None
    library, name = ref.split(":", 1)
    if not library or not name:
        return None
    if library == "lucide":
        return load_lucide_icon(name, _icons_dir)
    return None
