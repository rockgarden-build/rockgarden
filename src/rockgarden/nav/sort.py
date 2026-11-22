from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rockgarden.config import FolderSortOverride, NavConfig
    from rockgarden.content import FolderMeta


@dataclass
class ResolvedSort:
    sort: str
    reverse: bool


def _levels(
    folder_path: str,
    nav_config: NavConfig,
    folder_metas: Mapping[str, FolderMeta] | None,
) -> Iterator[tuple[FolderSortOverride | None, dict]]:
    """Yield (config override, `_folder.md` frontmatter) from root to folder."""
    folder_metas = folder_metas or {}
    parts = [p for p in folder_path.strip("/").split("/") if p]
    for i in range(len(parts) + 1):
        level = "/".join(parts[:i])
        meta = folder_metas.get(level)
        yield nav_config.overrides.get(level), meta.frontmatter if meta else {}


def resolve_sort(
    folder_path: str,
    nav_config: NavConfig,
    folder_metas: Mapping[str, FolderMeta] | None = None,
) -> ResolvedSort:
    """Resolve effective sort config for a folder.

    Settings inherit down the tree; the deepest folder that sets a value wins.
    Within one folder, `_folder.md` beats `[nav.overrides]`.
    """
    sort = nav_config.sort
    reverse = nav_config.reverse

    for override, fm in _levels(folder_path, nav_config, folder_metas):
        if override and override.sort is not None:
            sort = override.sort
        if override and override.reverse is not None:
            reverse = override.reverse
        if "sort" in fm:
            sort = fm["sort"]
        if "sort_reverse" in fm:
            reverse = bool(fm["sort_reverse"])

    return ResolvedSort(sort=sort, reverse=reverse)


def resolve_show_subtitles(
    folder_path: str,
    nav_config: NavConfig,
    folder_metas: Mapping[str, FolderMeta] | None = None,
) -> bool:
    """Resolve whether nav shows subtitles for a folder's children.

    Inherits like `resolve_sort`.
    """
    show = nav_config.show_subtitles

    for override, fm in _levels(folder_path, nav_config, folder_metas):
        if override and override.show_subtitles is not None:
            show = override.show_subtitles
        if "show_subtitles" in fm:
            show = bool(fm["show_subtitles"])

    return show
