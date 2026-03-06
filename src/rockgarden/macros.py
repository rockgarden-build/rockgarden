"""User-defined Jinja2 macro support."""

from pathlib import Path

from jinja2 import Environment, StrictUndefined


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
    compilation on every page.
    """
    if not macros:
        return None

    preamble = "\n".join(macros.values())
    env = Environment(autoescape=False, undefined=StrictUndefined)

    def render(content: str, page) -> str:
        full_template = preamble + "\n" + content
        template = env.from_string(full_template)
        result = template.render(page=page)
        # The preamble (macro definitions) renders to empty/whitespace; strip
        # the leading newlines it introduces so downstream markdown sees clean
        # content.
        return result.lstrip("\n")

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
