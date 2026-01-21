"""Jinja2 template engine setup."""

from pathlib import Path

from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PackageLoader

from rockgarden.config import Config
from rockgarden.content.models import Page


def create_engine(
    config: Config,
    site_root: Path | None = None,
) -> Environment:
    """Create a Jinja2 environment with layered template loading.

    Resolution order (first match wins):
    1. Site templates (_templates/)
    2. Theme templates (_themes/<name>/)
    3. Built-in defaults (package templates)

    Args:
        config: The site configuration.
        site_root: Root directory of the site (for finding _templates/).

    Returns:
        Configured Jinja2 Environment.
    """
    loaders = []

    if site_root:
        site_templates = site_root / "_templates"
        if site_templates.exists():
            loaders.append(FileSystemLoader(site_templates))

        if config.theme.name:
            theme_templates = site_root / "_themes" / config.theme.name
            if theme_templates.exists():
                loaders.append(FileSystemLoader(theme_templates))

    loaders.append(PackageLoader("rockgarden", "templates"))

    return Environment(
        loader=ChoiceLoader(loaders),
        autoescape=True,
    )


def render_page(
    env: Environment,
    page: Page,
    site_config: dict,
    breadcrumbs: list | None = None,
) -> str:
    """Render a page using the page template.

    Args:
        env: The Jinja2 environment.
        page: The page to render.
        site_config: Site configuration to pass to template.
        breadcrumbs: Optional list of Breadcrumb objects for navigation.

    Returns:
        Rendered HTML string.
    """
    template = env.get_template("page.html")
    return template.render(page=page, site=site_config, breadcrumbs=breadcrumbs or [])
