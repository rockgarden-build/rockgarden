"""Site building orchestration."""

import hashlib
import json
import shutil
import sys
import time
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
    Page,
    build_link_index,
    entry_fields,
    generate_collection_url,
    get_collection_skip_slugs,
    load_collection_data_files,
    load_content,
    partition_collections,
    resolve_model,
    strip_content_title,
    validate_entry,
)
from rockgarden.hooks import run_hooks
from rockgarden.icons import configure_icons_dir, process_inline_icons
from rockgarden.links import transform_md_links
from rockgarden.macros import build_macro_renderer, load_macros
from rockgarden.nav import (
    build_breadcrumbs,
    build_nav_tree,
    extract_toc,
    generate_folder_indexes,
    inject_nav_links,
)
from rockgarden.obsidian import (
    process_callouts,
    process_media_embeds,
    process_note_transclusions,
    process_wikilinks,
)
from rockgarden.output.build_info import get_build_info
from rockgarden.output.feed import build_atom_feed
from rockgarden.output.llms_txt import build_llms_full_txt, build_llms_txt
from rockgarden.output.search import build_search_index, strip_html
from rockgarden.output.sitemap import build_sitemap
from rockgarden.output.tags import build_tag_pages, collect_tags
from rockgarden.render import (
    create_engine,
    render_markdown,
    render_page,
    resolve_layout,
)
from rockgarden.urls import get_base_path, get_folder_url, get_output_path


@dataclass
class BuildResult:
    """Result of building the site.

    Attributes:
        page_count: Number of pages built.
        broken_links: Mapping of source filenames to lists of broken link targets.
        duration_seconds: Total build time in seconds.
    """

    page_count: int
    broken_links: dict[str, list[str]]
    duration_seconds: float = 0.0


def copy_static_files(output: Path, assets_dir: str = "_assets") -> None:
    """Copy bundled static assets (CSS, JS) to the output directory."""
    static_src = Path(__file__).resolve().parent.parent / "static"
    static_dst = output / assets_dir
    if static_src.exists():
        shutil.copytree(static_src, static_dst, dirs_exist_ok=True)


def copy_theme_static_files(
    theme_name: str, site_root: Path, output: Path, assets_dir: str = "_assets"
) -> None:
    """Copy theme static files to output, overriding bundled statics."""
    if not theme_name:
        return
    theme_static = site_root / "_themes" / theme_name / "static"
    if theme_static.exists():
        shutil.copytree(theme_static, output / assets_dir, dirs_exist_ok=True)


def discover_user_assets(site_root: Path) -> tuple[list[str], list[str]]:
    """Discover user-provided CSS and JS files.

    Args:
        site_root: Root directory of the site (parent of content source).

    Returns:
        Tuple of (style filenames, script filenames), each sorted.
    """
    styles_dir = site_root / "_styles"
    scripts_dir = site_root / "_scripts"
    styles = (
        sorted(p.name for p in styles_dir.glob("*.css")) if styles_dir.exists() else []
    )
    scripts = (
        sorted(p.name for p in scripts_dir.glob("*.js")) if scripts_dir.exists() else []
    )
    return styles, scripts


def copy_user_assets(
    site_root: Path, output: Path, styles: list[str], scripts: list[str]
) -> None:
    """Copy user-provided CSS and JS files to the output directory."""
    if styles:
        out_styles = output / "styles"
        out_styles.mkdir(parents=True, exist_ok=True)
        for name in styles:
            shutil.copy2(site_root / "_styles" / name, out_styles / name)
    if scripts:
        out_scripts = output / "scripts"
        out_scripts.mkdir(parents=True, exist_ok=True)
        for name in scripts:
            shutil.copy2(site_root / "_scripts" / name, out_scripts / name)


def copy_user_static_files(site_root: Path, output: Path) -> None:
    """Copy user _static/ directory contents to the output root."""
    static_dir = site_root / "_static"
    if static_dir.exists():
        shutil.copytree(static_dir, output, dirs_exist_ok=True)


