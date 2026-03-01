"""Jinja2 template engine setup."""

from datetime import datetime
from datetime import timezone as dt_timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PackageLoader

from rockgarden.config import Config
from rockgarden.content.models import Page
from rockgarden.nav.tree import NavNode
from rockgarden.urls import get_tag_url, get_tags_root_url


def _make_format_datetime(tz_name: str):
    tz = ZoneInfo(tz_name)

    def format_datetime(dt: datetime | None, fmt: str = "%Y-%m-%d") -> str:
        if dt is None:
            return ""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=dt_timezone.utc)
        return dt.astimezone(tz).strftime(fmt)

    return format_datetime


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

    env = Environment(
        loader=ChoiceLoader(loaders),
        autoescape=True,
    )
    env.filters["format_datetime"] = _make_format_datetime(config.dates.timezone)
    clean_urls = config.site.clean_urls
    env.globals["tag_url"] = lambda slug: get_tag_url(slug, clean_urls)
    env.globals["tags_root_url"] = get_tags_root_url(clean_urls)
    return env


def render_page(
    env: Environment,
    page: Page,
    site_config: dict,
    breadcrumbs: list | None = None,
    backlinks: NavNode | None = None,
    toc: list | None = None,
) -> str:
    """Render a page using the page template.

    Args:
        env: The Jinja2 environment.
        page: The page to render.
        site_config: Site configuration to pass to template.
        breadcrumbs: Optional list of Breadcrumb objects for navigation.
        backlinks: Optional NavNode tree of pages that link to this page.
        toc: Optional list of TocEntry trees for table of contents.

    Returns:
        Rendered HTML string.
    """
    template = env.get_template("page.html")
    return template.render(
        page=page,
        site=site_config,
        breadcrumbs=breadcrumbs or [],
        backlinks=backlinks,
        toc=toc,
    )
