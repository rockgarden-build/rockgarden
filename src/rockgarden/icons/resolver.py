"""Icon reference resolver.

Parses "library:name" references and dispatches to the appropriate
library loader. Currently supports Lucide; new libraries can be added
by registering a loader function in _LIBRARY_LOADERS.
"""

from collections.abc import Callable

from rockgarden.icons.lucide import load_lucide_icon

_LIBRARY_LOADERS: dict[str, Callable[[str], str | None]] = {
    "lucide": load_lucide_icon,
}


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
    loader = _LIBRARY_LOADERS.get(library)
    if loader is None:
        return None
    return loader(name)
