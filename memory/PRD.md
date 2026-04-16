# AxiomFinity — Product Requirements Document

## Original Problem Statement
Build a full-stack financial news site (AxiomFinity). Features include real market data ticker, JWT auth, dark theme with gold accents, multi-category articles, a TipTap WYSIWYG editor with Cloudinary image upload, scheduled publishing, RBAC roles, author profiles, and extended CMS capabilities.

## Tech Stack
- **Frontend**: React, TailwindCSS, TipTap Editor, Framer Motion
- **Backend**: FastAPI (Python), Motor (async MongoDB)
- **Database**: MongoDB
- **Storage**: Cloudflare R2 (new uploads), Cloudinary (legacy images)
- **Analytics**: Plausible
- **Deployment**: Railway + Custom domain (www.axiomfinity.com)
- **DNS/Email**: GoDaddy DNS, Zoho Mail (petar@axiomfinity.com)

## Core Features (All Implemented)
- Dark theme with gold (#D4AF37) accents, Cabinet Grotesk typography
- Live CoinGecko market data ticker
- JWT auth with RBAC (super_admin, admin, editor, author)
- TipTap WYSIWYG editor with Ctrl+K inline links, Cloudinary image upload, Media Library
- Multi-category articles with badges
- Scheduled publishing with CET timezone support
- Dynamic server-side OG meta tags (Nginx bot-proxy)
- RSS feeds (standard + quality-filtered)
- XML Sitemaps
- Custom permalinks (slug editor)
- FAQ system with JSON-LD schema
- CMS Pages Manager (About, Contact, Legal, Educational pages)
- Team Members manager
- Homepage section ordering
- SEO/Nofollow manager
- Author profiles

## Completed Work
- [Feb 2026] Full MVP: Auth, Articles CRUD, Categories, Tags, CMS Pages, Market Ticker
- [Feb 2026] TipTap editor crash fix, multi-category badges, sitemap fix
- [Feb 2026] Publish timestamps (CET), Ctrl+K links, Media Library
- [Feb 2026] RSS/Quality RSS feeds, scheduled article auto-promotion fixes
- [Feb 2026] Tweet embed support, dynamic OG tags via Nginx
- [Feb 2026] "Updated" timestamps, FAQ system with JSON-LD
- [Feb 2026] Custom permalink editor
- [Apr 2026] DNS optimization (SPF, DKIM, DMARC) for Zoho Mail deliverability
- [Apr 2026] Contact page converted to CMS-editable page (removed form, added mailto link)
- [Apr 2026] Author URLs changed from ID-based to name-based slugs (/author/petar)
- [Apr 2026] Migrated image storage from Cloudinary to Cloudflare R2 (zero egress fees)
- [Apr 2026] SSR meta injection — all public pages serve unique title, meta, OG, canonical, JSON-LD in initial HTML
- [Apr 2026] Pages Manager upgraded: TipTap WYSIWYG editor + FAQ support for all CMS pages
- [Apr 2026] Education Hub: structured SEO pillar page with 12 beginner articles, 4 sections, featured guide, hub FAQs, per-page FAQs + JSON-LD

## Upcoming Tasks (P2)
- Category page FAQs — Add FAQ sections to category pages for long-tail SEO
- Topic authority pages — SEO landing pages for specific assets (e.g., "XRP News Today")
- Backend refactoring — Split server.py monolith (~1500+ lines) into routes/ directory

## Future/Backlog (P3)
- Custom CTA button blocks in TipTap editor
- Article revision history
- Commenting system
- Newsletter integration

## Key DB Schema
- `articles`: {title, slug, excerpt, content, cover_image, author_id, categories, status, published_at, updated_at, scheduled_at, faqs}
- `pages`: {slug, title, content, page_type, updated_at}
- `users`: {email, password_hash, name, role, bio, avatar_url, social_*}
- `categories`: {name, slug, description}
- `tags`: {name, slug}
- `contact_messages`: {name, email, message, created_at} (legacy, form removed)

## Admin Credentials
- Email: petar010591@gmail.com
- Password: Zvezda2023!

## Key Architecture Notes
- Nginx serves static React build, proxies bots/RSS/sitemaps to backend
- Backend is a monolith (server.py ~1560 lines) — needs refactoring
- Docker ARGs don't carry between build stages; frontend Dockerfile uses sed to inject backend URL
- Zoho Mail configured on domain; free plan has shared IP deliverability issues with Microsoft
