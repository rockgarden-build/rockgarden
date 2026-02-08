# Future Ideas

Noted but not currently planned:

- **ASCII-only slugs**: Strip Unicode/accents from URLs (e.g., "Orontinórë" → "orotinore"). See research below.
- Incremental builds / watch-mode selective rebuild (file-mtime dirty checking, partial rebuilds)
- Backlinks position customization (bottom vs sidebar) - currently right sidebar only, may add config for position later or leave to custom templates
- Hover previews (popover preview of linked page on hover)
- CLI model discovery wizard
- Config drift detection
- MCP server for vault data (JSON content export makes this feasible)
- Graph visualization
- Installable templates
- Python plugins (see [concepts.md](concepts.md) for the plugin model)
- Configurable markdown preset (commonmark, gfm-like, custom plugins)

Moved to roadmap:
- ~~Content from other data sources~~ → Feature 14 (Collections) + Feature 15 (Build Hooks)

---

## ASCII-only Slugs Research

**Problem**: Unicode in URLs causes encoding issues, server compatibility problems, and SEO challenges.
- Current: "Groups/Orontinórë.md" → `/groups/orontinórë/` → percent-encoded as `/groups/orontinor%C3%AB/`
- Desired: "Groups/Orontinórë.md" → `/groups/orotinore/`

**Approaches tested**:

1. **Strip accents (NFD normalization)** - Recommended ✓
   - No dependencies, works for European languages
   - "Orontinórë" → "Orontinore", "Café" → "Cafe"
   - Doesn't handle Cyrillic/CJK

2. **python-slugify library** - Full solution
   - Comprehensive transliteration including Cyrillic, Greek, CJK
   - "Москва" → "moskva", "日本" → "ri-ben"
   - Adds ~500KB dependency

3. **Comparison with other SSGs**:
   - Hugo: Full transliteration via go-unidecode
   - Jekyll: Strip accents only
   - Quartz: Similar to python-slugify

**Implementation location**: `src/rockgarden/urls.py` - `generate_slug()` function

**Breaking change**: URLs would change. Either:
- Add as config option (default: preserve current behavior)
- Just do it in v0.x (pre-1.0, breaking changes acceptable)

**Recommendation**: Implement NFD strip approach (no deps) with optional python-slugify for advanced cases.
