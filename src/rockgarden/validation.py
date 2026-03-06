"""Config validation for rockgarden."""

import tomllib
from dataclasses import dataclass
from difflib import get_close_matches
from pathlib import Path
from typing import Literal

from rockgarden.config import (
    BuildConfig,
    DatesConfig,
    HooksConfig,
    NavConfig,
    SearchConfig,
    SiteConfig,
    ThemeConfig,
    TocConfig,
)

# Map of top-level TOML section names to their config model classes.
# "collections" is a list and handled separately.
_SECTION_MODELS: dict[str, type] = {
    "site": SiteConfig,
    "build": BuildConfig,
    "theme": ThemeConfig,
    "nav": NavConfig,
    "toc": TocConfig,
    "search": SearchConfig,
    "dates": DatesConfig,
    "hooks": HooksConfig,
}

_KNOWN_SECTIONS = set(_SECTION_MODELS.keys()) | {"collections"}


@dataclass
class ValidationIssue:
    level: Literal["error", "warning"]
    message: str


def load_theme_manifest(theme_dir: Path) -> dict:
    """Load and parse theme.toml from a theme directory. Returns {} if absent."""
    manifest_path = theme_dir / "theme.toml"
    if not manifest_path.exists():
        return {}
    with open(manifest_path, "rb") as f:
        return tomllib.load(f)


def _known_keys(model_class: type) -> set[str]:
    return set(model_class.model_fields.keys())


def validate_config(
    config_dict: dict,
    source_dir: Path | None = None,
    config_file_dir: Path | None = None,
) -> list[ValidationIssue]:
    """Validate a parsed TOML dict against known config schema."""
    issues: list[ValidationIssue] = []

    # Unknown top-level sections
    for key in config_dict:
        if key not in _KNOWN_SECTIONS:
            suggestion = get_close_matches(key, _KNOWN_SECTIONS, n=1, cutoff=0.6)
            hint = f' (did you mean "{suggestion[0]}"?)' if suggestion else ""
            issues.append(
                ValidationIssue("warning", f"unknown top-level section [{key}]{hint}")
            )

    # Unknown keys per section
    for section, model_class in _SECTION_MODELS.items():
        if section not in config_dict:
            continue
        section_data = config_dict[section]
        if not isinstance(section_data, dict):
            continue
        known = _known_keys(model_class)
        for key in section_data:
            if key not in known:
                suggestion = get_close_matches(key, known, n=1, cutoff=0.6)
                hint = f' (did you mean "{suggestion[0]}"?)' if suggestion else ""
                issues.append(
                    ValidationIssue("warning", f'[{section}] unknown key "{key}"{hint}')
                )

    # Timezone validation
    dates_data = config_dict.get("dates", {})
    if isinstance(dates_data, dict) and "timezone" in dates_data:
        tz = dates_data["timezone"]
        try:
            from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

            ZoneInfo(tz)
        except ZoneInfoNotFoundError:
            issues.append(
                ValidationIssue(
                    "error",
                    f'[dates] invalid timezone "{tz}" — ZoneInfoNotFoundError',
                )
            )

    # Source directory existence
    resolved_source: Path | None = None
    site_data = config_dict.get("site", {})
    if source_dir is not None:
        resolved_source = source_dir
    elif isinstance(site_data, dict) and "source" in site_data:
        raw = site_data["source"]
        base = config_file_dir or Path(".")
        resolved_source = (base / raw).resolve()

    if resolved_source is not None and not resolved_source.exists():
        issues.append(
            ValidationIssue(
                "warning", f'source directory "{resolved_source}" does not exist'
            )
        )

    # Theme directory and manifest
    theme_data = config_dict.get("theme", {})
    if isinstance(theme_data, dict) and theme_data.get("name"):
        theme_name = theme_data["name"]
        base = config_file_dir or Path(".")
        theme_dir = base / "_themes" / theme_name

        if not theme_dir.exists():
            issues.append(
                ValidationIssue(
                    "warning",
                    f'theme "{theme_name}" not found — no directory at {theme_dir}',
                )
            )
        else:
            manifest = load_theme_manifest(theme_dir)
            if manifest:
                manifest_theme = manifest.get("theme", {})

                # Declared keys are valid — no unknown-key warning for them
                declared_keys = {
                    entry["key"]
                    for entry in manifest_theme.get("config", [])
                    if "key" in entry
                }

                # Remove warnings we already added for [theme] unknown keys
                # that are now covered by the manifest
                issues = [
                    issue
                    for issue in issues
                    if not (
                        issue.level == "warning"
                        and issue.message.startswith("[theme] unknown key")
                        and any(f'"{k}"' in issue.message for k in declared_keys)
                    )
                ]

                # Required keys from manifest
                for entry in manifest_theme.get("config", []):
                    if entry.get("required") and entry.get("key"):
                        k = entry["key"]
                        if k not in theme_data:
                            msg = (
                                f'[theme] required key "{k}"'
                                " declared in theme manifest is missing"
                            )
                            issues.append(ValidationIssue("warning", msg))

    return issues
