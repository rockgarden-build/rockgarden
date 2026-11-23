# Roadmap to 1.0

1.0 means a stable public contract. Before freezing it, get rockgarden to a generally usable, feature-complete state, publicize it, and collect feedback from new users. Breaking changes are acceptable until the contract phase.

## Phase 1: Feature completeness

Goal: the feature set a new user would expect from an Obsidian-friendly SSG.

- [ ] **Social links + brand icons**: configurable social/external links with icons in nav or footer. Needs a brand icon library alongside Lucide (see `issues.md`).
- [ ] **Hover previews**: popover preview of a linked page on hover. See `features/hover-previews.md`.
- [ ] **Graph view**: interactive graph of page links. See `features/graph-view.md`.
- [ ] **Block references**: `[[page#^block]]` links and `![[page#^block]]` embeds. See `features/block-references.md`.
- [ ] **Plugin design**: write the spec in `features/plugins.md` and resolve its open questions. Implementation is post-1.0; the design informs which APIs the contract phase freezes.

## Phase 2: Launch readiness

Goal: a new user can evaluate rockgarden without help.

- [ ] **Demo site**: rename `site/` to `demo/`, expand to cover all features, deploy separately. See `features/demo-site.md`.
- [ ] **Alternate bundled theme**: a more modern style alongside the default docs/wiki theme; the demo shows both. See `features/alternate-theme.md`.
- [ ] **Docs pass**: Getting Started, Customization, and Configuration reflect current behavior; screenshots or demo links where useful.
- [ ] **README**: feature overview pointing to the demo and docs.
- [ ] **Unified logging/output**: consistent CLI output with verbosity control, replacing ad hoc `typer.echo` calls.
- [ ] **Publicize** and collect feedback.

## Phase 3: Stability contract

Goal: define, document, and freeze the public surface. Changes to it after 1.0 require a major version.

- [ ] **Feedback triage**: fold launch feedback into the contract before freezing.
- [ ] **Config validation**: warn or error on unknown `rockgarden.toml` keys (currently silently ignored).
- [ ] **Hardcoded names**: decide configurable or permanently fixed:
  - `/tags/` URL prefix
  - Reserved directories (`_templates/`, `_themes/`, `_styles/`, `_scripts/`), plus reserving `_plugins/`
- [ ] **Theme API**: document the full template context, named blocks, component names, and `theme.toml` manifest format.
- [ ] **Build hooks**: document stages and environment variables; add a version field to `content.json`.
- [ ] **CLI**: review commands and flags for consistency.
- [ ] **Policy doc**: what is public (CLI, config, frontmatter, theme API, hooks, output URLs) vs internal (Python modules), and how deprecations work.
- [ ] **Upgrade guide** from 0.x.
- [ ] **Release**: change PyPI classifier from Alpha to Production/Stable; tag 1.0.

## Post-1.0

Everything in `ideas.md`, plus plugin implementation.
