"""Load non-markdown data files (YAML, JSON, TOML) for collections."""

import json
import tomllib
from pathlib import Path

import yaml

DATA_EXTENSIONS = {".yaml", ".yml", ".json", ".toml"}


def load_data_file(path: Path) -> dict:
    """Parse a YAML, JSON, or TOML file into a dict.

    Raises:
        ValueError: If the file format is unsupported or the parsed content
            is not a dict.
    """
    suffix = path.suffix.lower()

    if suffix in (".yaml", ".yml"):
        with open(path) as f:
            data = yaml.safe_load(f)
    elif suffix == ".json":
        with open(path) as f:
            data = json.load(f)
    elif suffix == ".toml":
        with open(path, "rb") as f:
            data = tomllib.load(f)
    else:
        raise ValueError(f"Unsupported data file format: {path}")

    if not isinstance(data, dict):
        raise ValueError(
            f"Data file must contain a mapping/dict, got {type(data).__name__}: {path}"
        )

    return data


def load_collection_data_files(
    source: Path,
    collection_source: str,
    ignore_patterns: list[str] | None = None,
) -> list[dict]:
    """Discover and load non-markdown data files from a collection directory.

    Each entry gets a ``slug`` derived from the filename stem unless it already
    has an explicit ``slug`` field.

    Args:
        source: Content source root directory.
        collection_source: Collection's source directory (relative to source).
        ignore_patterns: Patterns to ignore (unused for now, reserved).

    Returns:
        List of dicts, one per data file.
    """
    data_dir = source / collection_source
    if not data_dir.exists():
        return []

    entries = []
    for path in sorted(data_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in DATA_EXTENSIONS:
            continue

        entry = load_data_file(path)
        if "slug" not in entry:
            entry["slug"] = path.stem
        entries.append(entry)

    return entries
