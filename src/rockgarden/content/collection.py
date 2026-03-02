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

    @property
    def generates_pages(self) -> bool:
        """Whether this collection generates its own pages."""
        return bool(
            self.config.pages and self.config.template and self.config.url_pattern
        )


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


def entry_fields(entry: Page | dict) -> dict:
    """Extract a flat dict of fields from an entry for URL substitution."""
    if isinstance(entry, Page):
        return {
            "slug": entry.source_path.stem,
            "title": entry.title,
            **entry.frontmatter,
        }
    return dict(entry)


def generate_collection_url(url_pattern: str, entry: Page | dict) -> str:
    """Replace ``{field}`` placeholders in url_pattern with entry values."""
    fields = entry_fields(entry)
    try:
        return url_pattern.format(**fields)
    except KeyError as exc:
        if isinstance(entry, Page):
            entry_id = entry.slug
        else:
            entry_id = entry.get("slug", "<unknown>")
        raise ValueError(
            f"url_pattern '{url_pattern}' references missing "
            f"field {exc} in entry '{entry_id}'"
        ) from exc


def get_collection_skip_slugs(
    collections: dict[str, "Collection"],
) -> set[str]:
    """Return slugs of Pages that should be skipped in the main render loop.

    A page is skipped if its collection either generates its own pages
    (custom template) or suppresses page output (``pages=false``).
    """
    skip: set[str] = set()
    for col in collections.values():
        if col.generates_pages or not col.config.pages:
            for entry in col.entries:
                if isinstance(entry, Page):
                    skip.add(entry.slug)
    return skip
