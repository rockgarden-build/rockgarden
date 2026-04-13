"""Content discovery and loading."""

import fnmatch
import logging
from datetime import date, datetime
from pathlib import Path

import frontmatter

from rockgarden.config import DatesConfig
from rockgarden.content.models import FolderMeta, Page
from rockgarden.urls import generate_slug

FOLDER_META_FILENAME = "_folder.md"

logger = logging.getLogger(__name__)


def _resolve_frontmatter_date(
    metadata: dict, field_names: list[str]
) -> datetime | None:
    """Check frontmatter fields in order and return the first valid date."""
    for name in field_names:
        value = metadata.get(name)
        if value is None:
            continue
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime(value.year, value.month, value.day)
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
    return None


def should_ignore(path: Path, source: Path, patterns: list[str]) -> bool:
    """Check if a path should be ignored based on patterns.

    Args:
        path: The file path to check.
        source: The source root directory.
        patterns: List of glob patterns to ignore.

    Returns:
        True if the path should be ignored.
    """
    rel_path = path.relative_to(source)

    for pattern in patterns:
        if fnmatch.fnmatch(str(rel_path), pattern):
            return True
        if fnmatch.fnmatch(rel_path.name, pattern):
            return True
        for part in rel_path.parts:
            if fnmatch.fnmatch(part, pattern):
                return True

    return False


def path_to_slug(
    path: Path,
    source: Path,
    url_style: str = "slug",
    ascii_urls: bool = False,
) -> str:
    """Convert a file path to a URL slug.

    Args:
        path: The file path.
        source: The source root directory.
        url_style: URL style ("slug", "preserve-case", or "preserve").
        ascii_urls: When True, transliterate Unicode to ASCII.

    Returns:
        The slug (e.g., 'index', 'npcs/olvir').
    """
    rel_path = str(path.relative_to(source))
    return generate_slug(rel_path, style=url_style, ascii_urls=ascii_urls)


def load_page(
    path: Path,
    source: Path,
    dates_config: DatesConfig | None = None,
    url_style: str = "slug",
    ascii_urls: bool = False,
) -> Page:
    """Load a single page from a markdown file.

    Args:
        path: Path to the markdown file.
        source: The source root directory.
        dates_config: Date resolution configuration.

    Returns:
        A Page object with parsed frontmatter and content.
    """
    if dates_config is None:
        dates_config = DatesConfig()

    post = frontmatter.load(path)
    metadata = dict(post.metadata)

    if custom_slug := metadata.get("slug"):
        slug = custom_slug
    else:
        slug = path_to_slug(path, source, url_style, ascii_urls)
        # Folder note: rewrite slug so downstream index-page logic applies
        parts = slug.split("/")
        if len(parts) >= 2 and parts[-1] == parts[-2]:
            slug = "/".join(parts[:-1]) + "/index"

    modified = _resolve_frontmatter_date(metadata, dates_config.modified_date_fields)
    if modified is None and dates_config.modified_date_fallback:
        modified = datetime.fromtimestamp(path.stat().st_mtime)

    created = _resolve_frontmatter_date(metadata, dates_config.created_date_fields)

    return Page(
        source_path=path,
        slug=slug,
        frontmatter=metadata,
        content=post.content,
        modified=modified,
        created=created,
    )


def load_content(
    source: Path,
    ignore_patterns: list[str],
    dates_config: DatesConfig | None = None,
    url_style: str = "slug",
    ascii_urls: bool = False,
) -> list[Page]:
    """Discover and load all markdown files from source directory.

    Args:
        source: The source directory to scan.
        ignore_patterns: List of glob patterns to ignore.
        dates_config: Date resolution configuration.

    Returns:
        List of Page objects.
    """
    pages = []

    for path in source.rglob("*.md"):
        if should_ignore(path, source, ignore_patterns):
            continue

        if path.name == FOLDER_META_FILENAME:
            continue

        page = load_page(path, source, dates_config, url_style, ascii_urls)
        pages.append(page)

    # Resolve conflicts: if both a folder note and index.md exist, index.md wins
    index_slugs: dict[str, list[Page]] = {}
    for page in pages:
        if page.slug.endswith("/index") or page.slug == "index":
            index_slugs.setdefault(page.slug, []).append(page)

    for _slug, slug_pages in index_slugs.items():
        if len(slug_pages) > 1:
            explicit = [p for p in slug_pages if p.source_path.name == "index.md"]
            folder_notes = [p for p in slug_pages if p.source_path.name != "index.md"]
            if explicit and folder_notes:
                for fn in folder_notes:
                    fn.slug = path_to_slug(
                        fn.source_path, source, url_style, ascii_urls
                    )
                    logger.warning(
                        "Both %s and index.md exist in %s. "
                        "Using index.md as the folder page.",
                        fn.source_path.name,
                        fn.source_path.parent,
                    )

    return pages


def load_folder_metas(
    source: Path,
    ignore_patterns: list[str],
) -> dict[str, FolderMeta]:
    """Discover and load all `_folder.md` files from source directory.

    Args:
        source: The source directory to scan.
        ignore_patterns: List of glob patterns to ignore.

    Returns:
        Dict mapping folder path (relative to source, with forward slashes,
        empty string for the source root) to FolderMeta.
    """
    metas: dict[str, FolderMeta] = {}

    for path in source.rglob(FOLDER_META_FILENAME):
        if should_ignore(path, source, ignore_patterns):
            continue

        post = frontmatter.load(path)
        rel_parent = path.parent.relative_to(source)
        folder_path = "" if rel_parent == Path(".") else rel_parent.as_posix()

        metas[folder_path] = FolderMeta(
            source_path=path,
            folder_path=folder_path,
            frontmatter=dict(post.metadata),
        )

    return metas
