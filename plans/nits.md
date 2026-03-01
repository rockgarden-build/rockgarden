# Nits

Things to revisit before release.

- **Date field defaults**: Research commonly used frontmatter field names for modified/created dates across Obsidian plugins and other SSGs. Current defaults (`modified`, `updated`, `last_modified` / `created`, `date`, `date_created`) are guesses — validate against real-world usage before shipping.
- **Config namespacing**: As the number of config options grows, consider better sections or namespacing in `rockgarden.toml`. Currently options like `show_build_info` and `show_build_commit` sit under `[build]` but could warrant their own section.
- **User asset subdirectory support**: `discover_user_assets` in `builder.py` only discovers files directly in `_styles/` and `_scripts/` (no glob for subdirectories). May want to support nested dirs (e.g. `_scripts/vendor/`) before release.
- **Media resolver base_path gap**: `create_media_resolver` in `assets.py` hardcodes `"/" + actual_path` for `src_url` (lines 113, 120, 129). Obsidian-style media embeds (`![[image.png]]`) will have broken `src` attributes on sites deployed to a subpath `base_url`. Needs `base_path` threaded into the resolver the same way `clean_urls` was.