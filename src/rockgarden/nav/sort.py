from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rockgarden.config import NavConfig


@dataclass
class ResolvedSort:
    sort: str
    reverse: bool


def resolve_sort(
    folder_path: str,
    nav_config: NavConfig,
    folder_frontmatter: dict | None = None,
) -> ResolvedSort:
    """Resolve effective sort config for a folder.

    Priority: frontmatter > config overrides > global defaults.
    """
    sort = nav_config.sort
    reverse = nav_config.reverse

    normalized = folder_path.strip("/")
    if normalized in nav_config.overrides:
        override = nav_config.overrides[normalized]
        if override.sort is not None:
            sort = override.sort
        if override.reverse is not None:
            reverse = override.reverse

    if folder_frontmatter:
        if "sort" in folder_frontmatter:
            sort = folder_frontmatter["sort"]
        if "sort_reverse" in folder_frontmatter:
            reverse = bool(folder_frontmatter["sort_reverse"])

    return ResolvedSort(sort=sort, reverse=reverse)
