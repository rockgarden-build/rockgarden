"""Theme export utilities."""

import json
import re
import shutil
from pathlib import Path

from rockgarden import __version__

_PACKAGE_DIR = Path(__file__).resolve().parent

_THEME_NAME_RE = re.compile(r"^[a-zA-Z0-9_-]+$")

_TAILWIND_CONFIG = """\
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./**/*.html"],
  theme: {
    extend: {
      typography: {
        DEFAULT: {
          css: {
            maxWidth: "none",
          },
        },
      },
    },
  },
  plugins: [require("@tailwindcss/typography"), require("daisyui")],
  daisyui: {
    themes: true,
  },
};
"""

_PACKAGE_JSON = (
    json.dumps(
        {
            "private": True,
            "scripts": {
                "build:css": (
                    "npx tailwindcss -i static-src/input.css"
                    " -o static/rockgarden.css --minify"
                ),
                "watch:css": (
                    "npx tailwindcss -i static-src/input.css"
                    " -o static/rockgarden.css --watch"
                ),
            },
            "devDependencies": {
                "@tailwindcss/typography": "^0.5.16",
                "daisyui": "^4.12.14",
                "tailwindcss": "^3.4.17",
            },
        },
        indent=2,
    )
    + "\n"
)


def validate_theme_name(name: str) -> None:
    """Raise ValueError if name contains characters unsafe for TOML or filesystem."""
    if not _THEME_NAME_RE.match(name):
        raise ValueError(
            f"Invalid theme name {name!r}. "
            "Use only letters, numbers, hyphens, and underscores."
        )


def export_theme(dest: Path) -> dict:
    """Export the bundled default theme to a directory.

    Args:
        dest: Target directory. Must not already exist.

    Returns:
        Dict with counts: {"templates": int, "static_files": int}

    Raises:
        FileExistsError: If dest already exists.
    """
    if dest.exists():
        raise FileExistsError(dest)

    try:
        dest.mkdir(parents=True)

        # Templates
        templates_src = _PACKAGE_DIR / "templates"
        shutil.copytree(templates_src, dest, dirs_exist_ok=True)
        template_count = sum(1 for _ in dest.rglob("*.html"))

        # Compiled CSS
        css_src = _PACKAGE_DIR / "static" / "rockgarden.css"
        static_dest = dest / "static"
        static_dest.mkdir()
        shutil.copy2(css_src, static_dest / "rockgarden.css")

        # CSS source
        input_css_src = _PACKAGE_DIR / "theme_src" / "input.css"
        static_src_dest = dest / "static-src"
        static_src_dest.mkdir()
        shutil.copy2(input_css_src, static_src_dest / "input.css")

        # Build tooling
        (dest / "tailwind.config.js").write_text(_TAILWIND_CONFIG)
        (dest / "package.json").write_text(_PACKAGE_JSON)

        # Theme manifest
        theme_name = dest.name
        theme_toml = (
            f"[theme]\n"
            f'name = "{theme_name}"\n'
            f'description = "Rockgarden default theme — Tailwind CSS + DaisyUI"\n'
            f'rockgarden_version = "{__version__}"\n'
        )
        (dest / "theme.toml").write_text(theme_toml)

        return {"templates": template_count, "static_files": 2}
    except Exception:
        shutil.rmtree(dest, ignore_errors=True)
        raise


def set_theme_name_in_config(config_path: Path, theme_name: str) -> None:
    """Update or add [theme] name = ... in a rockgarden.toml file."""
    content = config_path.read_text()
    lines = content.splitlines(keepends=True)

    in_theme = False
    theme_section_start = None
    name_line_idx = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[") and not stripped.startswith("[["):
            in_theme = stripped == "[theme]"
            if in_theme:
                theme_section_start = i
        elif in_theme and re.match(r"^name\s*=", stripped):
            name_line_idx = i

    if name_line_idx is not None:
        lines[name_line_idx] = f'name = "{theme_name}"\n'
        config_path.write_text("".join(lines))
    elif theme_section_start is not None:
        if not lines[theme_section_start].endswith("\n"):
            lines[theme_section_start] += "\n"
        lines.insert(theme_section_start + 1, f'name = "{theme_name}"\n')
        config_path.write_text("".join(lines))
    else:
        suffix = "\n" if content.endswith("\n") else "\n\n"
        config_path.write_text(content + f'{suffix}[theme]\nname = "{theme_name}"\n')
