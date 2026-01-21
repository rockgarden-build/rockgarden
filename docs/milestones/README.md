# Milestones

Implementation roadmap for rockgarden. Each milestone builds on the previous.

## Test Vaults

Using two Obsidian vaults with Quartz as reference implementations:
- `nat1-club/freemenswood/` - D&D campaign wiki
- `nat1-club/never-sunny/` - D&D campaign wiki

Both use Quartz-style `content/` folder structure.

## Roadmap

### Milestone 1: Home Page ✅
Render single `index.md` to HTML. Basic markdown, no link resolution.

### Milestone 2: All Pages ✅
Render all markdown files. Folder structure preserved in output.

### Milestone 3: Wiki-Links ✅
Resolve `[[Name]]` and `[[Name|Alias]]` to actual page URLs.

### Milestone 4: Embeds
Support `![[image.jpg]]` and `![[file.md]]` embeds.

### Milestone 5: Callouts
Convert Obsidian callout syntax to styled HTML.

### Milestone 6: Navigation ✅
Sidebar explorer, breadcrumbs, folder pages. See [06-navigation.md](06-navigation.md).

### Milestone 7: Backlinks
Track and display pages that link to each page.

### Milestone 8: Search
Client-side search with JSON index.

### Milestone 9: Macros
User-defined Jinja2 macros in `_macros/` directory.

### Milestone 10: Themes
Full theme support - override single templates or replace entire template set.

### Milestone 11: RSS Feed
Generate RSS/Atom feed for content updates.

### Milestone 12: Base Path Prefix
Support deploying to subdirectories (e.g., `example.com/docs/`) via `base_url` config.

### Milestone 13: Polish
Dark mode, responsive design, sitemap.

## Quartz Features to Support

From the test vaults' Quartz configs:

**Core:**
- [x] Frontmatter parsing
- [x] Wiki-links with name-based resolution
- [ ] Image/audio embeds
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