def _static_hash(output: Path, assets_dir: str = "_assets") -> str:
    """Generate a short content hash of static CSS files for cache busting."""
    assets = output / assets_dir
    if not assets.exists():
        return ""
    files = sorted(assets.glob("*.css"))
    if not files:
        return ""
    hasher = hashlib.md5()
    for css_file in files:
        hasher.update(css_file.read_bytes())
    return hasher.hexdigest()[:8]


def _make_note_resolver(
    store,
    source: Path,
    media_index: dict,
    clean_urls: bool,
    visited: frozenset[str],
    all_media: set[str],
    broken_links: dict[str, list[str]],
    base_path: str = "",
):
    """Return a transclusion resolver that renders a note's content as HTML.

    The resolver performs cycle detection via the visited set and runs the same
    processing pipeline as the main build loop (media embeds, transclusions,
    wikilinks, markdown render, callouts). Media files and broken links found
    inside transclusions are propagated to the caller's all_media and broken_links.
    """

    def resolve(target: str) -> str | None:
        name = target.strip()
        if name.lower().endswith(".md"):
            name = name[:-3]

        page = store.get_by_name(name)
        if page is None or page.slug in visited:
            return None

        new_visited = visited | {page.slug}
        page_rel_path = str(page.source_path.relative_to(source))
        media_resolver = create_media_resolver(
            source, page_rel_path, media_index, base_path
        )

        sub_content = page.content
        sub_content, media = process_media_embeds(sub_content, media_resolver)
        all_media.update(media)
        all_media.update(collect_markdown_images(sub_content, media_resolver))
        sub_content = process_note_transclusions(
            sub_content,
            _make_note_resolver(
                store,
                source,
                media_index,
                clean_urls,
                new_visited,
                all_media,
                broken_links,
                base_path,
            ),
        )
        sub_content, sub_broken = process_wikilinks(sub_content, store.resolve_link)
        if sub_broken:
            broken_links.setdefault(page.source_path.name, []).extend(
                t for t, _ in sub_broken
            )
        sub_content = transform_md_links(sub_content, clean_urls)
        return process_callouts(render_markdown(sub_content))

    return resolve


def _warn_gitignore(site_root: Path) -> None:
    """Warn if .rockgarden/ is not in .gitignore for a git repo."""
    git_path = site_root / ".git"
    if not git_path.exists():
        return
    gitignore = site_root / ".gitignore"
    if gitignore.exists():
        for line in gitignore.read_text().splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            normalized = stripped.lstrip("/").rstrip("/")
            if normalized == ".rockgarden":
                return
    print(
        "Warning: .rockgarden/ is not in .gitignore. "
        "Consider adding it to avoid committing build artifacts.",
        file=sys.stderr,
    )


def _serialize_page(page, site_root: Path, clean_urls: bool, base_path: str) -> dict:
    """Serialize a Page to a JSON-safe dict."""
    from rockgarden.urls import get_url

    return {
        "slug": page.slug,
        "title": page.title,
        "url": get_url(page.slug, clean_urls, base_path),
        "tags": page.frontmatter.get("tags", []),
        "frontmatter": {
            k: (
                v
                if isinstance(v, (str, int, float, bool, list, dict, type(None)))
                else str(v)
            )
            for k, v in page.frontmatter.items()
        },
        "modified": page.modified.isoformat() if page.modified else None,
        "created": page.created.isoformat() if page.created else None,
        "source_path": str(
            page.source_path.relative_to(site_root)
            if page.source_path.is_absolute()
            else page.source_path
        ),
    }


def _serialize_entry(entry, site_root: Path, clean_urls: bool, base_path: str) -> dict:
    """Serialize a collection entry (Page or dict) to a JSON-safe dict."""
    from rockgarden.content.models import Page

    if isinstance(entry, Page):
        return _serialize_page(entry, site_root, clean_urls, base_path)
    return entry


