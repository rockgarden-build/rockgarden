---
tags: [configuration, reference]
---

# Configuration

Rockgarden follows a progressive customization model: sensible conventions are the defaults, and everything is configurable. A site with zero configuration works out of the box. Add options as your needs grow.

Configuration lives in `rockgarden.toml` at the site root.

## `[site]`

| Field         | Type   | Default     | Description                                                                                                                |
| ------------- | ------ | ----------- | -------------------------------------------------------------------------------------------------------------------------- |
| `title`       | `str`  | `"My Site"` | Site name, used in `<title>` tags and branding                                                                             |
| `description` | `str`  | `""`        | Default meta description (overridden per-page via frontmatter)                                                             |
| `og_image`    | `str`  | `""`        | Default Open Graph image URL (overridden per-page via frontmatter)                                                         |
| `source`      | `path` | `"."`       | Source directory containing content files                                                                                  |
| `output`      | `path` | `"_site"`   | Output directory for built site                                                                                            |
| `clean_urls`  | `bool` | `true`      | Generate `/page/index.html` instead of `/page.html`                                                                        |
| `base_url`    | `str`  | `""`        | Full base URL (e.g. `https://example.com/docs`). Used for feeds, sitemap, and deriving `base_path` when not set explicitly. Trailing slash is stripped automatically. |
| `base_path`   | `str`  | `""`        | URL path prefix for subdirectory deploys (e.g. `/docs`). When set, all generated URLs are prefixed with this path. If not set, derived from `base_url`. Trailing slash is stripped automatically. |

## `[build]`

| Field             | Type           | Default                                                          | Description                                                                |
| ----------------- | -------------- | ---------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `ignore_patterns` | `list[str]`    | `[".obsidian", "private", "templates", "Templates", "_static"]`  | Paths to exclude from content loading                                      |
| `icons_dir`       | `path \| null` | `null`                                                           | Directory containing custom icon SVGs. Falls back to bundled Lucide icons. |
| `assets_dir`      | `str`          | `"_assets"`                                                      | Output subdirectory for bundled CSS and JS assets.                         |
| `inline_icons`    | `bool`         | `true`                                                           | Enable `:lucide-name:` icon syntax in markdown content.                    |

## `[theme]`

Theme-specific display and rendering options. These are supported by the default theme. Custom themes may support different options.

