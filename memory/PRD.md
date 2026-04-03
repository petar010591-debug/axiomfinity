# AxiomFinity (formerly FinNews) - Financial News Website PRD

## Original Problem Statement
Build a full-stack financial news website. Dark theme with gold accents inspired by CoinBureau. Target audience: retail investors in crypto/financial markets. Brand: **AxiomFinity** (www.axiomfinity.com)

## Architecture
- **Frontend**: React 19 + Tailwind CSS + Shadcn UI + Framer Motion
- **Backend**: FastAPI + Motor (async MongoDB)
- **Database**: MongoDB
- **Auth**: JWT Bearer token based
- **Market Data**: CoinGecko API with fallback
- **Rich Text**: TipTap WYSIWYG Editor with media embeds
- **Storage**: Cloudinary
- **SEO**: React-Helmet-Async for OG tags, XML sitemap
- **Security**: DOMPurify for HTML sanitization
- **Design**: Dark obsidian (#0A0D14) + Gold (#D4AF37)
- **Deployment**: Railway (frontend + backend + MongoDB)
- **Domain**: www.axiomfinity.com (GoDaddy → Railway)

## What's Been Implemented

### Core Site
- Homepage with sectioned layout (Latest, Crypto, Press Releases, Sponsored, More Stories + Sidebar)
- Live market ticker (CoinGecko + fallback)
- Multi-category articles, search, pagination
- Education hub, About, Contact, Legal pages
- 7 Categories, 8 Tags, 10 sample articles, 6 CMS pages

### Rich Content & Admin
- TipTap WYSIWYG editor with embeds (Twitter, YouTube, Images, Tables)
- Featured image upload button (file picker → Cloudinary)
- Article scheduling, Author profiles, RBAC roles
- XML sitemap, OG meta tags, Admin profile management

### Production Readiness
- DOMPurify XSS sanitization
- Cloudinary image storage (replaced Emergent dependency)
- Dockerfiles for Railway deployment
- CORS configured for cross-origin Bearer token auth
- Admin seed always syncs password from env vars

### Branding (Apr 2026)
- Renamed from FinNews → AxiomFinity
- Custom logo in header, footer, admin login, admin sidebar
- Removed "Made with Emergent" badge
- Updated page titles, meta description, copyright

## Deployment
- **Frontend**: Railway (dazzling-light) — Nginx serving React build, REACT_APP_BACKEND_URL baked at build time
- **Backend**: Railway (axiomfinity) — FastAPI Docker container
- **Database**: Railway MongoDB addon
- **Domain**: www.axiomfinity.com via GoDaddy CNAME → Railway

## Pending Items
- Clicky analytics integration (waiting for Site ID)
- Cloudinary credentials need to be set on Railway backend

## Prioritized Backlog

### P1
- Connect Clicky analytics
- Verify Cloudinary image uploads on production

### P2
- CTA button blocks in editor
- Article revision history
- RSS feed

### P3
- Commenting system, Newsletter, Analytics dashboard
- Ad slot management, MFA
