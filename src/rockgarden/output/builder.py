"""Site building orchestration."""

from pathlib import Path

from rockgarden.config import Config
from rockgarden.content import load_content
from rockgarden.render import create_engine, render_markdown, render_page


def build_site(config: Config, source: Path, output: Path) -> int:
    """Build the static site.

    Args:
        config: The site configuration.
        source: Source directory containing markdown files.
        output: Output directory for generated HTML.

    Returns:
        Number of pages built.
    """
    output.mkdir(parents=True, exist_ok=True)

    pages = load_content(source, config.build.ignore_patterns)

    env = create_engine(config, site_root=source.parent)

    site_config = {"title": config.site.title}

    count = 0
    for page in pages:
        page.html = render_markdown(page.content)

        html = render_page(env, page, site_config)

        output_file = output / page.output_path
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html)

        count += 1

    return count
