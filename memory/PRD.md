# FinNews - Financial News Website PRD

## Original Problem Statement
Build a full-stack financial news website based on a detailed blueprint (Financial_News_Website_Final_Blueprint_V2.pdf). Dark theme with gold accents inspired by CoinBureau. Target audience: retail investors in crypto/financial markets.

## Architecture
- **Frontend**: React 19 + Tailwind CSS + Shadcn UI + Framer Motion
- **Backend**: FastAPI + Motor (async MongoDB)
- **Database**: MongoDB
- **Auth**: JWT cookie + Bearer token based
- **Market Data**: CoinGecko API with fallback
- **Design**: Dark obsidian (#0A0D14) + Gold (#D4AF37), Cabinet Grotesk + Manrope fonts

## User Personas
1. **Retail Investor (Reader)**: Browses news, reads articles, searches content, visits educational pages
2. **Admin/Editor**: Creates, edits, publishes articles via CMS, manages categories/tags, curates homepage

## Core Requirements (Static)
- Public news website with articles, categories, search
- Admin CMS for content management
- Live market ticker
- SEO-friendly routing
- Editorial workflow (draft/published/archived)
- Responsive design

## What's Been Implemented (V1 - Feb 2026)
### Public Site
- Homepage with hero bento grid (1 primary + 2 secondary cards)
- Live market ticker strip (CoinGecko + fallback data)
- Latest News feed with category filtering & pagination
- Article page with content, related articles, tags, sharing
- Education hub with educational content cards
- About page with company values
- Contact page with working form
- Legal pages (Privacy, Terms, Disclaimer)
- Search with full-text across articles
- Category navigation & filtering

### Admin CMS
- JWT login (petar010591@gmail.com)
- Dashboard with stats overview
- Article CRUD (create/edit/delete with status management)
- Categories & Tags management
- Homepage curation (hero slot selection)
- SEO fields per article

### Backend
- 8 sample articles seeded across 5 categories
- 8 tags, 6 pages (educational + legal + about)
- Full CRUD API for all entities
- Market ticker endpoint with CoinGecko fallback

## Prioritized Backlog

### P0 (Next Phase)
- Rich text editor (replace HTML textarea with WYSIWYG)
- Image upload functionality (object storage)
- Article scheduling (publish at future date)
- Author profiles page

### P1
- RBAC roles (Editor, Author, Compliance Reviewer)
- Article revision history & diff comparison
- XML sitemap generation
- Social share meta tags (OG)
- RSS feed

### P2
- Multi-author support
- Commenting system (public users)
- Newsletter subscription
- Analytics dashboard (pageviews, popular articles)
- Ad slot management
- MFA for admin login
- IP allowlisting for admin

## Real Market Data Setup
To get live market data (instead of fallback):
1. CoinGecko free API is used (no key required for basic endpoints)
2. For higher rate limits: Sign up at https://www.coingecko.com/en/api and get a demo API key
3. For premium data: CoinGecko Pro plan ($129/mo) for commercial use
4. Alternative: CoinMarketCap API (https://coinmarketcap.com/api/) 

## Next Tasks
1. Implement rich text editor (TipTap or Quill)
2. Add object storage for image uploads
3. Article scheduling system
4. Author profiles
5. SEO improvements (sitemap, OG tags)
