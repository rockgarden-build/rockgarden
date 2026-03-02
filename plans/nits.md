# Nits

Things to revisit before release.

- **Date field defaults**: Research commonly used frontmatter field names for modified/created dates across Obsidian plugins and other SSGs. Current defaults (`modified`, `updated`, `last_modified` / `created`, `date`, `date_created`) are guesses — validate against real-world usage before shipping.
- **Config namespacing**: As the number of config options grows, consider better sections or namespacing in `rockgarden.toml`. Currently options like `show_build_info` and `show_build_commit` sit under `[build]` but could warrant their own section.
- **User asset subdirectory support**: `discover_user_assets` in `builder.py` only discovers files directly in `_styles/` and `_scripts/` (no glob for subdirectories). May want to support nested dirs (e.g. `_scripts/vendor/`) before release.
- **Unified logging / output**: Currently a mix of `print()`, `typer.echo()`, and `print(..., file=sys.stderr)` across CLI, builder, and hooks. Should introduce a consistent logging approach (stdlib `logging` or a thin wrapper) with verbosity control before 1.0. Would let hooks, build warnings, and CLI output all be controlled/redirected uniformly.
- **Theme config update is text-based**: `set_theme_name_in_config` in `theme.py` uses regex/text manipulation to update `rockgarden.toml` rather than a proper TOML writer (stdlib `tomllib` is read-only). Works for typical configs but could mangle unusual formatting. Swap for `tomlkit` or similar before 1.0.
- **Tag URL prefix configurable**: `/tags/` is hardcoded in `urls.py` and `tags.py`. Should be configurable (e.g. `[theme] tag_prefix = "tags"`) since a user could have a content page named "tags" that would conflict.
- **Convention directories configurable**: `_templates/`, `_themes/`, `_styles/`, `_scripts/` are hardcoded directory names. Should be configurable in case someone wants different names. Low priority.
- **Merge `./site` and `./docs`**: `./site` was an early example website; newer content moved to `./docs`. Merge the two so we can eventually serve a real website with examples once the project is released.
