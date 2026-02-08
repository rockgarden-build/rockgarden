# Concepts

Core abstractions for customizing a rockgarden site.

## Project Layout

```
my-site/
├── rockgarden.toml
├── _templates/          # template overrides
├── _themes/<name>/      # complete theme packages
├── _plugins/<name>/     # behavioral extensions (future)
├── _macros/             # reusable Jinja2 snippets (planned — Feature 09)
├── _styles/             # custom CSS (planned — Feature 16)
├── _scripts/            # custom JS (planned — Feature 16)
└── content/
```

## Theme

A purely visual presentation layer: templates, styles, scripts, and theme-specific configuration. No behavioral code.

- Lives in `_themes/<name>/`
- The built-in theme is called **"default"** and ships with rockgarden
- Config section: `[theme]` — tweak settings (colors, layout options) without replacing the theme, or provide a complete custom theme with its own settings
- If a theme needs custom processing (e.g., SCSS compilation), it declares a plugin dependency rather than including behavioral code itself

Templates are resolved in this order (first match wins):

1. **Site templates** (`_templates/`) — override individual components
2. **Theme** (`_themes/<name>/`) — replace the full template set
3. **Built-in defaults** — ship with rockgarden

Status: partially implemented (DaisyUI theme selection, ChoiceLoader resolution).

## Plugin

A behavioral extension with Python integration. Project-local only — no global install, no marketplace.

- Lives in `_plugins/<name>/`
- Can register: build hooks, Jinja2 template filters, markdown-it-py extensions, CLI subcommands
- Installed by convention (copy/clone into project) or via CLI from a git URL or local directory

Plugins handle functionality that's too opinionated for the core. Example: OG/social preview image generation — different users want different tools and layouts for this, so it ships as a plugin rather than a built-in feature.

Status: future.

## Hook

A shell command or Python callable that runs at a build lifecycle stage.

| Stage | When | Use Cases |
|-------|------|-----------|
| `pre_build` | Before content loading | Data fetching, file generation |
| `post_collect` | After content collected, before render | OG images, data transforms |
| `post_build` | After all output written | Asset compilation, optimization |

Hooks can be declared directly in `rockgarden.toml` under `[hooks]`, or provided by a plugin.

Status: planned (Feature 15, Phase B).

## Macro

A reusable Jinja2 template snippet.

- Lives in `_macros/` as `.html` files
- Auto-loaded and available in templates as `macros.<filename>.<macro_name>()`
- Independent of themes and plugins — macros are project-level

Status: planned (Feature 09, Phase C).

## Relationships

Themes and plugins are **separate concepts in separate directories**. They don't nest inside each other.

- A theme can declare plugin dependencies (e.g., a theme that relies on an image optimization plugin)
- Plugins can provide their own templates (added to the template resolution chain)
- Hooks are a primitive: usable standalone via config, or provided by plugins
- Macros are project-level and independent of both themes and plugins

## Progressive Customization

Each level adds one layer of capability. See [Feature 10](features/10-progressive-customization.md) for implementation details.

| Level | What | How |
|-------|------|-----|
| 1 | Zero config | `rockgarden build` with built-in default theme |
| 2 | Theme settings | Tweak options via `[theme]` in config |
| 3 | Template overrides | Drop files in `_templates/` |
| 4 | Custom theme | Provide complete theme in `_themes/<name>/` |
| 5 | Plugins | Behavioral extensions in `_plugins/` |
| 6 | Full custom | Theme + plugins + hooks + macros |

## Installation Model

Rockgarden is installed at the user level via `uv tool`. All project-specific customization lives in the project directory.

- **Convention:** Copy or clone theme/plugin files into `_themes/` or `_plugins/`
- **CLI:** Install from a git URL or local directory (planned)
- No central registry or marketplace — themes and plugins are sourced directly
