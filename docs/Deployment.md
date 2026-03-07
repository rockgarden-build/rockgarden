---
tags: [deployment, build]
---

# Deployment

Rockgarden builds a static site into a single output directory (default: `_site/`). Any static hosting provider can serve it.

## 404 Pages

Rockgarden always generates a `404.html` in the output root. Most hosts auto-detect this file — no extra config needed for Netlify, Vercel, or GitHub Pages.

You can override the default page by placing a `404.html` in your site's `_templates/` directory.

### Provider-specific notes

**Netlify** — `404.html` in the publish directory is detected automatically. No config required.

**Vercel** — `404.html` in the output directory is detected automatically. If you use clean URLs (`cleanUrls = true` in `rockgarden.toml`), add a `vercel.json` to enable server-side clean URL handling:

```json
{
  "cleanUrls": true
}
```

**GitHub Pages** — `404.html` in the repository root (or `docs/` folder if configured) is detected automatically.

**Apache** — Add to `.htaccess` in your document root:

```apache
ErrorDocument 404 /404.html
```

**Nginx** — Add to your server block:

```nginx
error_page 404 /404.html;
```

## Subdirectory Deployment

To deploy to a subdirectory (e.g., `example.com/docs/`), set `base_url` in `rockgarden.toml`:

```toml
[site]
base_url = "https://example.com/docs"
```

All generated URLs (internal links, media embeds, search index, sitemap) will include the base path prefix.

## Clean URLs

By default, Rockgarden generates clean URLs (e.g., `/about/` rather than `/about.html`). Each page is written as `page/index.html`. This works on most hosts without configuration.

To disable clean URLs, set in `rockgarden.toml`:

```toml
[site]
clean_urls = false
```

## Dev Server

The built-in `rgdn serve` command is a simple development preview server. It does not simulate 404 behavior — visit `/404.html` directly to preview the error page during development.
