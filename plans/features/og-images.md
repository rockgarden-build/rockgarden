# OG Image Generation — Options & Recommendation

## Status: Future Feature (Phase C or later)

## Context

Feature 17 (SEO & Meta Tags) is complete. The `og_image` frontmatter field and `site.og_image` config fallback are wired into `templates/components/meta.html`. Currently the field expects a **pre-existing image path** — users must provide OG images manually.

The goal is to **generate OG images automatically at build time** from page data (title, description, tags, etc.), so every page gets a social card without manual effort.

This feature depends on build hooks (Feature 15, Phase B Batch 4) being implemented first.

---

## Key Architectural Context

- Page data available for generation: `page.title`, `page.frontmatter.get("description")`, `page.frontmatter.get("tags")`, `page.slug`, `page.modified`
- `og_image` frontmatter field already consumed by `meta.html` — populating it before rendering means it just works
- The planned `post_collect` build hook stage (Feature 15) is explicitly designed for this use case: content is collected and exported to `.rockgarden/content.json`, hook scripts run before HTML rendering
- Node.js is already a project dependency (Tailwind CLI)
- Relevant files: `src/rockgarden/output/builder.py`, `src/rockgarden/config.py`, `src/rockgarden/content/models.py`, `src/rockgarden/templates/components/meta.html`

---

## Options

### Option A: Pillow (pure Python, built-in)

Render title + description onto a background image using Pillow's text drawing API.

- **Pros**: Zero extra deps (or Pillow as an optional dep), pure Python, fast, CI-friendly
- **Cons**: Low-level layout — wrapping long titles, centering, multi-line text require manual math. Hard to make look polished.
- **Best for**: Simple, consistent cards (title + site name on a branded background)
- Pillow is not currently a dependency — would need to be added as optional

### Option B: SVG template → CairoSVG

User provides a Jinja2 SVG template with `{{ page.title }}` etc. Python renders it and converts to PNG via CairoSVG.

- **Pros**: SVG handles layout/design — designers can work in Inkscape/Figma. Text wrapping is natural. Good quality output.
- **Cons**: Requires Cairo system library (`brew install cairo` / `apt install libcairo2`) — cross-platform friction.
- **Best for**: Sites where the design matters and users are comfortable with SVG

### Option C: Satori + Node subprocess (best quality)

Vercel's approach: render HTML/CSS to SVG via Satori (pure JS, no browser), convert SVG → PNG via resvg-js. rockgarden would ship a small Node script.

```bash
node scripts/generate_og.js --content .rockgarden/content.json --output _site/og/
```

- **Pros**: Highest quality output (flexbox layout), fast (milliseconds per image), headless/CI-friendly. Node.js already present for Tailwind.
- **Cons**: Adds JS complexity to what is otherwise a Python tool; users need `npm install`.
- **Best for**: Sites needing polished, design-forward cards (e.g. PyOhio)

### Option D: Post-collect hook pattern (most flexible, no built-in)

Implement build hooks (Feature 15) and document the pattern. rockgarden exports `.rockgarden/content.json`; users write their own generation script.

```toml
[hooks]
post_collect = ["python scripts/generate_og_images.py"]
```

- **Pros**: Maximum flexibility — users choose any library. No new core deps.
- **Cons**: Not "batteries included."
- **Best for**: Power users and complex sites already running a build pipeline

---

## Recommendation

**Two-tier approach:**

1. **Phase B (with hooks)**: Implement build hooks (Feature 15). Document the `post_collect` hook pattern for OG image generation. Provide example scripts — one Pillow-based (simple), one Satori-based (polished). Unblocks PyOhio and advanced users immediately with no new core deps.

2. **Phase C (built-in)**: Add an opt-in built-in generator using **SVG template → CairoSVG**:
   ```toml
   [og_images]
   enabled = true
   template = "_themes/mysite/og-template.svg"
   output_dir = "og"   # written to _site/og/<slug>.png
   ```
   SVG is preferred over Pillow because layout and design are far easier to express there.

---

## Integration Point

```
load_content()
  → export .rockgarden/content.json
  → [post_collect hook OR built-in og_images step]
      → write _site/og/<slug>.png per page
      → update page.frontmatter["og_image"] = "/og/<slug>/"
  → render_page() → meta.html picks up og_image automatically
```

No changes to `meta.html` needed — it already conditionally renders `og:image`.

---

## Dependencies

| Approach | New Python dep | New system dep | New Node dep |
|---|---|---|---|
| Pillow | `pillow` (optional) | None | None |
| CairoSVG | `cairosvg` (optional) | `libcairo2` | None |
| Satori | None | None | `satori`, `@resvg/resvg-js` |
| Hook pattern | None | None | None |
