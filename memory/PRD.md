# FinNews - Financial News Website PRD

## Original Problem Statement
Build a full-stack financial news website based on a detailed blueprint. Dark theme with gold accents inspired by CoinBureau. Target audience: retail investors in crypto/financial markets.

## Architecture
- **Frontend**: React 19 + Tailwind CSS + Shadcn UI + Framer Motion
- **Backend**: FastAPI + Motor (async MongoDB)
- **Database**: MongoDB
- **Auth**: JWT cookie + Bearer token based
- **Market Data**: CoinGecko API with fallback
- **Rich Text**: TipTap WYSIWYG Editor with media embeds
- **Storage**: Cloudinary (replaced Emergent object storage)
- **SEO**: React-Helmet-Async for OG tags, XML sitemap
- **Security**: DOMPurify for HTML sanitization
- **Design**: Dark obsidian (#0A0D14) + Gold (#D4AF37), Cabinet Grotesk + Manrope fonts

## What's Been Implemented

### V1+V2: Core Site
- Homepage with sectioned layout (Latest, Crypto, Press Releases, Sponsored, More Stories + Sidebar)
- Live market ticker (CoinGecko + fallback)
- Multi-category articles, search, pagination
- Education hub, About, Contact, Legal pages
- 7 Categories, 8 Tags, 10 sample articles, 6 CMS pages

### V3: Rich Content & Admin Features
- TipTap WYSIWYG editor with embeds (Twitter, YouTube, Images, Tables)
- Article scheduling, Author profiles, RBAC roles
- XML sitemap, OG meta tags, Admin profile management

### V3.1: Production Readiness (Apr 2026)
- DOMPurify XSS sanitization on article content rendering
- Cloudinary image storage (replaced Emergent dependency)
- Dockerfiles for both frontend (nginx) and backend (uvicorn)
- Railway deployment guide with custom domain instructions
- Removed all Emergent-specific dependencies

## Bug Fixes Applied
- MongoDB mixed projection error in get_article_by_slug (Apr 2026)
- React-Helmet title crash - template literal fix (Apr 2026)

## Deployment
- Dockerfiles: `/app/backend/Dockerfile`, `/app/frontend/Dockerfile`
- Nginx config: `/app/frontend/nginx.conf`
- Full guide: `/app/DEPLOYMENT_GUIDE.md`
- Target: Railway (backend + frontend + MongoDB) with custom domain

## Prioritized Backlog

### P2
- CTA button blocks in editor
- Article revision history & diff comparison
- RSS feed

### P3
- Commenting system, Newsletter, Analytics dashboard
- Ad slot management, MFA, IP allowlisting
