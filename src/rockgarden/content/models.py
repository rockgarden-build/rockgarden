"""Content data models."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class Page:
    """Represents a single page/note from the vault."""

    source_path: Path
    slug: str
    frontmatter: dict = field(default_factory=dict)
    content: str = ""
    html: str | None = None
    modified: datetime | None = None
    created: datetime | None = None

    @property
    def title(self) -> str:
        """Get page title from frontmatter or derive from filename."""
        if title := self.frontmatter.get("title"):
            return title
        return self.source_path.stem.replace("_", " ")


@dataclass
class FolderMeta:
    """Folder-level metadata loaded from an optional `_folder.md` file.

    Unlike Page, FolderMeta does not produce a URL or appear in the content
    store or link index. Its body (if any) is ignored. Only frontmatter fields
    are consumed.
    """

    source_path: Path
    folder_path: str
    frontmatter: dict = field(default_factory=dict)

    @property
    def nav_order(self) -> int | None:
        return self.frontmatter.get("nav_order")

    @property
    def label(self) -> str | None:
        return self.frontmatter.get("label")

    @property
    def sort(self) -> str | None:
        return self.frontmatter.get("sort")

    @property
    def sort_reverse(self) -> bool | None:
        val = self.frontmatter.get("sort_reverse")
        return bool(val) if val is not None else None

    @property
    def unlisted(self) -> bool:
        return bool(self.frontmatter.get("unlisted", False))

    @property
    def show_index(self) -> bool:
        return bool(self.frontmatter.get("show_index", False))
