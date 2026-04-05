# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Jekyll-based personal tech blog (tgparkk.github.io) covering C++, async/multi-threading, rendering, Windows development, game programming, and stock trading systems. Content is primarily in Korean.

## Commands

### Local Development
```bash
bundle install                    # Install dependencies
bundle exec jekyll serve          # Run local server at http://localhost:4000
bundle exec jekyll build          # Build site to _site/
```

### Deployment
Push to `main` branch - GitHub Pages auto-deploys.

## Blog Post Structure

Posts go in `_posts/` with filename format: `YYYY-MM-DD-title.md`

Required frontmatter:
```yaml
---
layout: post
title: "Post Title"
date: YYYY-MM-DD
categories: category-name
tags: [tag1, tag2]
excerpt: "Brief description"
comments: true
---
```

Available categories: `stock`, `cpp`, `windows`, `gamedev`, `rendering`, `async_servers`, `cooking`, `hobby`, `book`, `english`, `robotrader`, `trading-journal`, `machine-learning`, `blog-analysis`, `review`, `security`

## Architecture

- `_layouts/` - HTML templates (default.html, post.html, home.html, page.html)
- `_includes/` - Reusable HTML partials (header, footer, nav-drawer, navigation, like-button, toc-sidebar, curation-panel, next-read, series-banner, ad-unit, google-adsense)
- `_sass/` - SCSS source files (compiled with `style: compressed`)
- `categories/` - Category landing pages
- `assets/` - CSS, JS, images
- `research-materials/` - Collected notes, papers, articles for blog research
- `research-notes/` - Working research notes (e.g., strategy breakdowns)
- `.github/workflows/` - GitHub Actions for likes system via Gist storage

## Features

- **Future posts**: `future: true` in _config.yml — posts with future dates are built (useful for UTC timezone offset)
- **SEO/Feed/Sitemap**: jekyll-feed, jekyll-seo-tag, jekyll-sitemap plugins
- **Mermaid diagrams**: Supported in posts via ```mermaid code blocks
- **Disqus comments**: Enabled via `comments: true` in frontmatter
- **Like button**: Custom implementation using GitHub Gist for storage
- **Google Analytics**: Configured in _config.yml
- **TOC sidebar**: Table of contents via `toc-sidebar.html` include
- **Series banner**: Multi-part post series support via `series-banner.html`
- **Google AdSense**: Ad units via `ad-unit.html` and `google-adsense.html` includes
