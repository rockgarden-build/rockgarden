# Features

Implementation roadmap for rockgarden. See individual feature docs for details.

## Test Vaults

Using two Obsidian vaults with Quartz as reference implementations:
- `nat1-club/freemenswood/` - D&D campaign wiki
- `nat1-club/never-sunny/` - D&D campaign wiki

Both use Quartz-style `content/` folder structure.

## Feature List

| # | Feature | Status | Doc |
|---|---------|--------|-----|
| 01 | [Home Page](01-home-page.md) | ✅ | Render single index.md to HTML |
| 02 | [All Pages](02-all-pages.md) | ✅ | Render all markdown files |
| 03 | [Wiki-Links](03-wiki-links.md) | ✅ | Resolve `[[Name]]` to URLs |
| 04 | [Embeds](04-embeds.md) | Partial | Image embeds ✅, transclusions ❌ |
| 05 | [Callouts](05-callouts.md) | ❌ | Obsidian callout syntax |
| 06 | [Navigation](06-navigation.md) | ✅ | Sidebar, breadcrumbs, folder pages |
| 07 | [Backlinks](07-backlinks.md) | ❌ | Pages that link to current page |
| 08 | [Search](08-search.md) | ❌ | Client-side search |
| 09 | [Macros](09-macros.md) | ❌ | User-defined Jinja2 macros |
| 10 | [Progressive Customization](10-progressive-customization.md) | In Progress | Themes and layouts |
| 11 | [RSS Feed](11-rss-feed.md) | ❌ | RSS/Atom feed generation |
| 12 | [Base Path Prefix](12-base-path-prefix.md) | ❌ | Deploy to subdirectories |
| 13 | [Polish](13-polish.md) | ❌ | Dark mode, responsive, sitemap |

## Quartz Features Reference

From test vaults' Quartz configs:

**Core:**
- [x] Frontmatter parsing
- [x] Wiki-links with name-based resolution
- [x] Image embeds (with alt text, sizing)
- [ ] Audio embeds
- [ ] Note transclusions
- [ ] Callouts
- [ ] Table of contents
- [ ] Backlinks
- [ ] Graph visualization
- [ ] Search

**Output:**
- [x] Content pages
- [x] Folder pages
- [ ] Tag pages
- [ ] Sitemap
- [ ] RSS feed

**Customizations found:**
- [ ] `BeyondLink` component (frontmatter-driven D&D Beyond links)
- [ ] Build info in footer (timestamp, git commit)
- [x] Ignore patterns (private, templates, .obsidian)
