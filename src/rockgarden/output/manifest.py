"""Build manifest for incremental builds."""

from __future__ import annotations

import hashlib
import importlib.resources
import json
from dataclasses import dataclass, field
from pathlib import Path

MANIFEST_VERSION = 1


@dataclass
class PageManifestEntry:
    content_hash: str
    output_path: str


@dataclass
class BuildManifest:
    config_hash: str
    template_hash: str
    macro_hash: str
    output_dir: str
    page_count: int
    cdn_flags: str = ""
    pages: dict[str, PageManifestEntry] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> BuildManifest | None:
        """Load from JSON. Returns None if missing, invalid, or wrong version."""
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text())
            if data.get("version") != MANIFEST_VERSION:
                return None
            pages = {
                slug: PageManifestEntry(**entry)
                for slug, entry in data.get("pages", {}).items()
            }
            return cls(
                config_hash=data["config_hash"],
                template_hash=data["template_hash"],
                macro_hash=data["macro_hash"],
                output_dir=data["output_dir"],
                page_count=data["page_count"],
                cdn_flags=data.get("cdn_flags", ""),
                pages=pages,
            )
        except (json.JSONDecodeError, KeyError, TypeError):
            return None

    def save(self, path: Path) -> None:
        """Write manifest to JSON."""
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": MANIFEST_VERSION,
            "config_hash": self.config_hash,
            "template_hash": self.template_hash,
            "macro_hash": self.macro_hash,
            "output_dir": self.output_dir,
            "page_count": self.page_count,
            "cdn_flags": self.cdn_flags,
            "pages": {
                slug: {"content_hash": e.content_hash, "output_path": e.output_path}
                for slug, e in self.pages.items()
            },
        }
        path.write_text(json.dumps(data, indent=2) + "\n")

    def is_page_dirty(self, slug: str, content_hash: str, output: Path) -> bool:
        """Check if a page needs rebuilding."""
        entry = self.pages.get(slug)
        if entry is None:
            return True
        if entry.content_hash != content_hash:
            return True
        output_file = output / entry.output_path
        return not output_file.exists()

    def needs_full_rebuild(
        self,
        config_hash: str,
        template_hash: str,
        macro_hash: str,
        output_dir: str,
        page_count: int,
        cdn_flags: str = "",
    ) -> bool:
        """Check if a full rebuild is needed due to global changes."""
        if self.config_hash != config_hash:
            return True
        if self.template_hash != template_hash:
            return True
        if self.macro_hash != macro_hash:
            return True
        if self.output_dir != output_dir:
            return True
        if self.page_count != page_count:
            return True
        if self.cdn_flags != cdn_flags:
            return True
        if not Path(output_dir).exists():
            return True
        return False


def hash_file(path: Path) -> str:
    """SHA-256 hex digest of a file's contents."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hash_directory(directory: Path, glob: str = "**/*") -> str:
    """Combined SHA-256 of all files in a directory, sorted by relative path."""
    h = hashlib.sha256()
    if not directory.exists():
        return h.hexdigest()
    for file_path in sorted(directory.glob(glob)):
        if file_path.is_file():
            rel = str(file_path.relative_to(directory))
            h.update(rel.encode())
            h.update(file_path.read_bytes())
    return h.hexdigest()


def compute_config_hash(config_path: Path | None) -> str:
    """Hash the config file contents."""
    if config_path and config_path.exists():
        return hash_file(config_path)
    return hashlib.sha256(b"").hexdigest()


def compute_template_hash(site_root: Path, theme_name: str) -> str:
    """Hash all template sources: _templates/, _themes/<name>/, bundled."""
    h = hashlib.sha256()

    site_templates = site_root / "_templates"
    h.update(hash_directory(site_templates).encode())

    if theme_name:
        theme_templates = site_root / "_themes" / theme_name
        h.update(hash_directory(theme_templates).encode())

    bundled = importlib.resources.files("rockgarden").joinpath("templates")
    with importlib.resources.as_file(bundled) as bundled_path:
        h.update(hash_directory(bundled_path).encode())

    return h.hexdigest()


def compute_macro_hash(site_root: Path) -> str:
    """Hash all _macros/ files."""
    return hash_directory(site_root / "_macros")