def export_content_json(
    pages: list,
    site_root: Path,
    clean_urls: bool,
    base_path: str,
    collections: dict | None = None,
) -> Path:
    """Export collected content metadata to .rockgarden/content.json.

    Returns the path to the written JSON file.
    """
    page_data = [
        _serialize_page(page, site_root, clean_urls, base_path) for page in pages
    ]

    collections_data = {}
    if collections:
        for name, collection in collections.items():
            collections_data[name] = [
                _serialize_entry(entry, site_root, clean_urls, base_path)
                for entry in collection.entries
            ]

    data = {"pages": page_data, "collections": collections_data}

    out_dir = site_root / ".rockgarden"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "content.json"
    out_path.write_text(json.dumps(data, indent=2, default=str))
    return out_path


def build_collection_pages(
    collections: dict,
    env,
    site_config: dict,
    output: Path,
    clean_urls: bool,
    base_path: str,
    config: Config,
) -> list[dict]:
    """Generate HTML pages for collections with page generation enabled.

    Returns a list of search-index-ready dicts for the generated pages.
    """
    from rockgarden.content.models import Page

    generated = []

    for col in collections.values():
        if not col.generates_pages:
            continue

        template = env.get_template(col.config.template)
        layout_template = resolve_layout({}, config.theme.default_layout)

        for entry in col.entries:
            url = generate_collection_url(col.config.url_pattern, entry)
            slug = url.strip("/")

            html_content = None
            if isinstance(entry, Page) and entry.content:
                html_content = process_callouts(render_markdown(entry.content))

            fields = entry_fields(entry)
            rendered = template.render(
                entry=fields,
                entry_obj=entry,
                html_content=html_content,
                collection=col,
                site=site_config,
                layout_template=layout_template,
            )

            output_file = output / get_output_path(slug, clean_urls)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(rendered)

            generated.append(
                {
                    "title": fields.get("title", fields.get("name", slug)),
                    "url": f"{base_path}{url}",
                    "slug": slug,
                    "collection": col.name,
                    "rendered_html": rendered,
                }
            )

    return generated


