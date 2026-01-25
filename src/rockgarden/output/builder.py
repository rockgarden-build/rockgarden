"""Site building orchestration."""

from pathlib import Path

from rockgarden.assets import (
    build_media_index,
    collect_markdown_images,
    copy_assets,
    create_media_resolver,
)
from rockgarden.config import Config
from rockgarden.content import ContentStore, load_content, strip_content_title
from rockgarden.links import transform_md_links
from rockgarden.nav import (
    build_breadcrumbs,
    build_nav_tree,
    generate_folder_indexes,
)
from rockgarden.obsidian import process_media_embeds, process_wikilinks
from rockgarden.render import create_engine, render_markdown, render_page
from rockgarden.urls import get_folder_url, get_output_path


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
    clean_urls = config.site.clean_urls
    store = ContentStore(pages, clean_urls)

    nav_tree = build_nav_tree(pages, config.nav, clean_urls)

    env = create_engine(config, site_root=source.parent)

    site_config = {
        "title": config.site.title,
        "nav": nav_tree,
        "nav_default_state": config.nav.default_state,
        "daisyui_theme": config.theme.daisyui,
    }

    show_index_map = {}
    for p in pages:
        parts = p.slug.split("/")
        if parts[-1] == "index":
            folder_path = "/".join(parts[:-1])
            show_index = p.frontmatter.get("show_index", False)
            show_index_map[folder_path] = show_index

    media_index = build_media_index(source)
    all_media: set[str] = set()

    count = 0
    for page in pages:
        parts = page.slug.split("/")
        if parts[-1] == "index":
            folder_path = "/".join(parts[:-1])
            if show_index_map.get(folder_path, False):
                continue

        content = page.content

        if page.frontmatter.get("title"):
            content = strip_content_title(content)

        page_rel_path = str(page.source_path.relative_to(source))
        media_resolver = create_media_resolver(source, page_rel_path, media_index)
        content, media = process_media_embeds(content, media_resolver)
        all_media.update(media)
        all_media.update(collect_markdown_images(content, media_resolver))
        content = process_wikilinks(content, store.resolve_link)
        content = transform_md_links(content, clean_urls)
        page.html = render_markdown(content)

        breadcrumbs = build_breadcrumbs(page, pages, config.nav, clean_urls)
        html = render_page(env, page, site_config, breadcrumbs)

        output_file = output / get_output_path(page.slug, clean_urls)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html)

        count += 1

    folder_indexes = generate_folder_indexes(pages, config.nav, clean_urls)
    folder_template = env.get_template("folder_index.html")

    for folder in folder_indexes:
        folder_path = folder.slug.rsplit("/", 1)[0] if "/" in folder.slug else ""
        if folder_path in show_index_map and not show_index_map[folder_path]:
            continue

        if folder.custom_content:
            processed = folder.custom_content
            if folder.frontmatter.get("title"):
                processed = strip_content_title(processed)
            folder_src = folder_path + "/index.md" if folder_path else "index.md"
            media_resolver = create_media_resolver(source, folder_src, media_index)
            processed, media = process_media_embeds(processed, media_resolver)
            all_media.update(media)
            all_media.update(collect_markdown_images(processed, media_resolver))
            processed = process_wikilinks(processed, store.resolve_link)
            processed = transform_md_links(processed, clean_urls)
            folder.custom_content = render_markdown(processed)

        breadcrumbs = _build_folder_breadcrumbs(folder, pages, config.nav, clean_urls)

        html = folder_template.render(
            folder=folder,
            site=site_config,
            breadcrumbs=breadcrumbs,
        )

        output_file = output / get_output_path(folder.slug, clean_urls)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html)

        count += 1

    copy_assets(all_media, source, output)

    return count


def _build_folder_breadcrumbs(folder, pages, nav_config, clean_urls=True):
    """Build breadcrumbs for a folder index page."""
    from rockgarden.nav import Breadcrumb, resolve_label

    folder_pages: dict[str, any] = {}
    for p in pages:
        parts = p.slug.split("/")
        if parts[-1] == "index":
            folder_path = "/".join(parts[:-1])
            folder_pages[folder_path] = p

    breadcrumbs = []

    root_label = resolve_label("", "Home", nav_config.labels, folder_pages)
    root_path = get_folder_url("", clean_urls)
    breadcrumbs.append(Breadcrumb(label=root_label, path=root_path))

    folder_path = folder.slug.rsplit("/", 1)[0] if "/" in folder.slug else ""
    if not folder_path:
        return breadcrumbs

    parts = folder_path.split("/")
    current_parts = []

    for part in parts:
        current_parts.append(part)
        path = "/".join(current_parts)

        label = resolve_label(path, part, nav_config.labels, folder_pages)
        folder_url = get_folder_url(path, clean_urls)
        breadcrumbs.append(Breadcrumb(label=label, path=folder_url))

    return breadcrumbs