| Field               | Type        | Default       | Description                                                                                                                                                             |
| ------------------- | ----------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`              | `str`       | `""`          | Theme directory name under `_themes/`. Empty = bundled default theme.                                                                                                   |
| `default_layout`    | `str`       | `""`          | Default layout template for pages (e.g. `"wide"`). Resolved to `layouts/<value>.html`. Per-page `layout` frontmatter overrides this. Falls back to `layouts/default.html`. |
| `toc`               | `bool`      | `true`        | Show table of contents panel                                                                                                                                            |
| `backlinks`         | `bool`      | `true`        | Show backlinks panel                                                                                                                                                    |
| `search`            | `bool`      | `true`        | Enable search UI and index generation                                                                                                                                   |
| `tag_index`         | `bool`      | `true`        | Generate `/tags/` index pages                                                                                                                                           |
| `daisyui_default`   | `str`       | `"light"`     | Default DaisyUI color theme (default theme only)                                                                                                                        |
| `daisyui_themes`    | `list[str]` | `[]`          | Available themes for the theme switcher. Empty = light/dark toggle. (default theme only)                                                                                |
| `nav_default_state` | `str`       | `"collapsed"` | Sidebar nav state: `"collapsed"` or `"expanded"` (default theme only)                                                                                                   |
| `show_build_info`   | `bool`      | `true`        | Show build timestamp in footer (default theme only)                                                                                                                     |
| `show_build_commit` | `bool`      | `false`       | Show git commit in footer (default theme only)                                                                                                                          |

## `[nav]`

| Field             | Type        | Default         | Description                                                         |
| ----------------- | ----------- | --------------- | ------------------------------------------------------------------- |
| `hide`            | `list[str]` | `[]`            | Paths to hide from sidebar navigation                               |
| `labels`          | `dict`      | `{}`            | Custom labels for paths (e.g. `{"/api" = "API Reference"}`)         |
| `sort`            | `str`       | `"files-first"` | Sort order: `"files-first"`, `"folders-first"`, or `"alphabetical"` |
| `link_auto_index` | `bool`      | `false`         | Make folders with `index.md` clickable links in nav                 |
| `links`           | `list`      | `[]`            | Custom navigation links. Each entry has `label`, `url`, and optional `children` (same structure, nested) |
| `links_position`  | `str`       | `"after"`       | Where to place custom links relative to directory nav: `"before"` or `"after"` |

## `[feed]`

Atom feed generation. Requires `site.base_url` to be set.

| Field           | Type        | Default        | Description                                                              |
| --------------- | ----------- | -------------- | ------------------------------------------------------------------------ |
| `enabled`       | `bool`      | `false`        | Enable Atom feed generation                                              |
| `path`          | `str`       | `"/feed.xml"`  | Output path for the feed file                                            |
| `limit`         | `int`       | `20`           | Maximum number of entries in the feed                                    |
| `author`        | `str`       | `""`           | Feed author name                                                         |
| `include_paths` | `list[str]` | `[]`           | Limit feed to pages under these paths. Empty = all pages.                |
| `collections`   | `list[str]` | `[]`           | Include entries from these collections in the feed                       |

## `[toc]`

| Field       | Type  | Default | Description                            |
| ----------- | ----- | ------- | -------------------------------------- |
| `max_depth` | `int` | `4`     | Maximum heading depth to include (1–6) |

## `[search]`

| Field             | Type   | Default | Description                                                                                      |
| ----------------- | ------ | ------- | ------------------------------------------------------------------------------------------------ |
| `include_content` | `bool` | `true`  | Include full page body in search index. When `false`, only title, slug, and tags are searchable. |

## `[dates]`

| Field                    | Type        | Default                                    | Description                                                          |
| ------------------------ | ----------- | ------------------------------------------ | -------------------------------------------------------------------- |
| `modified_date_fields`   | `list[str]` | `["modified", "updated", "last_modified"]` | Frontmatter fields to check for modification date (first match wins) |
| `created_date_fields`    | `list[str]` | `["created", "date", "date_created"]`      | Frontmatter fields to check for creation date (first match wins)     |
| `modified_date_fallback` | `bool`      | `false`                                    | Use file modification time when no frontmatter date field matches    |
| `timezone`               | `str`       | `"UTC"`                                    | IANA timezone for date display (e.g. `"US/Eastern"`)                 |

## `[hooks]`

Shell commands executed at build lifecycle stages. Commands run sequentially; any non-zero exit aborts the build.

| Field          | Type        | Default | Description                                    |
| -------------- | ----------- | ------- | ---------------------------------------------- |
| `pre_build`    | `list[str]` | `[]`    | Run before content loading                     |
| `post_collect` | `list[str]` | `[]`    | Run after content collection, before rendering |
| `post_build`   | `list[str]` | `[]`    | Run after all output is written                |

See [[Build Hooks]] for environment variables, content JSON export, and examples.

## `[[collections]]`

Repeatable section. Each defines a named content collection with its own namespace.

| Field         | Required | Type   | Default | Description                                                                                                   |
| ------------- | -------- | ------ | ------- | ------------------------------------------------------------------------------------------------------------- |
| `name`        | yes      | `str`  | —       | Collection identifier                                                                                         |
| `source`      | yes      | `str`  | —       | Directory containing collection files (relative to source root)                                               |
| `template`    | no       | `str`  | `null`  | Template for rendering each entry. Required if `pages = true`.                                                |
| `url_pattern` | no       | `str`  | `null`  | URL pattern with `{field}` placeholders (e.g. `/speakers/{slug}/`). Required if `pages = true`.               |
| `pages`       | no       | `bool` | `true`  | Generate HTML pages per entry. Set `false` for data-only collections.                                         |
| `nav`         | no       | `bool` | `false` | Add collection pages to sidebar navigation                                                                    |
| `model`       | no       | `str`  | `null`  | Pydantic model name for validation. Resolved from `_models/<name>.py` or `_themes/<theme>/_models/<name>.py`. |

Supported file formats: `.md`, `.yaml`, `.yml`, `.json`, `.toml`

Collections are available in templates as `collections.<name>`.

## Frontmatter Fields

Per-page options set in YAML frontmatter:

| Field         | Type            | Description                                                               |
| ------------- | --------------- | ------------------------------------------------------------------------- |
| `title`       | `str`           | Page title (used in `<title>`, nav, heading)                              |
| `description` | `str`           | Page-specific meta description (overrides site default)                   |
| `og_image`    | `str`           | Page-specific Open Graph image (overrides site default)                   |
| `keywords`    | `str` or `list` | Meta keywords                                                             |
| `slug`        | `str`           | Override auto-generated URL slug                                          |
| `nav_order`   | `int`           | Pin position in navigation (lower = higher)                               |
| `tags`        | `list[str]`     | Content tags, used for tag index pages                                    |
| `layout`      | `str`           | Layout template name (e.g. `"talk"` → `layouts/talk.html`)                |
| `show_index`  | `bool`          | For `index.md` files: render page content + auto-generated folder listing |

## CLI Overrides

Command-line flags override config file values:

```bash
rockgarden build --source ./vault --output ./dist
rockgarden build --config ./custom.toml
rockgarden build --clean
rockgarden serve --output ./dist --port 3000
```

## Convention Directories

These directories are discovered by convention at the site root:

| Directory         | Purpose                                                    |
| ----------------- | ---------------------------------------------------------- |
| `_templates/`     | Template overrides (highest priority in ChoiceLoader)      |
| `_themes/<name>/` | Custom theme directory (active when `theme.name` is set)   |
| `_styles/`        | Custom CSS files (auto-injected as `<link>` tags)          |
| `_scripts/`       | Custom JavaScript files (auto-injected as `<script>` tags) |
| `_static/`        | Static files copied as-is to output root                   |
| `.rockgarden/`    | Build cache and content JSON export (add to `.gitignore`)  |