def build_site(
    config: Config,
    source: Path,
    output: Path,
    project_root: Path | None = None,
) -> BuildResult:
    """Build the static site.

    Args:
        config: The site configuration.
        source: Source directory containing markdown files.
        output: Output directory for generated HTML.
        project_root: Root directory of the project (where _themes/, _templates/
            etc. live). Defaults to source.parent for backward compatibility.

    Returns:
        BuildResult with page count and broken links information.
    """
    _start = time.perf_counter()
    output.mkdir(parents=True, exist_ok=True)
    assets_dir = config.build.assets_dir
    copy_static_files(output, assets_dir)

    site_root = project_root if project_root is not None else source.parent
    macros = load_macros(site_root / "_macros")
    apply_macros = build_macro_renderer(macros)
    copy_theme_static_files(config.theme.name, site_root, output, assets_dir)
    user_styles, user_scripts = discover_user_assets(site_root)
    copy_user_assets(site_root, output, user_styles, user_scripts)

    if config.build.icons_dir:
        configure_icons_dir((site_root / config.build.icons_dir).resolve())

    hook_env = {
        "ROCKGARDEN_SOURCE": str(source.resolve()),
        "ROCKGARDEN_OUTPUT": str(output.resolve()),
    }
    run_hooks(config.hooks.pre_build, "pre_build", cwd=site_root, env_vars=hook_env)

    pages = load_content(
        source, config.build.ignore_patterns, config.dates, config.site.url_style
    )
    clean_urls = config.site.clean_urls
    base_path = config.site.base_path or get_base_path(config.site.base_url)

    collections = partition_collections(pages, config.collections, source)

    for col in collections.values():
        data_entries = load_collection_data_files(source, col.config.source)
        col.entries.extend(data_entries)

    validated_entries: set[tuple[int, type]] = set()
    for col in collections.values():
        if col.config.model:
            model_class = resolve_model(col.config.model, site_root, config.theme.name)
            if model_class is None:
                raise ValueError(
                    f"Collection '{col.name}' references model '{col.config.model}' "
                    f"but no model file was found"
                )
            for entry in col.entries:
                key = (id(entry), model_class)
                if key in validated_entries:
                    continue
                validate_entry(entry, model_class, col.name)
                validated_entries.add(key)

    # Build media index before creating store so it can resolve media file links
    media_index = build_media_index(source)
    store = ContentStore(pages, clean_urls, media_index, base_path, collections)

    link_index = build_link_index(pages, store)

    has_post_hooks = config.hooks.post_collect or config.hooks.post_build
    if has_post_hooks:
        content_json_path = export_content_json(
            pages, site_root, clean_urls, base_path, collections
        )
        hook_env["ROCKGARDEN_CONTENT_JSON"] = str(content_json_path.resolve())
        _warn_gitignore(site_root)
    run_hooks(
        config.hooks.post_collect,
        "post_collect",
        cwd=site_root,
        env_vars=hook_env,
    )

    nav_tree = build_nav_tree(pages, config.nav, clean_urls, base_path)

    env = create_engine(config, site_root=site_root, base_path=base_path)
    env.globals["collections"] = {
        name: col.entries for name, col in collections.items()
    }

    cache_hash = _static_hash(output, assets_dir)

    build_info = None
    if config.theme.show_build_info:
        build_info = get_build_info(
            source.parent,
            include_git=config.theme.show_build_commit,
        )

    site_config = {
        "title": config.site.title,
        "description": config.site.description,
        "og_image": config.site.og_image,
        "base_url": config.site.base_url,
        "base_path": base_path,
        "clean_urls": config.site.clean_urls,
        "tag_index": config.theme.tag_index,
        "nav": nav_tree,
        "nav_default_state": config.theme.nav_default_state,
        "daisyui_theme": config.theme.daisyui_default,
        "daisyui_themes": config.theme.daisyui_themes,
        "search_enabled": config.theme.search,
        "build_info": build_info,
        "cache_hash": cache_hash,
        "user_styles": user_styles,
        "user_scripts": user_scripts,
        "assets_dir": assets_dir,
        "main_content_padding": config.theme.main_content_padding,
        "feed_enabled": config.feed.enabled and bool(config.site.base_url),
        "feed_path": config.feed.path,
    }

    show_index_map = {}
    for p in pages:
        parts = p.slug.split("/")
        if parts[-1] == "index":
            folder_path = "/".join(parts[:-1])
            show_index = p.frontmatter.get("show_index", False)
            show_index_map[folder_path] = show_index
    # Pre-compute collection nav nodes so they're visible to all templates
    # (including collection page templates themselves).
    from rockgarden.nav.tree import NavNode

    for col in collections.values():
        if not col.config.nav or not col.generates_pages:
            continue
        children = []
        for entry in col.entries:
            url = generate_collection_url(col.config.url_pattern, entry)
            slug = url.strip("/")
            fields = entry_fields(entry)
            title = fields.get("title", fields.get("name", slug))
            children.append(
                NavNode(
                    name=slug.rsplit("/", 1)[-1],
                    path=f"{base_path}{url}",
                    label=title,
                    is_folder=False,
                )
            )
        if not children:
            continue
        children.sort(key=lambda n: n.label.lower())
        col_node = NavNode(
            name=col.name,
            path=children[0].path,
            label=col.name,
            is_folder=True,
            children=children,
        )
        nav_tree.children.append(col_node)

    inject_nav_links(
        nav_tree, config.nav.links, config.nav.links_position, config.nav.sort
    )

    # Generate collection pages (nav tree is fully populated at this point).
    collection_page_entries = build_collection_pages(
        collections,
        env,
        site_config,
        output,
        clean_urls,
        base_path,
        config,
    )

    all_media: set[str] = set()
    broken_links_by_page: dict[str, list[str]] = {}
    collection_skip_slugs = get_collection_skip_slugs(collections)

    count = len(collection_page_entries)
    for page in pages:
        if page.slug in collection_skip_slugs:
            continue

        parts = page.slug.split("/")
        if parts[-1] == "index":
            folder_path = "/".join(parts[:-1])
            if show_index_map.get(folder_path, False):
                continue

        content = page.content

        content = strip_content_title(content)
        if apply_macros:
            content = apply_macros(content, page)

        page_rel_path = str(page.source_path.relative_to(source))
        media_resolver = create_media_resolver(
            source, page_rel_path, media_index, base_path
        )
        content, media = process_media_embeds(content, media_resolver)
        all_media.update(media)
        all_media.update(collect_markdown_images(content, media_resolver))
        content = process_note_transclusions(
            content,
            _make_note_resolver(
                store,
                source,
                media_index,
                clean_urls,
                frozenset({page.slug}),
                all_media,
                broken_links_by_page,
                base_path,
            ),
        )
        content, broken = process_wikilinks(content, store.resolve_link)
        if broken:
            source_file = page.source_path.name
            broken_links_by_page[source_file] = [target for target, _ in broken]
        content = transform_md_links(content, clean_urls)
        if config.build.inline_icons:
            content = process_inline_icons(content)
        page.html = process_callouts(render_markdown(content))

        toc_entries = None
        if config.theme.toc:
            page.html, toc_entries = extract_toc(
                page.html, max_level=config.toc.max_depth
            )

        breadcrumbs = build_breadcrumbs(page, pages, config.nav, clean_urls, base_path)

        # Get backlinks if enabled
        backlinks_tree = None
        if config.theme.backlinks:
            backlink_slugs = link_index.get_backlinks(page.slug)
            backlink_pages = [
                store.get_by_slug(slug)
                for slug in backlink_slugs
                if store.get_by_slug(slug)
            ]
            if backlink_pages:
                backlinks_tree = build_nav_tree(
                    backlink_pages, config.nav, clean_urls, base_path
                )

        layout_template = resolve_layout(page.frontmatter, config.theme.default_layout)
        html = render_page(
            env,
            page,
            site_config,
            breadcrumbs,
            backlinks_tree,
            toc_entries,
            layout_template,
        )

        output_file = output / get_output_path(page.slug, clean_urls)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html)

        count += 1

    folder_indexes = generate_folder_indexes(
        pages, config.nav, clean_urls, base_path, config.site.title
    )
    rendered_folder_indexes: list = []
    folder_template = env.get_template("folder_index.html")

    for folder in folder_indexes:
        folder_path = folder.slug.rsplit("/", 1)[0] if "/" in folder.slug else ""
        if folder_path in show_index_map and not show_index_map[folder_path]:
            continue

        if folder.custom_content:
            processed = folder.custom_content
            processed = strip_content_title(processed)
            if apply_macros:
                processed = apply_macros(processed, folder)
            folder_src = folder_path + "/index.md" if folder_path else "index.md"
            media_resolver = create_media_resolver(
                source, folder_src, media_index, base_path
            )
            processed, media = process_media_embeds(processed, media_resolver)
            all_media.update(media)
            all_media.update(collect_markdown_images(processed, media_resolver))
            processed = process_note_transclusions(
                processed,
                _make_note_resolver(
                    store,
                    source,
                    media_index,
                    clean_urls,
                    frozenset({folder.slug}),
                    all_media,
                    broken_links_by_page,
                    base_path,
                ),
            )
            processed, broken = process_wikilinks(processed, store.resolve_link)
            if broken:
                broken_links_by_page[folder_src] = [target for target, _ in broken]
            processed = transform_md_links(processed, clean_urls)
            folder.custom_content = process_callouts(render_markdown(processed))

        breadcrumbs = _build_folder_breadcrumbs(
            folder, pages, config.nav, clean_urls, base_path
        )

        folder_layout = resolve_layout(folder.frontmatter, config.theme.default_layout)
        html = folder_template.render(
            folder=folder,
            site=site_config,
            breadcrumbs=breadcrumbs,
            layout_template=folder_layout,
        )

        output_file = output / get_output_path(folder.slug, clean_urls)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html)
        rendered_folder_indexes.append(folder)

        count += 1

    copy_assets(all_media, source, output)

    # Generate search index if enabled
    if config.theme.search:
        searchable_pages = [p for p in pages if p.slug not in collection_skip_slugs]
        search_index = build_search_index(
            searchable_pages, config.search.include_content, clean_urls, base_path
        )

        for entry in collection_page_entries:
            search_entry = {
                "title": entry["title"],
                "url": entry["url"],
            }
            if config.search.include_content and entry.get("rendered_html"):
                search_entry["content"] = strip_html(entry["rendered_html"])
            search_index.append(search_entry)
        search_index_file = output / "search-index.json"
        search_index_file.write_text(json.dumps(search_index))

    # Generate tag index pages if enabled
    if config.theme.tag_index:
        tags = collect_tags(pages)
        if tags:
            tag_layout = resolve_layout({}, config.theme.default_layout)
            build_tag_pages(
                tags, env, site_config, output, clean_urls, base_path, tag_layout
            )

    # Generate sitemap if base_url is configured
    if config.site.base_url:
        sitemap_xml = build_sitemap(
            pages, rendered_folder_indexes, config.site.base_url, clean_urls
        )
        (output / "sitemap.xml").write_text(sitemap_xml)

    # Generate Atom feed if base_url is configured and feed enabled
    if config.site.base_url and config.feed.enabled:
        feed_pages = pages
        if config.feed.collections:
            feed_pages = [
                entry
                for col_name in config.feed.collections
                if col_name in collections
                for entry in collections[col_name].entries
                if isinstance(entry, Page)
            ]
        feed_xml = build_atom_feed(
            feed_pages,
            config.site.title,
            config.site.description,
            config.site.base_url,
            clean_urls,
            base_path,
            config.feed.path,
            config.feed.limit,
            config.feed.author,
            config.feed.include_paths or None,
        )
        feed_path = config.feed.path.lstrip("/")
        feed_file = output / feed_path
        feed_file.parent.mkdir(parents=True, exist_ok=True)
        feed_file.write_text(feed_xml)

    # Generate llms.txt if base_url is configured and llms_txt enabled
    if config.site.base_url and config.llms_txt.enabled:
        full_url = (
            f"{config.site.base_url}{base_path}/llms-full.txt"
            if config.llms_txt.full
            else ""
        )
        llms_txt_content = build_llms_txt(
            pages,
            rendered_folder_indexes,
            collections,
            config.site.base_url,
            config.site.title,
            config.llms_txt.description,
            clean_urls,
            base_path,
            config.nav.links,
            full_url,
        )
        (output / "llms.txt").write_text(llms_txt_content)

        if config.llms_txt.full:
            llms_full_content = build_llms_full_txt(
                pages,
                rendered_folder_indexes,
                collections,
                config.site.base_url,
                config.site.title,
                config.llms_txt.description,
                clean_urls,
                base_path,
                config.nav.links,
            )
            (output / "llms-full.txt").write_text(llms_full_content)

    # Generate 404 page
    not_found_template = env.get_template("404.html")
    not_found_layout = resolve_layout({}, config.theme.default_layout)
    (output / "404.html").write_text(
        not_found_template.render(site=site_config, layout_template=not_found_layout)
    )

    copy_user_static_files(site_root, output)

    run_hooks(config.hooks.post_build, "post_build", cwd=site_root, env_vars=hook_env)

    return BuildResult(
        page_count=count,
        broken_links=broken_links_by_page,
        duration_seconds=time.perf_counter() - _start,
    )


def _build_folder_breadcrumbs(folder, pages, nav_config, clean_urls=True, base_path=""):
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
    root_path = get_folder_url("", clean_urls, base_path)
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
        folder_url = get_folder_url(path, clean_urls, base_path)
        breadcrumbs.append(Breadcrumb(label=label, path=folder_url))

    return breadcrumbs
