# AxiomFinity - Financial News Website PRD

## Original Problem Statement
Full-stack financial news website for retail crypto/financial investors. Brand: **AxiomFinity** (www.axiomfinity.com)

## Architecture
React 19 + FastAPI + MongoDB | Cloudinary images | Railway deployment | GoDaddy domain

## What's Implemented

### Core Site
- Homepage with reorderable sections (Latest, Crypto, Press Releases, Sponsored, More Stories)
- Live market ticker (CoinGecko), article pages with DOMPurify sanitization
- Education, About (with team section), Contact, Legal pages, Search, Author profiles
- **Multiple category badges** on article cards and article detail pages

### Admin CMS
- Articles CRUD with TipTap WYSIWYG editor + image upload (Cloudinary)
- **TipTap content loads correctly when editing existing articles** (async content sync fix)
- **Ctrl+K inline link input** in TipTap editor (also accessible via toolbar link button)
- **Media Library** modal with image grid, search, upload new, sync from Cloudinary, select existing images
- **Exact publish timestamps** (date + time) in admin articles list
- Categories & Tags management
- **Pages editor** (Privacy Policy, Terms, Financial Disclaimer, About, Education pages)
- **Homepage section reordering** (move sections up/down)
- **Team Members management** (name, role, bio, avatar - shown on About page)
- **Users & Roles** (super_admin, admin, editor, author)
- **SEO / Nofollow settings** (toggle nofollow, exclude dofollow domains)
- Homepage hero curation, Admin profile with social fields

### SEO & Analytics
- XML sitemap, **News sitemap** (Google News format), OG meta tags
- **Dynamic OG meta tags** for social crawlers (X, Facebook, CMC) — Nginx detects bot user-agents and proxies to backend's `/api/og/{category}/{slug}` endpoint serving server-rendered HTML with og:title, og:description, og:image, twitter:card, canonical URL
- **RSS 2.0 Feed** (`/rss.xml`) — title, link, pubDate, dc:creator, categories, description, enclosure image, media:content/thumbnail, atom:self, channel image
- RSS auto-discovery `<link>` tag in HTML `<head>`
- Nginx proxy for `/sitemap.xml`, `/news-sitemap.xml`, `/rss.xml` to backend
- **Plausible Analytics** integrated
- Clean URLs, article scheduling, `robots.txt`

### Production
- Cloudinary image storage, Dockerfiles, Railway deployment
- CORS with Bearer token auth, DOMPurify XSS protection
- Meta: "AxiomFinity | Crypto & Financial News"

## Pending
- Cloudinary credentials on Railway (image uploads won't work without them)

## Recently Fixed
- Sitemap redirect: Nginx now uses `envsubst` at startup to redirect `/sitemap.xml` and `/news-sitemap.xml` to the backend API endpoints. Updated `robots.txt` to reference `www.axiomfinity.com/sitemap.xml` (canonical domain).

## Backlog
- P2: CTA buttons in editor, article revision history
- P2: Category page FAQs (add curated FAQ sections to /crypto, /markets, etc.)
- P2: Topic authority pages (/topics/xrp-news, /topics/bitcoin-price-prediction)
- P3: Comments, newsletter, analytics dashboard, MFA
