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

### Admin CMS
- Articles CRUD with TipTap WYSIWYG editor + image upload (Cloudinary)
- Categories & Tags management
- **Pages editor** (Privacy Policy, Terms, Financial Disclaimer, About, Education pages)
- **Homepage section reordering** (move sections up/down)
- **Team Members management** (name, role, bio, avatar - shown on About page)
- **Users & Roles** (super_admin, admin, editor, author)
- **SEO / Nofollow settings** (toggle nofollow, exclude dofollow domains)
- Homepage hero curation, Admin profile with social fields

### SEO & Analytics
- XML sitemap, **News sitemap** (Google News format), OG meta tags
- **Plausible Analytics** integrated
- Clean URLs, article scheduling

### Production
- Cloudinary image storage, Dockerfiles, Railway deployment
- CORS with Bearer token auth, DOMPurify XSS protection
- Meta: "AxiomFinity | Crypto & Financial News"

## Pending
- Cloudinary credentials on Railway (image uploads won't work without them)

## Backlog
- P2: CTA buttons in editor, article revision history, RSS feed
- P3: Comments, newsletter, analytics dashboard, MFA
