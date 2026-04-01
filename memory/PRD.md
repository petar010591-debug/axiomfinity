# FinNews - Financial News Website PRD

## Original Problem Statement
Build a full-stack financial news website based on a detailed blueprint (Financial_News_Website_Final_Blueprint_V2.pdf). Dark theme with gold accents inspired by CoinBureau. Target audience: retail investors in crypto/financial markets.

## Architecture
- **Frontend**: React 19 + Tailwind CSS + Shadcn UI + Framer Motion
- **Backend**: FastAPI + Motor (async MongoDB)
- **Database**: MongoDB
- **Auth**: JWT cookie + Bearer token based
- **Market Data**: CoinGecko API with fallback
- **Rich Text**: TipTap WYSIWYG Editor with media embeds
- **Storage**: Object Storage via Emergent Integrations
- **SEO**: React-Helmet-Async for OG tags, XML sitemap
- **Design**: Dark obsidian (#0A0D14) + Gold (#D4AF37), Cabinet Grotesk + Manrope fonts

## User Personas
1. **Retail Investor (Reader)**: Browses news, reads articles, searches content, visits educational pages
2. **Admin/Editor**: Creates, edits, publishes articles via CMS, manages categories/tags, curates homepage
3. **Author**: Writes and submits articles for review

## Core Requirements (Static)
- Public news website with articles, categories, search
- Admin CMS for content management
- Live market ticker
- SEO-friendly routing + OG tags + XML sitemap
- Editorial workflow (draft/published/scheduled/archived)
- RBAC (super_admin, admin, editor, author)
- Responsive design

## What's Been Implemented

### V1+V2: Core Site
- Homepage with sectioned layout: Latest News (hero bento) -> Crypto -> Press Releases -> Sponsored -> More Stories + Sidebar
- Live market ticker strip with CoinGecko API (2-min cache, fallback data)
- Latest News feed with category filtering (7 categories) & pagination
- Multi-category articles (primary + secondary categories)
- Article page with content, related articles, tags, sharing, OG meta tags
- Education hub, About page, Contact page, Legal pages, Search
- Categories: Crypto, Markets, DeFi, Analysis, Educational, Sponsored, Press Releases

### V3: Rich Content & Admin Features (Complete)
- TipTap WYSIWYG editor with embeds (Twitter, YouTube, Images, Tables)
- Object Storage integration for image uploads
- Article scheduling (publish at future date)
- Author profiles page with bio, social links, article listing
- RBAC roles (super_admin, admin, editor, author)
- XML sitemap at /api/sitemap.xml
- OG meta tags on article pages (React-Helmet-Async)
- Admin profile management with social fields

### Admin CMS
- JWT login (super_admin: petar010591@gmail.com)
- Dashboard with stats overview
- Article CRUD with TipTap editor, multi-category support, scheduling
- Categories & Tags management
- Homepage curation (hero slot selection)
- Users management with role assignment
- SEO fields per article

### Backend
- 10 sample articles seeded across 7 categories
- 8 tags, 6 pages (educational + legal + about)
- Full CRUD API with multi-category filtering
- Homepage sections endpoint for grouped content
- Market ticker with 2-min caching (CoinGecko + fallback)

## Bug Fixes Applied (Apr 2026)
- Fixed MongoDB mixed projection error in get_article_by_slug (exclusion + inclusion fields)
- Fixed React-Helmet <title> crash (multiple children -> template literal)
- Added defensive error handling for article page API failures

## Prioritized Backlog

### P1 (Ready for Deployment)
- App is feature-complete for V3. User ready to deploy.

### P2
- Article revision history & diff comparison
- RSS feed
- Multi-author collaboration workflow

### P3
- Commenting system (public users)
- Newsletter subscription
- Analytics dashboard (pageviews, popular articles)
- Ad slot management
- MFA for admin login
- IP allowlisting for admin

## Real Market Data Setup
- CoinGecko free API (no key required for basic endpoints)
- For higher rate limits: Sign up at https://www.coingecko.com/en/api
- Alternative: CoinMarketCap API (https://coinmarketcap.com/api/)
