"""Site building orchestration."""

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from rockgarden.assets import (
    build_media_index,
    collect_markdown_images,
    copy_assets,
    create_media_resolver,
)
from rockgarden.config import Config
from rockgarden.content import (
    ContentStore,
    build_link_index,
    load_content,
    strip_content_title,
)
from rockgarden.icons import configure_icons_dir
from rockgarden.links import transform_md_links
from rockgarden.nav import (
    build_breadcrumbs,
    build_nav_tree,
    extract_toc,
    generate_folder_indexes,
)
from rockgarden.obsidian import (
    process_callouts,
    process_media_embeds,
    process_wikilinks,
)
from rockgarden.output.search import build_search_index
from rockgarden.output.sitemap import build_sitemap
from rockgarden.render import create_engine, render_markdown, render_page
from rockgarden.urls import get_folder_url, get_output_path, get_url


@dataclass
class BuildResult:
    """Result of building the site.

    Attributes:
        page_count: Number of pages built.
        broken_links: Mapping of source filenames to lists of broken link targets.
    """

    page_count: int
    broken_links: dict[str, list[str]]


def copy_static_files(output: Path) -> None:
    """Copy bundled static assets (CSS, JS) to the output directory."""
    static_src = Path(__file__).resolve().parent.parent / "static"
    static_dst = output / "_static"
    if static_src.exists():
        shutil.copytree(static_src, static_dst, dirs_exist_ok=True)


def build_site(config: Config, source: Path, output: Path) -> BuildResult:
    """Build the static site.

    Args:
        config: The site configuration.
        source: Source directory containing markdown files.
        output: Output directory for generated HTML.

    Returns:
        BuildResult with page count and broken links information.
    """
    output.mkdir(parents=True, exist_ok=True)
    copy_static_files(output)

    if config.build.icons_dir:
        configure_icons_dir((source.parent / config.build.icons_dir).resolve())

    pages = load_content(source, config.build.ignore_patterns, config.dates)
    clean_urls = config.site.clean_urls

    # Build media index before creating store so it can resolve media file links
    media_index = build_media_index(source)
    store = ContentStore(pages, clean_urls, media_index)

    link_index = build_link_index(pages, store)

    nav_tree = build_nav_tree(pages, config.nav, clean_urls)

    env = create_engine(config, site_root=source.parent)

    site_config = {
        "title": config.site.title,
        "nav": nav_tree,
        "nav_default_state": config.nav.default_state,
        "daisyui_theme": config.theme.daisyui_default,
        "daisyui_themes": config.theme.daisyui_themes,
        "search_enabled": config.search.enabled,
    }

    show_index_map = {}
    for p in pages:
        parts = p.slug.split("/")
        if parts[-1] == "index":
            folder_path = "/".join(parts[:-1])
            show_index = p.frontmatter.get("show_index", False)
            show_index_map[folder_path] = show_index
    all_media: set[str] = set()
    broken_links_by_page: dict[str, list[str]] = {}

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
        content, broken = process_wikilinks(content, store.resolve_link)
        if broken:
            source_file = page.source_path.name
            broken_links_by_page[source_file] = [target for target, _ in broken]
        content = transform_md_links(content, clean_urls)
        page.html = process_callouts(render_markdown(content))

        toc_entries = None
        if config.toc.enabled:
            page.html, toc_entries = extract_toc(
                page.html, max_level=config.toc.max_depth
            )

        breadcrumbs = build_breadcrumbs(page, pages, config.nav, clean_urls)

        # Get backlinks if enabled
        backlinks_tree = None
        if config.backlinks.enabled:
            backlink_slugs = link_index.get_backlinks(page.slug)
            backlink_pages = [
                store.get_by_slug(slug)
                for slug in backlink_slugs
                if store.get_by_slug(slug)
            ]
            if backlink_pages:
                backlinks_tree = build_nav_tree(backlink_pages, config.nav, clean_urls)

        html = render_page(
            env, page, site_config, breadcrumbs, backlinks_tree, toc_entries
        )

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
            processed, broken = process_wikilinks(processed, store.resolve_link)
            if broken:
                broken_links_by_page[folder_src] = [target for target, _ in broken]
            processed = transform_md_links(processed, clean_urls)
            folder.custom_content = process_callouts(render_markdown(processed))

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

    # Generate search index if enabled
    if config.search.enabled:
        search_index = build_search_index(
            pages, config.search.include_content, clean_urls
        )
        search_index_file = output / "search-index.json"
        search_index_file.write_text(json.dumps(search_index))

    # Generate sitemap if base_url is configured
    if config.site.base_url:
        sitemap_xml = build_sitemap(
            pages, folder_indexes, config.site.base_url, clean_urls
        )
        (output / "sitemap.xml").write_text(sitemap_xml)

    return BuildResult(page_count=count, broken_links=broken_links_by_page)


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
