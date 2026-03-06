"""User-defined Jinja2 macro support."""

import re
from pathlib import Path

from jinja2 import Environment, StrictUndefined

# Matches CommonMark code forms that must be protected from Jinja2 evaluation:
#   - Backtick fenced blocks (```) and multi-backtick spans (``) — {2,} covers both
#   - Tilde fenced blocks (~~~)
#   - Single-backtick inline spans
#   - Indented code block lines (4 spaces or tab at start of line)
_CODE_RE = re.compile(
    r"`{2,}[\s\S]*?`{2,}"
    r"|~{3,}[\s\S]*?~{3,}"
    r"|`[^`\n]+`"
    r"|^(?:    |\t)[^\n]*",
    re.DOTALL | re.MULTILINE,
)
_PLACEHOLDER_PREFIX = "\x00RGCODE"
_PLACEHOLDER_SUFFIX = "\x00"


def _protect_code(content: str) -> tuple[str, dict[str, str]]:
    """Replace code blocks/spans with placeholders safe from Jinja2 evaluation."""
    protected: dict[str, str] = {}

    def replace(m: re.Match) -> str:
        key = f"{_PLACEHOLDER_PREFIX}{len(protected)}{_PLACEHOLDER_SUFFIX}"
        protected[key] = m.group(0)
        return key

    return _CODE_RE.sub(replace, content), protected


def _restore_code(content: str, protected: dict[str, str]) -> str:
    for key, value in protected.items():
        content = content.replace(key, value)
    return content


def load_macros(macros_dir: Path) -> dict[str, str]:
    """Load all .html files from a _macros/ directory.

    Returns a dict mapping file stem to file contents, or {} if the
    directory does not exist.
    """
    if not macros_dir.exists():
        return {}
    return {f.stem: f.read_text() for f in sorted(macros_dir.glob("*.html"))}


def build_macro_renderer(macros: dict[str, str]):
    """Compile macro definitions into a reusable renderer.

    Returns a callable ``render(content, page)`` that applies macros to a
    content string, or ``None`` if macros is empty.

    Building the environment and preamble once per build avoids redundant
    compilation on every page.  Code blocks and inline code spans are
    protected from Jinja2 evaluation before rendering and restored after.
    """
    if not macros:
        return None

    preamble = "\n".join(macros.values())
    env = Environment(autoescape=False, undefined=StrictUndefined)

    def render(content: str, page) -> str:
        protected_content, code_blocks = _protect_code(content)
        full_template = preamble + "\n" + protected_content
        template = env.from_string(full_template)
        result = template.render(page=page)
        result = result.lstrip("\n")
        return _restore_code(result, code_blocks)

    return render


def preprocess_macros(content: str, macros: dict[str, str], page) -> str:
    """Render Jinja2 macro calls in markdown content before markdown processing.

    Macro definitions from all loaded files are prepended inline so that
    macros and the content share a single template scope.  This means macros
    can reference render-context variables (e.g. ``page``) without needing to
    receive them as explicit arguments.

    For repeated calls across many pages, prefer ``build_macro_renderer`` to
    avoid recompiling the environment on every call.

    Raises ``jinja2.TemplateError`` on syntax or render errors.
    """
    renderer = build_macro_renderer(macros)
    if renderer is None:
        return content
    return renderer(content, page)
