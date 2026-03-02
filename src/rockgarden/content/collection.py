"""Collection partitioning for named content groupings."""

from dataclasses import dataclass, field
from pathlib import Path

from rockgarden.config import CollectionConfig
from rockgarden.content.models import Page


@dataclass
class Collection:
    """A named group of content entries."""

    name: str
    config: CollectionConfig
    entries: list[Page | dict] = field(default_factory=list)


def partition_collections(
    pages: list[Page],
    collection_configs: list[CollectionConfig],
    source: Path,
) -> dict[str, Collection]:
    """Partition pages into named collections based on source directory paths.

    A page matches a collection if its source_path (relative to source) starts
    with the collection's ``source`` prefix. Pages can appear in multiple
    collections when collections nest (e.g. ``characters/pcs/`` matches both
    a ``pcs`` collection with ``source="characters/pcs"`` and a ``characters``
    collection with ``source="characters"``).

    Args:
        pages: All loaded markdown pages.
        collection_configs: Collection definitions from config.
        source: The content source root directory.

    Returns:
        Mapping of collection name to Collection object.
    """
    collections: dict[str, Collection] = {}

    for cfg in collection_configs:
        collection = Collection(name=cfg.name, config=cfg)
        prefix = cfg.source.rstrip("/")

        for page in pages:
            try:
                rel = page.source_path.relative_to(source)
            except ValueError:
                rel = page.source_path

            rel_str = str(rel.as_posix())
            if rel_str.startswith(prefix + "/") or rel_str == prefix:
                collection.entries.append(page)

        collections[cfg.name] = collection

    return collections
