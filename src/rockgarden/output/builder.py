"""Site building orchestration."""

from pathlib import Path

from rockgarden.config import Config
from rockgarden.content import ContentStore, load_content, strip_content_title
from rockgarden.links import transform_md_links
from rockgarden.nav import (
    build_breadcrumbs,
    build_nav_tree,
    generate_folder_indexes,
)
from rockgarden.obsidian import process_wikilinks
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
    store = ContentStore(pages)

    nav_tree = build_nav_tree(pages, config.nav)

    env = create_engine(config, site_root=source.parent)

    site_config = {
        "title": config.site.title,
        "nav": nav_tree,
        "nav_default_state": config.nav.default_state,
    }

    indexes_with_auto = {}
    for p in pages:
        parts = p.slug.split("/")
        if parts[-1].lower() == "index":
            folder_path = "/".join(parts[:-1])
            auto_index = p.frontmatter.get("auto_index", True)
            indexes_with_auto[folder_path] = auto_index

    count = 0
    for page in pages:
        parts = page.slug.split("/")
        if parts[-1].lower() == "index":
            folder_path = "/".join(parts[:-1])
            if indexes_with_auto.get(folder_path, True):
                continue

        content = page.content

        if page.frontmatter.get("title"):
            content = strip_content_title(content)

        content = process_wikilinks(content, store.resolve_link)
        content = transform_md_links(content)
        page.html = render_markdown(content)

        breadcrumbs = build_breadcrumbs(page, pages, config.nav)
        html = render_page(env, page, site_config, breadcrumbs)

        output_file = output / page.output_path
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html)

        count += 1

    folder_indexes = generate_folder_indexes(pages, config.nav)
    folder_template = env.get_template("folder_index.html")

    for folder in folder_indexes:
        folder_path = folder.slug.rsplit("/", 1)[0] if "/" in folder.slug else ""
        if folder_path in indexes_with_auto and not indexes_with_auto[folder_path]:
            continue

        if folder.custom_content:
            processed = folder.custom_content
            if folder.frontmatter.get("title"):
                processed = strip_content_title(processed)
            processed = process_wikilinks(processed, store.resolve_link)
            processed = transform_md_links(processed)
            folder.custom_content = render_markdown(processed)

        breadcrumbs = _build_folder_breadcrumbs(folder, pages, config.nav)

        html = folder_template.render(
            folder=folder,
            site=site_config,
            breadcrumbs=breadcrumbs,
        )

        output_file = output / f"{folder.slug}.html"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html)

        count += 1

    return count


def _build_folder_breadcrumbs(folder, pages, nav_config):
    """Build breadcrumbs for a folder index page."""
    from rockgarden.nav import Breadcrumb

    folder_pages: dict[str, any] = {}
    for p in pages:
        parts = p.slug.split("/")
        if parts[-1].lower() == "index":
            folder_path = "/".join(parts[:-1])
            folder_pages[folder_path] = p

    breadcrumbs = []

    root_label = nav_config.labels.get("/", "Home")
    if "" in folder_pages and folder_pages[""].frontmatter.get("title"):
        root_label = folder_pages[""].frontmatter["title"]
    breadcrumbs.append(Breadcrumb(label=root_label, path="/index.html"))

    folder_path = folder.slug.rsplit("/", 1)[0] if "/" in folder.slug else ""
    if not folder_path:
        return breadcrumbs

    parts = folder_path.split("/")
    current_parts = []

    for part in parts:
        current_parts.append(part)
        path = "/".join(current_parts)

        label = nav_config.labels.get(f"/{path}", None)
        if not label and path in folder_pages:
            label = folder_pages[path].frontmatter.get("title")
        if not label:
            label = part.replace("-", " ").replace("_", " ").title()

        breadcrumbs.append(Breadcrumb(label=label, path=f"/{path}/index.html"))

    return breadcrumbs
