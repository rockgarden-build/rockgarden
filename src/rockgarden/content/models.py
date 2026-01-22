"""Content data models."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Page:
    """Represents a single page/note from the vault."""

    source_path: Path
    slug: str
    frontmatter: dict = field(default_factory=dict)
    content: str = ""
    html: str | None = None

    @property
    def title(self) -> str:
        """Get page title from frontmatter or derive from filename."""
        if title := self.frontmatter.get("title"):
            return title
        return self.source_path.stem.replace("_", " ")
