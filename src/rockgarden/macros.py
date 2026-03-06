"""User-defined Jinja2 macro support."""

from pathlib import Path

from jinja2 import Environment


def load_macros(macros_dir: Path) -> dict[str, str]:
    """Load all .html files from a _macros/ directory.

    Returns a dict mapping file stem to file contents, or {} if the
    directory does not exist.
    """
    if not macros_dir.exists():
        return {}
    return {f.stem: f.read_text() for f in sorted(macros_dir.glob("*.html"))}


def preprocess_macros(content: str, macros: dict[str, str], page) -> str:
    """Render Jinja2 macro calls in markdown content before markdown processing.

    Macro definitions from all loaded files are prepended inline so that
    macros and the content share a single template scope.  This means macros
    can reference render-context variables (e.g. ``page``) without needing to
    receive them as explicit arguments.

    Raises ``jinja2.TemplateError`` on syntax or render errors.
    """
    if not macros:
        return content

    preamble = "\n".join(macros.values())
    full_template = preamble + "\n" + content

    env = Environment(autoescape=False)
    template = env.from_string(full_template)
    result = template.render(page=page)
    # The preamble (macro definitions) renders to empty/whitespace; strip the
    # leading newlines it introduces so downstream markdown sees clean content.
    return result.lstrip("\n")
