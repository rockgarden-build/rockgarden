# Feature 02: All Pages ✅

Render all markdown files in the source directory, preserving folder structure in output.

## Goal

```
uv run rockgarden build
```

Converts all `.md` files to HTML, maintaining directory hierarchy.

## Implementation

- Recursive discovery of `.md` files via `source.rglob("*.md")`
- Ignore patterns applied during discovery (`.obsidian`, `private`, `templates`)
- Slug generation from file path (spaces/underscores → dashes, lowercase)
- Output path mirrors source structure with `.html` extension

## Key Files

- `content/loader.py` - `load_content()` discovers and parses all markdown files
- `urls.py` - `generate_slug()`, `get_output_path()` handle path transformations
- `output/builder.py` - Iterates all pages and writes HTML files

## Configuration

```toml
[build]
ignore_patterns = [".obsidian", "private", "templates", "Templates"]
```

## Clean URLs

When `clean_urls = true` (default):
- `docs/getting-started.md` → `docs/getting-started/index.html` (served as `/docs/getting-started/`)

When `clean_urls = false`:
- `docs/getting-started.md` → `docs/getting-started.html`
