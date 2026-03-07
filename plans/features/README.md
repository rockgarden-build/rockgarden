# Features

Implementation roadmap for rockgarden. See individual feature docs for details.

## Test Vaults

Using two Obsidian vaults with Quartz as reference implementations:
- `nat1-club/freemenswood/` - D&D campaign wiki
- `nat1-club/never-sunny/` - D&D campaign wiki

Both use Quartz-style `content/` folder structure.

## Benchmark

The [PyOhio static website](https://github.com/pyohio/static-website) (Astro + Python) serves as the benchmark for general-purpose SSG capability. See the gap analysis in the plan file for details.

## Feature List

| # | Feature | Status | Phase | Doc |
|---|---------|--------|-------|-----|
| 01 | [Home Page](01-home-page.md) | ✅ | — | Render single index.md to HTML |
| 02 | [All Pages](02-all-pages.md) | ✅ | — | Render all markdown files |
| 03 | [Wiki-Links](03-wiki-links.md) | ✅ | — | Resolve `[[Name]]` to URLs |
| 04 | [Embeds](04-embeds.md) | ✅ | — | Image/audio/video/PDF embeds, note transclusions |
| 05 | [Callouts](05-callouts.md) | ✅ | A | GFM alerts + Obsidian callouts |
| 06 | [Navigation](06-navigation.md) | ✅ | — | Sidebar, breadcrumbs, folder pages |
| 07 | [Backlinks](07-backlinks.md) | ✅ | A | Pages that link to current page |
| 08 | [Search](08-search.md) | ✅ | A | Client-side search |
| 09 | [Macros](09-macros.md) | ✅ | C | User-defined Jinja2 macros |
| 10 | [Progressive Customization](10-progressive-customization.md) | ✅ | B | Config separation, layout system, theme export |
| 11 | [RSS Feed](11-rss-feed.md) | ✅ | C | Atom feed generation |
| 12 | [Base Path Prefix](12-base-path-prefix.md) | ✅ | B | Deploy to subdirectories |
| 13 | [Polish](13-polish.md) | ✅ | A | Sitemap, 404, TOC, build info, timing |
| 14 | [Collections](14-collections.md) | ✅ | B | Unified content model, progressive collections |
| 15 | [Build Hooks](15-build-hooks.md) | ✅ | B | Pre/post-build shell commands |
| 16 | [Static Assets](16-static-assets.md) | ✅ | B | Custom CSS & JS inclusion |
| 17 | [SEO & Meta Tags](17-seo-meta.md) | ✅ | B | Frontmatter-driven meta, OG tags |
| 18 | [Accessibility](18-accessibility.md) | ✅ | A | Skip links, ARIA, focus styles |
| N6 | Broken Link Handling | ✅ | A | Visual indication + build warnings |
| N7 | Tag Display | ✅ | A | Show frontmatter tags on pages |
| N8 | [Tag Index Pages](N8-tag-index-pages.md) | ✅ | B | Generate `/tags/<tag>/` listing pages |
| N9 | Template Decomposition | ✅ | A | Named blocks as customization hooks in page templates |
| N10 | Newline Handling | ✅ | A | Obsidian-style single newline → `<br>` |
| N11 | [Config Validation](N11-config-validation.md) | ✅ | B | `validate` command, unknown-key warnings, theme manifest |

## Roadmap Phases

- **Phase A — Zero-Config Release** ✅: Callouts (05), backlinks (07), broken link handling (N6), polish (13), accessibility (18), search (08), tag display (N7), template decomposition (N9), newline handling (N10), embeds incl. transclusions (04)
- **Phase B — General SSG / PyOhio** ✅: Layout system (10B), static assets (16), theme export CLI (10C), collections (14), build hooks (15), base path (12), SEO (17), tag index pages (N8)
- **Phase C — Enhanced Features**: Macros (09), RSS (11)

## Quartz Features Reference

From test vaults' Quartz configs:

**Core:**
- [x] Frontmatter parsing
- [x] Wiki-links with name-based resolution
- [x] Section links (`[[Page#Section]]`)
- [x] Media file links (`[[image.png]]`)
- [x] Image embeds (with alt text, sizing)
- [x] Audio/video embeds
- [x] Note transclusions
- [x] Callouts
- [x] Table of contents
- [x] Backlinks
- [ ] Graph visualization
- [x] Search (index generation + client-side UI)
- [x] Modified date display on pages

**Output:**
- [x] Content pages
- [x] Folder pages
- [x] Tag pages
- [x] Sitemap
- [x] RSS feed

**Customizations found:**
- [ ] `BeyondLink` component (frontmatter-driven D&D Beyond links)
- [x] Build info in footer (timestamp, git commit)
- [x] Ignore patterns (private, templates, .obsidian)
