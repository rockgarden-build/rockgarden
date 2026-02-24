# Nits

Things to revisit before release.

- **Date field defaults**: Research commonly used frontmatter field names for modified/created dates across Obsidian plugins and other SSGs. Current defaults (`modified`, `updated`, `last_modified` / `created`, `date`, `date_created`) are guesses — validate against real-world usage before shipping.
- **Config namespacing**: As the number of config options grows, consider better sections or namespacing in `rockgarden.toml`. Currently options like `show_build_info` and `show_build_commit` sit under `[build]` but could warrant their own section.