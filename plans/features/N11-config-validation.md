# Feature N11: Config Validation

## Status: Complete

## Goal

Provide a `validate` CLI command that checks a `rockgarden.toml` for problems: unknown keys (likely typos), invalid values, missing required values, and theme-specific config issues. Themes should be able to declare what config keys they use so that unexpected or missing theme config can also be reported.

---

## Design

### Validation Categories

**Errors** (exit code 1):
- TOML syntax errors
- Invalid timezone (ZoneInfo lookup fails)
- Theme declared as required config missing from TOML

**Warnings** (exit code 0, printed to stderr):
- Unknown key in any config section (probable typo)
- Source directory does not exist
- `theme.name` set but `_themes/<name>/` directory not found
- Theme manifest declares a required key but it's absent from `[theme]` → **error**

### Known-Key Validation

The existing dataclasses define all valid keys per section. Validation extracts field names via `dataclasses.fields()` and compares against what the TOML dict actually contains. Unknown keys get a warning.

Known sections: `site`, `build`, `theme`, `nav`, `toc`, `search`, `dates`. Unknown top-level sections also warn.

### Theme Manifest (`theme.toml`)

A theme can optionally ship a `theme.toml` in its directory (`_themes/<name>/theme.toml`) to declare metadata and any additional config keys it reads from the `[theme]` section.

```toml
[theme]
name = "pyohio"
description = "PyOhio conference theme"
version = "1.0.0"

[[theme.config]]
key = "show_sponsors"
type = "bool"
required = true
description = "Whether to show sponsor logos in the footer"

[[theme.config]]
key = "primary_color"
type = "string"
required = false
default = "#3490dc"
description = "Primary brand color (CSS value)"
```

When a theme manifest exists:
- Its declared keys are added to the known-key set for `[theme]`, so they don't produce "unknown key" warnings
- Any key marked `required = true` that is absent from `[theme]` produces a warning
- Themes without a manifest are still valid — manifest is optional

---

## Implementation Plan

### 1. New module: `src/rockgarden/validation.py`

```python
@dataclass
class ValidationIssue:
    level: Literal["error", "warning"]
    message: str

def validate_config(config_dict: dict, source_dir: Path | None = None) -> list[ValidationIssue]:
    """Validate a parsed TOML dict against known config schema."""
    ...

def load_theme_manifest(theme_dir: Path) -> dict:
    """Load and parse theme.toml from a theme directory. Returns {} if absent."""
    ...
```

Key checks in `validate_config()`:
- Unknown top-level sections
- Unknown keys per section (via `dataclasses.fields()` on each config class)
- Timezone: `ZoneInfo(dates_data.get("timezone", "UTC"))` in try/except
- Source dir existence (if provided / resolvable)
- Theme dir existence + manifest loading if `theme.name` is set
- Theme manifest required-key check

### 2. New CLI command in `src/rockgarden/cli.py`

```python
@app.command()
def validate(
    source: Annotated[Path | None, typer.Option("--source", "-s")] = None,
    config_file: Annotated[Path | None, typer.Option("--config", "-c")] = None,
) -> None:
    """Validate rockgarden configuration."""
```

Same config/source resolution logic as `build` (auto-discovers `rockgarden.toml` in source dir). Reports issues to stderr, exits 1 on any errors.

Output format:
```
✓ No issues found.

# or:

Warning: [site] unknown key "titl" (did you mean "title"?)
Warning: source directory "content" does not exist
Error: [dates] invalid timezone "US/Easten" — ZoneInfoNotFoundError
```

### 3. Known-key sets

Rather than hard-coding lists, derive from dataclasses at runtime:

```python
import dataclasses
from rockgarden.config import SiteConfig, BuildConfig, ThemeConfig, ...

KNOWN_KEYS = {
    "site": {f.name for f in dataclasses.fields(SiteConfig)},
    "build": {f.name for f in dataclasses.fields(BuildConfig)},
    ...
}
```

Built-in `ThemeConfig` fields are always valid. Theme manifest declared keys are added on top.

---

## Key Files

- **New**: `src/rockgarden/validation.py`
- **Modified**: `src/rockgarden/cli.py` — add `validate` command
- **New (per-theme, optional)**: `_themes/<name>/theme.toml`

---

## Verification

- `rockgarden validate` on a clean config → exits 0, "No issues found"
- Introduce a typo (`titl = "foo"`) → warning reported
- Set `timezone = "Bad/Zone"` → error reported, exit 1
- Set `theme.name` to nonexistent dir → warning reported
- Create a theme manifest with a required key, omit it from TOML → error reported, exit 1
- `uv run pytest` still passes (no regressions)
