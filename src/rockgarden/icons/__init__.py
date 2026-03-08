"""Build-time icon resolution."""

from rockgarden.icons.inline import process_inline_icons
from rockgarden.icons.resolver import configure_icons_dir, resolve_icon

__all__ = ["configure_icons_dir", "process_inline_icons", "resolve_icon"]
