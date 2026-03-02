---
tags: [hooks, configuration]
---

# Build Hooks

Shell commands executed at build lifecycle stages. Hooks keep the core unopinionated while enabling custom processing like data fetching, asset generation, and CSS compilation.

## Configuration

```toml
[hooks]
pre_build = [
    "python scripts/fetch_data.py",
]
post_collect = [
    "python scripts/generate_og_images.py",
]
post_build = [
    "npx tailwindcss -i input.css -o _site/css/styles.css --minify",
]
```

Commands run sequentially within each stage. The build aborts if any command exits non-zero.

## Stages

| Stage | When | Content JSON Available | Typical Use |
|-------|------|------------------------|-------------|
| `pre_build` | Before content loading | No | Data fetching, file generation |
| `post_collect` | After content collected, before rendering | Yes | Derived assets (OG images), data transforms |
| `post_build` | After all output written | Yes | CSS/JS compilation, image optimization, validation |

## Content JSON Export

When `post_collect` or `post_build` hooks are configured, rockgarden exports page metadata to `.rockgarden/content.json` after content collection. Hook scripts can read this file to generate derived assets.

The JSON contains an array of objects, one per page:

```json
[
  {
    "slug": "notes/hello",
    "title": "Hello World",
    "url": "/notes/hello/",
    "tags": ["demo"],
    "frontmatter": { "title": "Hello World", "tags": ["demo"] },
    "modified": "2026-01-15T12:00:00",
    "created": null,
    "source_path": "content/notes/hello.md"
  }
]
```

## Environment Variables

Hooks receive these environment variables:

| Variable | Description |
|----------|-------------|
| `ROCKGARDEN_SOURCE` | Absolute path to the source content directory |
| `ROCKGARDEN_OUTPUT` | Absolute path to the output directory |
| `ROCKGARDEN_CONTENT_JSON` | Absolute path to `.rockgarden/content.json` (only set for `post_collect` and `post_build`) |

## Working Directory

All hooks run with `cwd` set to the site root (where `rockgarden.toml` lives).

## Examples

### Compile Tailwind CSS after build

```toml
[hooks]
post_build = [
    "npx tailwindcss -i _styles/input.css -o _site/styles/output.css --minify",
]
```

### Fetch external data before build

```toml
[hooks]
pre_build = [
    "python scripts/fetch_schedule.py",
]
```

The script writes data files into the source directory before content is loaded.

### Generate Open Graph images from content metadata

```toml
[hooks]
post_collect = [
    "python scripts/generate_og_images.py",
]
```

The script reads `.rockgarden/content.json` to get page titles and metadata, then generates image files into the output directory.

## Gitignore

The `.rockgarden/` directory should be added to `.gitignore`. Running `rockgarden init` does this automatically. If hooks are added to an existing project, a warning is printed during build if `.rockgarden/` is not ignored.
