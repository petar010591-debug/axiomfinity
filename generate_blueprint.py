#!/usr/bin/env python3
"""Generate FinNews Project Blueprint PDF"""
from fpdf import FPDF
import os

class BlueprintPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, "FinNews - Technical Blueprint", align="L")
        self.cell(0, 8, f"Page {self.page_no()}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, "Confidential - FinNews Project Documentation - April 2026", align="C")

    def section_title(self, title, level=1):
        if level == 1:
            self.ln(4)
            self.set_fill_color(10, 13, 20)
            self.set_text_color(212, 175, 55)
            self.set_font("Helvetica", "B", 16)
            self.cell(0, 12, f"  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
            self.set_text_color(40, 40, 40)
            self.ln(3)
        elif level == 2:
            self.ln(2)
            self.set_font("Helvetica", "B", 13)
            self.set_text_color(10, 13, 20)
            self.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(212, 175, 55)
            self.line(10, self.get_y(), 80, self.get_y())
            self.set_draw_color(0, 0, 0)
            self.set_text_color(40, 40, 40)
            self.ln(3)
        elif level == 3:
            self.ln(1)
            self.set_font("Helvetica", "B", 11)
            self.set_text_color(60, 60, 60)
            self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
            self.set_text_color(40, 40, 40)
            self.ln(1)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def bullet(self, text, indent=10):
        self.set_font("Helvetica", "", 10)
        self.set_x(self.l_margin + indent)
        w = self.w - self.l_margin - indent - self.r_margin
        self.multi_cell(w, 5.5, f"- {text}")

    def code_block(self, text):
        self.set_fill_color(240, 240, 245)
        self.set_font("Courier", "", 8.5)
        for line in text.strip().split("\n"):
            self.cell(0, 5, f"  {line}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 10)
        self.ln(2)

    def key_value(self, key, value, indent=10):
        self.set_font("Helvetica", "B", 10)
        self.set_x(self.l_margin + indent)
        w = self.w - self.l_margin - indent - self.r_margin
        self.multi_cell(w, 5.5, f"{key}: {value}")
        self.set_font("Helvetica", "", 10)

    def table_row(self, cells, widths, bold=False, fill=False):
        h = 7
        style = "B" if bold else ""
        if fill:
            self.set_fill_color(10, 13, 20)
            self.set_text_color(212, 175, 55)
        for i, (cell, w) in enumerate(zip(cells, widths)):
            self.set_font("Helvetica", style, 9)
            self.cell(w, h, str(cell), border=1, fill=fill)
        self.ln(h)
        if fill:
            self.set_text_color(40, 40, 40)


pdf = BlueprintPDF()
pdf.set_title("FinNews - Technical Blueprint")
pdf.set_author("FinNews Engineering Team")

# ═══════════════════════════════════════════════════════════
# COVER PAGE
# ═══════════════════════════════════════════════════════════
pdf.add_page()
pdf.ln(50)
pdf.set_fill_color(10, 13, 20)
pdf.rect(0, 0, 210, 297, "F")

pdf.set_text_color(212, 175, 55)
pdf.set_font("Helvetica", "B", 36)
pdf.cell(0, 15, "FinNews", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(3)
pdf.set_font("Helvetica", "", 16)
pdf.set_text_color(200, 200, 200)
pdf.cell(0, 10, "Technical Blueprint & Architecture Document", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(8)

pdf.set_draw_color(212, 175, 55)
pdf.line(60, pdf.get_y(), 150, pdf.get_y())
pdf.ln(12)

pdf.set_font("Helvetica", "", 12)
pdf.set_text_color(160, 160, 160)
pdf.cell(0, 8, "Full-Stack Financial News Platform", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, "React + FastAPI + MongoDB", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(5)
pdf.cell(0, 8, "Version 3.0  |  April 2026", align="C", new_x="LMARGIN", new_y="NEXT")

pdf.ln(40)
pdf.set_font("Helvetica", "I", 9)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 6, "Dark theme (#0A0D14) with gold accents (#D4AF37)", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 6, "Inspired by CoinBureau | Built for retail crypto investors", align="C", new_x="LMARGIN", new_y="NEXT")

# ═══════════════════════════════════════════════════════════
# TABLE OF CONTENTS
# ═══════════════════════════════════════════════════════════
pdf.add_page()
pdf.set_text_color(40, 40, 40)
pdf.section_title("Table of Contents")

toc = [
    ("1.", "Project Overview", 3),
    ("2.", "Architecture & Tech Stack", 4),
    ("3.", "Design System", 5),
    ("4.", "Database Schema", 6),
    ("5.", "API Reference", 7),
    ("6.", "Frontend Structure", 9),
    ("7.", "Features - Public Site", 10),
    ("8.", "Features - Admin CMS", 11),
    ("9.", "Features - WYSIWYG Editor", 12),
    ("10.", "Authentication & RBAC", 13),
    ("11.", "SEO & Sitemap", 14),
    ("12.", "Object Storage", 14),
    ("13.", "Market Data Integration", 15),
    ("14.", "Seed Data & Sample Content", 15),
    ("15.", "File Structure", 16),
    ("16.", "Deployment Guide", 17),
    ("17.", "Future Roadmap", 18),
]
for num, title, pg in toc:
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(10, 7, num)
    pdf.cell(140, 7, title)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, str(pg), align="R", new_x="LMARGIN", new_y="NEXT")

# ═══════════════════════════════════════════════════════════
# 1. PROJECT OVERVIEW
# ═══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("1. Project Overview")

pdf.section_title("Mission", 2)
pdf.body_text("FinNews is a full-stack financial news platform targeting retail investors in the crypto and financial markets space. It delivers real-time market data, curated news across multiple categories, and a powerful admin CMS for content creation and management.")

pdf.section_title("Target Audience", 2)
pdf.bullet("Retail Investors - Browse categorized news, read articles, search content")
pdf.bullet("Content Creators (Authors/Editors) - Write articles using WYSIWYG editor")
pdf.bullet("Administrators - Full site management, user roles, homepage curation")

pdf.section_title("Key Capabilities", 2)
pdf.bullet("Live cryptocurrency market ticker with real-time price data")
pdf.bullet("Multi-category article system with 7 content categories")
pdf.bullet("TipTap WYSIWYG rich text editor with media embeds (Twitter, YouTube, Images, Tables)")
pdf.bullet("Role-based access control (super_admin, admin, editor, author)")
pdf.bullet("Article scheduling for future publication dates")
pdf.bullet("Object Storage integration for image uploads")
pdf.bullet("SEO optimization: XML sitemap, Open Graph meta tags, clean URLs")
pdf.bullet("Author profile pages with bio, social links, and article listings")
pdf.bullet("Homepage curation with hero slot management")
pdf.bullet("Dark theme UI with gold accents, inspired by CoinBureau")

# ═══════════════════════════════════════════════════════════
# 2. ARCHITECTURE & TECH STACK
# ═══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("2. Architecture & Tech Stack")

pdf.section_title("System Architecture", 2)
pdf.body_text("The application follows a standard three-tier architecture with a React SPA frontend communicating with a FastAPI backend, which connects to MongoDB for data persistence.")

pdf.code_block("""
+-------------------+       +-------------------+       +-------------------+
|                   |       |                   |       |                   |
|   React 19 SPA    | <---> |   FastAPI Server  | <---> |     MongoDB       |
|   (Port 3000)     |  API  |   (Port 8001)     |       |   (Motor Async)   |
|                   |       |                   |       |                   |
+-------------------+       +-------------------+       +-------------------+
        |                           |
        |                   +-------+-------+
        |                   |               |
        v               v               v
   Tailwind CSS     CoinGecko API    Object Storage
   Framer Motion    (Market Data)    (Emergent)
   React-Helmet
   TipTap Editor
""")

pdf.section_title("Frontend Stack", 2)
pdf.key_value("Framework", "React 19 with React Router 7")
pdf.key_value("Styling", "Tailwind CSS 3 + Shadcn/UI components")
pdf.key_value("Animation", "Framer Motion 12")
pdf.key_value("Rich Text", "TipTap 3.22 (ProseMirror-based)")
pdf.key_value("SEO", "React-Helmet-Async 3")
pdf.key_value("HTTP Client", "Axios")
pdf.key_value("Icons", "Lucide React")
pdf.key_value("Ticker", "React Fast Marquee")

pdf.section_title("Backend Stack", 2)
pdf.key_value("Framework", "FastAPI 0.110.1")
pdf.key_value("Database Driver", "Motor 3.3.1 (Async MongoDB)")
pdf.key_value("Authentication", "JWT (PyJWT) + bcrypt password hashing")
pdf.key_value("HTTP Client", "HTTPX (async) + Requests (sync)")
pdf.key_value("Slug Generation", "python-slugify")
pdf.key_value("Object Storage", "Emergent Integrations library")
pdf.key_value("Server", "Uvicorn 0.25")

pdf.section_title("Database", 2)
pdf.key_value("Engine", "MongoDB")
pdf.key_value("Driver", "PyMongo 4.5 / Motor 3.3.1 (async wrapper)")
pdf.key_value("Collections", "users, articles, categories, tags, pages, homepage_slots, contact_messages")

# ═══════════════════════════════════════════════════════════
# 3. DESIGN SYSTEM
# ═══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("3. Design System")

pdf.section_title("Color Palette", 2)
colors = [
    ("Background Base", "#0A0D14", "Dark obsidian - main background"),
    ("Surface", "#121620", "Card and component backgrounds"),
    ("Surface Hover", "#1C2230", "Hover states on surfaces"),
    ("Brand Gold", "#D4AF37", "Primary accent, CTAs, active states"),
    ("Brand Gold Hover", "#C39F2F", "Hover state for gold elements"),
    ("Gold Muted", "rgba(212,175,55,0.12)", "Subtle gold backgrounds"),
    ("Text Primary", "#F3F4F6", "Main text color"),
    ("Text Secondary", "#9CA3AF", "Subtitles and descriptions"),
    ("Text Muted", "#6B7280", "Meta info, timestamps"),
    ("Border Default", "#232B3E", "Card borders, dividers"),
    ("Border Subtle", "#1A202E", "Subtle separators"),
    ("Positive", "#10B981", "Green for gains/success"),
    ("Negative", "#EF4444", "Red for losses/errors"),
]
widths = [40, 45, 105]
pdf.table_row(["Token", "Value", "Usage"], widths, bold=True, fill=True)
for name, val, usage in colors:
    pdf.table_row([name, val, usage], widths)

pdf.ln(3)
pdf.section_title("Typography", 2)
pdf.key_value("Headings", "Cabinet Grotesk (fontshare.com) - weights: 400, 500, 700, 800")
pdf.key_value("Body Text", "Manrope (Google Fonts) - weights: 300-800")
pdf.key_value("Code", "JetBrains Mono (monospace)")
pdf.ln(2)
pdf.body_text("Heading Scale: H1 = text-4xl/5xl/6xl responsive, H2 = text-2xl, Body = text-base/sm")

pdf.section_title("Component Library", 2)
pdf.body_text("Built on Shadcn/UI (Radix primitives + Tailwind). Key components used: Button, Card, Dialog, DropdownMenu, Input, Select, Tabs, Table, Tooltip, Toast (Sonner), Calendar, Badge, Separator, ScrollArea.")

# ═══════════════════════════════════════════════════════════
# 4. DATABASE SCHEMA
# ═══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("4. Database Schema")

pdf.section_title("users", 2)
fields = [
    ("_id", "ObjectId", "Auto-generated primary key"),
    ("email", "String", "Unique, lowercase, indexed"),
    ("password_hash", "String", "bcrypt hashed password"),
    ("name", "String", "Display name"),
    ("role", "String", "super_admin | admin | editor | author"),
    ("bio", "String", "Author biography"),
    ("avatar_url", "String", "Profile image URL"),
    ("social_twitter", "String", "Twitter/X profile link"),
    ("social_linkedin", "String", "LinkedIn profile link"),
    ("website", "String", "Personal website URL"),
    ("created_at", "String (ISO)", "Account creation timestamp"),
]
widths = [35, 25, 130]
pdf.table_row(["Field", "Type", "Description"], widths, bold=True, fill=True)
for f, t, d in fields:
    pdf.table_row([f, t, d], widths)

pdf.ln(3)
pdf.section_title("articles", 2)
fields = [
    ("_id", "ObjectId", "Auto-generated"),
    ("title", "String", "Article headline"),
    ("slug", "String", "URL-friendly identifier (unique)"),
    ("excerpt", "String", "Short description / summary"),
    ("content", "String", "Full HTML content (TipTap output)"),
    ("featured_image", "String", "Hero image URL"),
    ("category_id", "String", "Primary category ObjectId ref"),
    ("category_name", "String", "Denormalized category name"),
    ("category_slug", "String", "Denormalized category slug"),
    ("categories", "Array[Str]", "All category slugs (primary + secondary)"),
    ("tags", "Array[Str]", "Tag names"),
    ("author_id", "String", "User ObjectId ref"),
    ("author_name", "String", "Denormalized author name"),
    ("status", "String", "draft | published | scheduled | archived"),
    ("is_sponsored", "Boolean", "Sponsored content flag"),
    ("scheduled_at", "String", "Future publish date (ISO)"),
    ("published_at", "String", "Publication timestamp (ISO)"),
    ("og_image", "String", "Open Graph image URL"),
    ("meta_title", "String", "SEO title override"),
    ("meta_description", "String", "SEO description override"),
    ("created_at", "String", "Creation timestamp"),
    ("updated_at", "String", "Last update timestamp"),
]
widths = [35, 25, 130]
pdf.table_row(["Field", "Type", "Description"], widths, bold=True, fill=True)
for f, t, d in fields:
    pdf.table_row([f, t, d], widths)

pdf.add_page()
pdf.section_title("categories", 2)
fields = [
    ("_id", "ObjectId", "Auto-generated"),
    ("name", "String", "Category display name"),
    ("slug", "String", "URL-friendly identifier"),
    ("description", "String", "Category description"),
    ("created_at", "String", "Timestamp"),
]
widths = [35, 25, 130]
pdf.table_row(["Field", "Type", "Description"], widths, bold=True, fill=True)
for f, t, d in fields:
    pdf.table_row([f, t, d], widths)

pdf.ln(3)
pdf.section_title("tags", 2)
fields = [
    ("_id", "ObjectId", "Auto-generated"),
    ("name", "String", "Tag display name"),
    ("slug", "String", "URL-friendly identifier"),
    ("created_at", "String", "Timestamp"),
]
pdf.table_row(["Field", "Type", "Description"], widths, bold=True, fill=True)
for f, t, d in fields:
    pdf.table_row([f, t, d], widths)

pdf.ln(3)
pdf.section_title("pages", 2)
fields = [
    ("_id", "ObjectId", "Auto-generated"),
    ("title", "String", "Page title"),
    ("slug", "String", "URL path"),
    ("content", "String", "HTML content"),
    ("page_type", "String", "educational | legal | about"),
    ("created_at", "String", "Timestamp"),
    ("updated_at", "String", "Timestamp"),
]
pdf.table_row(["Field", "Type", "Description"], widths, bold=True, fill=True)
for f, t, d in fields:
    pdf.table_row([f, t, d], widths)

pdf.ln(3)
pdf.section_title("homepage_slots", 2)
fields = [
    ("_id", "String", "Always 'config' (singleton)"),
    ("hero_primary", "String", "Article ID for main hero"),
    ("hero_secondary", "Array[Str]", "Article IDs for secondary heroes"),
]
pdf.table_row(["Field", "Type", "Description"], widths, bold=True, fill=True)
for f, t, d in fields:
    pdf.table_row([f, t, d], widths)

pdf.ln(3)
pdf.section_title("contact_messages", 2)
fields = [
    ("name", "String", "Sender name"),
    ("email", "String", "Sender email"),
    ("subject", "String", "Message subject"),
    ("message", "String", "Message body"),
    ("created_at", "String", "Timestamp"),
]
pdf.table_row(["Field", "Type", "Description"], widths, bold=True, fill=True)
for f, t, d in fields:
    pdf.table_row([f, t, d], widths)

# ═══════════════════════════════════════════════════════════
# 5. API REFERENCE
# ═══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("5. API Reference")
pdf.body_text("All endpoints are prefixed with /api. Authentication uses JWT tokens via httpOnly cookies or Bearer header.")

pdf.section_title("Authentication", 2)
endpoints = [
    ("POST", "/api/auth/login", "Login with email/password, returns JWT token + sets cookies"),
    ("POST", "/api/auth/logout", "Clears auth cookies"),
    ("GET", "/api/auth/me", "Returns current user profile (requires auth)"),
]
widths = [18, 50, 122]
pdf.table_row(["Method", "Endpoint", "Description"], widths, bold=True, fill=True)
for m, e, d in endpoints:
    pdf.table_row([m, e, d], widths)

pdf.ln(3)
pdf.section_title("Public Articles", 2)
endpoints = [
    ("GET", "/api/articles", "List articles with pagination, category/tag filters"),
    ("GET", "/api/articles/featured", "Get hero primary + secondary articles"),
    ("GET", "/api/articles/homepage-sections", "Get categorized homepage content"),
    ("GET", "/api/articles/by-slug/{slug}", "Get full article with author & related"),
    ("GET", "/api/articles/search?q=", "Full-text search across articles"),
]
pdf.table_row(["Method", "Endpoint", "Description"], widths, bold=True, fill=True)
for m, e, d in endpoints:
    pdf.table_row([m, e, d], widths)

pdf.ln(3)
pdf.section_title("Public Resources", 2)
endpoints = [
    ("GET", "/api/categories", "List all categories"),
    ("GET", "/api/tags", "List all tags"),
    ("GET", "/api/pages", "List CMS pages (with optional type filter)"),
    ("GET", "/api/pages/{slug}", "Get page by slug"),
    ("POST", "/api/contact", "Submit contact form message"),
    ("GET", "/api/market/ticker", "Live crypto prices (2-min cache)"),
    ("GET", "/api/authors/{id}", "Author profile + their articles"),
    ("GET", "/api/sitemap.xml", "XML sitemap for search engines"),
]
pdf.table_row(["Method", "Endpoint", "Description"], widths, bold=True, fill=True)
for m, e, d in endpoints:
    pdf.table_row([m, e, d], widths)

pdf.ln(3)
pdf.section_title("Admin Articles (Auth Required)", 2)
endpoints = [
    ("GET", "/api/admin/articles", "List all articles (any status)"),
    ("GET", "/api/admin/articles/{id}", "Get article by ID"),
    ("POST", "/api/admin/articles", "Create new article"),
    ("PUT", "/api/admin/articles/{id}", "Update article"),
    ("DELETE", "/api/admin/articles/{id}", "Delete article"),
]
pdf.table_row(["Method", "Endpoint", "Description"], widths, bold=True, fill=True)
for m, e, d in endpoints:
    pdf.table_row([m, e, d], widths)

pdf.add_page()
pdf.section_title("Admin Management (Auth Required)", 2)
endpoints = [
    ("POST", "/api/admin/categories", "Create category"),
    ("PUT", "/api/admin/categories/{id}", "Update category (cascades to articles)"),
    ("DELETE", "/api/admin/categories/{id}", "Delete category"),
    ("POST", "/api/admin/tags", "Create tag"),
    ("DELETE", "/api/admin/tags/{id}", "Delete tag"),
    ("POST", "/api/admin/pages", "Create CMS page"),
    ("PUT", "/api/admin/pages/{id}", "Update CMS page"),
    ("DELETE", "/api/admin/pages/{id}", "Delete CMS page"),
    ("GET", "/api/admin/homepage", "Get homepage curation slots"),
    ("PUT", "/api/admin/homepage", "Update hero slots"),
    ("GET", "/api/admin/stats", "Dashboard statistics"),
    ("POST", "/api/upload", "Upload image to object storage"),
    ("PUT", "/api/admin/profile", "Update own profile"),
    ("GET", "/api/admin/users", "List all users (admin+)"),
    ("POST", "/api/admin/users", "Create new user (admin+)"),
    ("PUT", "/api/admin/users/{id}/role", "Change user role (super_admin only)"),
    ("DELETE", "/api/admin/users/{id}", "Delete user (super_admin only)"),
]
widths = [18, 55, 117]
pdf.table_row(["Method", "Endpoint", "Description"], widths, bold=True, fill=True)
for m, e, d in endpoints:
    pdf.table_row([m, e, d], widths)

# ═══════════════════════════════════════════════════════════
# 6. FRONTEND STRUCTURE
# ═══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("6. Frontend Structure")

pdf.section_title("Routing", 2)
routes = [
    ("/", "HomePage", "Homepage with sectioned news layout"),
    ("/latest", "LatestNewsPage", "All articles feed with pagination"),
    ("/category/:slug", "LatestNewsPage", "Category-filtered articles"),
    ("/education", "EducationPage", "Educational content hub"),
    ("/about", "AboutPage", "Company info and values"),
    ("/contact", "ContactPage", "Contact form"),
    ("/search", "SearchPage", "Full-text search"),
    ("/page/:slug", "LegalPage", "Static pages (privacy, terms, etc.)"),
    ("/author/:id", "AuthorProfile", "Author bio + article list"),
    ("/:category/:slug", "ArticlePage", "Full article with OG tags"),
    ("/admin/login", "AdminLogin", "Admin authentication"),
    ("/admin/*", "AdminDashboard", "Nested admin routes"),
]
widths = [42, 35, 113]
pdf.table_row(["Route", "Component", "Description"], widths, bold=True, fill=True)
for r, c, d in routes:
    pdf.table_row([r, c, d], widths)

pdf.ln(3)
pdf.section_title("Component Map", 2)
components = [
    ("Header.js", "210 lines", "Navigation bar with categories dropdown, search toggle"),
    ("Footer.js", "66 lines", "Site footer with links and branding"),
    ("TickerStrip.js", "49 lines", "Scrolling market price ticker"),
    ("ArticleCard.js", "93 lines", "3 variants: Hero, Secondary, Compact"),
    ("Sidebar.js", "76 lines", "Trending articles sidebar widget"),
    ("TipTapEditor.js", "275 lines", "Full WYSIWYG editor with toolbar"),
]
widths = [40, 22, 128]
pdf.table_row(["File", "Size", "Purpose"], widths, bold=True, fill=True)
for f, s, p in components:
    pdf.table_row([f, s, p], widths)

pdf.ln(3)
pdf.section_title("Admin Pages", 2)
admin_pages = [
    ("AdminDashboard.js", "180 lines", "Stats overview + sidebar navigation"),
    ("AdminLogin.js", "81 lines", "JWT login form"),
    ("ArticlesList.js", "163 lines", "Article management table"),
    ("ArticleEditor.js", "295 lines", "TipTap editor + scheduling + categories"),
    ("CategoriesManager.js", "171 lines", "CRUD for categories"),
    ("HomepageCuration.js", "127 lines", "Hero slot assignment"),
    ("UsersManager.js", "153 lines", "User CRUD + role management"),
    ("AdminProfile.js", "111 lines", "Profile editor with social fields"),
]
widths = [45, 22, 123]
pdf.table_row(["File", "Size", "Purpose"], widths, bold=True, fill=True)
for f, s, p in admin_pages:
    pdf.table_row([f, s, p], widths)

# ═══════════════════════════════════════════════════════════
# 7. FEATURES - PUBLIC SITE
# ═══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("7. Features - Public Site")

pdf.section_title("Homepage Layout", 2)
pdf.body_text("The homepage renders categorized content sections fetched from /api/articles/homepage-sections:")
pdf.bullet("Latest News: Hero bento layout (1 large + 2 secondary cards)")
pdf.bullet("Crypto: Dedicated cryptocurrency news section")
pdf.bullet("Press Releases: Official announcements")
pdf.bullet("Sponsored: Clearly labeled sponsored content")
pdf.bullet("More Stories: Remaining articles + Sidebar with trending")
pdf.ln(2)

pdf.section_title("Article Page", 2)
pdf.bullet("Full article rendering with TipTap HTML content")
pdf.bullet("Breadcrumb navigation (Home > Category > Title)")
pdf.bullet("Author info with avatar and link to profile")
pdf.bullet("Featured image with responsive sizing")
pdf.bullet("Related articles grid (same category, max 3)")
pdf.bullet("Share button (copy URL to clipboard)")
pdf.bullet("Tag links for discovery")
pdf.bullet("OG meta tags via React-Helmet for social sharing")
pdf.ln(2)

pdf.section_title("Search & Navigation", 2)
pdf.bullet("Full-text search across titles, excerpts, content, and tags")
pdf.bullet("Category navigation via header dropdown")
pdf.bullet("Pagination on list pages (12 articles per page)")
pdf.bullet("Live market ticker strip below header")
pdf.ln(2)

pdf.section_title("Static Pages", 2)
pdf.bullet("Education Hub: Blockchain/crypto educational articles")
pdf.bullet("About: Company mission and values")
pdf.bullet("Contact: Form that saves to database")
pdf.bullet("Legal: Privacy Policy, Terms & Conditions, Financial Disclaimer")

# ═══════════════════════════════════════════════════════════
# 8. FEATURES - ADMIN CMS
# ═══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("8. Features - Admin CMS")

pdf.section_title("Dashboard", 2)
pdf.body_text("Admin dashboard at /admin provides a statistics overview and sidebar navigation. Stats include: total articles, published, drafts, scheduled, categories, tags, pages, and team members.")

pdf.section_title("Article Management", 2)
pdf.bullet("Full CRUD: Create, Read, Update, Delete articles")
pdf.bullet("TipTap WYSIWYG editor for rich content creation")
pdf.bullet("Primary category selection (dropdown)")
pdf.bullet("Secondary categories (multi-select toggle buttons)")
pdf.bullet("Tags input with comma-separated entry")
pdf.bullet("Featured image upload via object storage")
pdf.bullet("Status management: Draft, Published, Scheduled, Archived")
pdf.bullet("Article scheduling with date/time picker")
pdf.bullet("SEO fields: Meta title, meta description, OG image")
pdf.bullet("Automatic slug generation from title")

pdf.section_title("Content Organization", 2)
pdf.bullet("Categories CRUD with cascade updates to articles")
pdf.bullet("Tags management")
pdf.bullet("Homepage curation: Select hero primary and secondary articles")
pdf.bullet("CMS pages management for static content")

pdf.section_title("User & Profile", 2)
pdf.bullet("User creation with role assignment")
pdf.bullet("Role management (super_admin can change roles)")
pdf.bullet("Profile editing: name, bio, avatar, Twitter, LinkedIn, website")
pdf.bullet("User deletion (super_admin only, cannot delete self)")

# ═══════════════════════════════════════════════════════════
# 9. FEATURES - WYSIWYG EDITOR
# ═══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("9. WYSIWYG Editor (TipTap)")

pdf.section_title("Overview", 2)
pdf.body_text("The article editor uses TipTap v3.22, a headless ProseMirror-based editor. It provides a full toolbar for rich content creation with support for various media embeds.")

pdf.section_title("Toolbar Features", 2)
pdf.bullet("Text formatting: Bold, Italic, Underline, Strikethrough")
pdf.bullet("Headings: H1, H2, H3")
pdf.bullet("Lists: Bullet list, Ordered list")
pdf.bullet("Text alignment: Left, Center, Right, Justify")
pdf.bullet("Block elements: Blockquote, Code block, Horizontal rule")
pdf.bullet("Media: Image insertion (URL), YouTube video embed")
pdf.bullet("Tables: Insert, add/remove rows and columns")
pdf.bullet("Links: Insert/edit hyperlinks")
pdf.bullet("History: Undo/Redo")

pdf.section_title("TipTap Extensions", 2)
extensions = [
    ("@tiptap/starter-kit", "Core editing (paragraphs, headings, lists, code blocks)"),
    ("@tiptap/extension-image", "Image node insertion"),
    ("@tiptap/extension-youtube", "YouTube video embeds"),
    ("@tiptap/extension-table", "Table support (with cell, header, row)"),
    ("@tiptap/extension-link", "Hyperlink support with URL validation"),
    ("@tiptap/extension-underline", "Underline text formatting"),
    ("@tiptap/extension-text-align", "Text alignment options"),
    ("@tiptap/extension-placeholder", "Placeholder text when empty"),
]
widths = [65, 125]
pdf.table_row(["Extension", "Purpose"], widths, bold=True, fill=True)
for e, p in extensions:
    pdf.table_row([e, p], widths)

pdf.ln(3)
pdf.section_title("Content Rendering", 2)
pdf.body_text("Article content stored as HTML is rendered on the public article page using dangerouslySetInnerHTML. Custom CSS in index.css styles TipTap output elements (headings, paragraphs, lists, blockquotes, tables, code blocks, images) within the .article-content class.")

# ═══════════════════════════════════════════════════════════
# 10. AUTH & RBAC
# ═══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("10. Authentication & RBAC")

pdf.section_title("Authentication Flow", 2)
pdf.body_text("1. User submits email/password to POST /api/auth/login")
pdf.body_text("2. Server verifies credentials using bcrypt")
pdf.body_text("3. On success, server issues JWT access token (24h) and refresh token (7d)")
pdf.body_text("4. Tokens set as httpOnly cookies + access token returned in response body")
pdf.body_text("5. Frontend stores token in AuthContext and sends via cookie or Bearer header")
pdf.body_text("6. Protected endpoints use get_current_user dependency to validate JWT")

pdf.section_title("Role Hierarchy", 2)
roles = [
    ("super_admin", "4", "Full access: all features + user management + role changes"),
    ("admin", "3", "Content management + user creation (cannot change roles)"),
    ("editor", "2", "Create and edit articles, manage categories/tags"),
    ("author", "1", "Create and edit own articles only"),
]
widths = [30, 15, 145]
pdf.table_row(["Role", "Level", "Permissions"], widths, bold=True, fill=True)
for r, l, p in roles:
    pdf.table_row([r, l, p], widths)

pdf.ln(3)
pdf.section_title("Security Features", 2)
pdf.bullet("Passwords hashed with bcrypt (salt rounds auto-generated)")
pdf.bullet("JWT tokens with expiration (24h access, 7d refresh)")
pdf.bullet("httpOnly cookies prevent XSS token theft")
pdf.bullet("Token type validation (access vs refresh)")
pdf.bullet("Role-based middleware via require_role() dependency")
pdf.bullet("Self-deletion prevention for super_admin")

# ═══════════════════════════════════════════════════════════
# 11. SEO & SITEMAP
# ═══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("11. SEO & Sitemap")

pdf.section_title("Open Graph Tags", 2)
pdf.body_text("Every article page injects OG meta tags via React-Helmet-Async:")
pdf.bullet("og:title - Article title (with meta_title override)")
pdf.bullet("og:description - Article excerpt (with meta_description override)")
pdf.bullet("og:image - Featured image (with og_image override)")
pdf.bullet("og:url - Canonical article URL")
pdf.bullet("og:type - 'article'")
pdf.bullet("twitter:card - summary_large_image")
pdf.bullet("twitter:title, twitter:description, twitter:image")

pdf.section_title("XML Sitemap", 2)
pdf.body_text("Generated dynamically at GET /api/sitemap.xml. Includes:")
pdf.bullet("Homepage (priority 1.0, hourly)")
pdf.bullet("Latest page (priority 0.9, hourly)")
pdf.bullet("Education, About, Contact pages")
pdf.bullet("All category pages (priority 0.8, daily)")
pdf.bullet("All published articles with lastmod dates (priority 0.7)")
pdf.bullet("All CMS pages (priority 0.4)")

pdf.section_title("Clean URLs", 2)
pdf.body_text("Articles use /:category/:slug format (e.g., /crypto/bitcoin-surges-past-100k). Slugs are auto-generated from titles using python-slugify with collision detection.")

# ═══════════════════════════════════════════════════════════
# 12. OBJECT STORAGE
# ═══════════════════════════════════════════════════════════
pdf.section_title("12. Object Storage")

pdf.section_title("Integration", 2)
pdf.body_text("Image uploads use Emergent's Object Storage service. The flow:")
pdf.bullet("POST /api/upload with multipart form data (image file)")
pdf.bullet("Server validates: must be image/*, max 10MB")
pdf.bullet("Generates unique filename: finnews/{uuid}.{ext}")
pdf.bullet("Uploads to Emergent Object Storage via REST API")
pdf.bullet("Returns public URL for use in articles and profiles")

pdf.section_title("Configuration", 2)
pdf.key_value("Storage URL", "https://integrations.emergentagent.com/objstore/api/v1/storage")
pdf.key_value("Auth", "EMERGENT_LLM_KEY from environment -> init -> storage_key")
pdf.key_value("Max File Size", "10MB")
pdf.key_value("Allowed Types", "image/* only")

# ═══════════════════════════════════════════════════════════
# 13. MARKET DATA
# ═══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("13. Market Data Integration")

pdf.section_title("CoinGecko API", 2)
pdf.body_text("The market ticker fetches live cryptocurrency prices from CoinGecko's free API. Response is cached for 2 minutes server-side to avoid rate limiting.")

pdf.section_title("Tracked Assets", 2)
assets = [
    ("BTC", "Bitcoin"), ("ETH", "Ethereum"), ("SOL", "Solana"), ("DOGE", "Dogecoin"),
    ("ADA", "Cardano"), ("XRP", "Ripple"), ("DOT", "Polkadot"), ("AVAX", "Avalanche"),
]
for sym, name in assets:
    pdf.bullet(f"{sym} - {name}")

pdf.ln(2)
pdf.section_title("Fallback Data", 2)
pdf.body_text("When CoinGecko is unavailable (rate limited or down), hardcoded fallback prices are returned. The ticker strip component on the frontend uses react-fast-marquee for smooth horizontal scrolling, showing each asset's symbol, price, and 24h change percentage with green/red coloring.")

# ═══════════════════════════════════════════════════════════
# 14. SEED DATA
# ═══════════════════════════════════════════════════════════
pdf.section_title("14. Seed Data & Sample Content")

pdf.section_title("Auto-Seeded on Startup", 2)
pdf.bullet("1 Admin User: super_admin role (credentials from environment)")
pdf.bullet("7 Categories: Crypto, Markets, DeFi, Analysis, Educational, Sponsored, Press Releases")
pdf.bullet("8 Tags: Bitcoin, Ethereum, Altcoins, Trading, Blockchain, NFT, Web3, Stablecoins")
pdf.bullet("10 Sample Articles: Distributed across categories with realistic financial content")
pdf.bullet("6 CMS Pages: 2 Educational, 3 Legal (Privacy, Terms, Disclaimer), 1 About")

pdf.section_title("Sample Articles", 2)
articles = [
    "Bitcoin Surges Past $100K as Institutional Demand Hits New Highs",
    "Ethereum's Layer 2 Ecosystem Reaches $50B in TVL",
    "Trezor Launches Next-Gen Hardware Wallet (Sponsored)",
    "Solana DeFi Sees Record Volume",
    "BlockFi Partners with Major Bank (Press Release)",
    "Technical Analysis: Key Support Levels This Week",
    "Understanding DeFi Yield Farming (Educational)",
    "Global Stock Markets Rally on Positive Data",
    "CoinSwap Exchange Zero-Fee Trading (Sponsored)",
    "Chainlink Announces Cross-Chain Protocol Upgrade (Press Release)",
]
for i, a in enumerate(articles, 1):
    pdf.bullet(f"{i}. {a}")

# ═══════════════════════════════════════════════════════════
# 15. FILE STRUCTURE
# ═══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("15. File Structure")

pdf.code_block("""
/app/
+-- backend/
|   +-- server.py              # Main FastAPI application (1099 lines)
|   +-- requirements.txt       # Python dependencies
|   +-- .env                   # MONGO_URL, DB_NAME, JWT_SECRET, ADMIN creds, EMERGENT_LLM_KEY
|   +-- tests/
|       +-- test_finnews_api.py
|
+-- frontend/
|   +-- package.json           # React dependencies (yarn)
|   +-- tailwind.config.js     # Tailwind + Shadcn theme
|   +-- .env                   # REACT_APP_BACKEND_URL
|   +-- src/
|       +-- App.js             # Routes, HelmetProvider, Layout wrapper
|       +-- index.js            # React entry point
|       +-- index.css          # Global styles, TipTap content styles, CSS variables
|       +-- App.css
|       +-- contexts/
|       |   +-- AuthContext.js  # JWT auth state management
|       +-- components/
|       |   +-- Header.js       # Main navigation with categories dropdown
|       |   +-- Footer.js       # Site footer
|       |   +-- TickerStrip.js  # Scrolling market prices
|       |   +-- ArticleCard.js  # Hero, Secondary, Compact card variants
|       |   +-- Sidebar.js      # Trending articles widget
|       |   +-- TipTapEditor.js # WYSIWYG editor with full toolbar
|       |   +-- ui/            # Shadcn/UI components (50+ files)
|       +-- pages/
|       |   +-- HomePage.js     # Sectioned news homepage
|       |   +-- ArticlePage.js  # Full article with OG tags
|       |   +-- LatestNewsPage.js
|       |   +-- EducationPage.js
|       |   +-- AboutPage.js
|       |   +-- SearchPage.js
|       |   +-- LegalPage.js
|       |   +-- AuthorProfile.js
|       |   +-- admin/
|       |       +-- AdminDashboard.js
|       |       +-- AdminLogin.js
|       |       +-- ArticleEditor.js   # TipTap + scheduling + categories
|       |       +-- ArticlesList.js
|       |       +-- CategoriesManager.js
|       |       +-- HomepageCuration.js
|       |       +-- UsersManager.js
|       |       +-- AdminProfile.js
|       +-- hooks/
|       |   +-- use-toast.js
|       +-- lib/
|           +-- utils.js
|
+-- memory/
    +-- PRD.md
    +-- test_credentials.md
""")

# ═══════════════════════════════════════════════════════════
# 16. DEPLOYMENT GUIDE
# ═══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("16. Deployment Guide")

pdf.section_title("Environment Variables Required", 2)
pdf.section_title("Backend (.env)", 3)
env_vars = [
    ("MONGO_URL", "MongoDB connection string"),
    ("DB_NAME", "Database name"),
    ("JWT_SECRET", "Secret key for JWT signing"),
    ("ADMIN_EMAIL", "Default admin email (seeded on startup)"),
    ("ADMIN_PASSWORD", "Default admin password"),
    ("EMERGENT_LLM_KEY", "Key for object storage integration"),
    ("SITE_URL", "Public site URL (for sitemap generation)"),
]
widths = [50, 140]
pdf.table_row(["Variable", "Description"], widths, bold=True, fill=True)
for v, d in env_vars:
    pdf.table_row([v, d], widths)

pdf.ln(3)
pdf.section_title("Frontend (.env)", 3)
pdf.table_row(["Variable", "Description"], widths, bold=True, fill=True)
pdf.table_row(["REACT_APP_BACKEND_URL", "Backend API base URL (no trailing slash)"], widths)

pdf.ln(3)
pdf.section_title("Startup Sequence", 2)
pdf.body_text("On backend startup, the following happens automatically:")
pdf.bullet("1. MongoDB connection established via Motor")
pdf.bullet("2. Email unique index created on users collection")
pdf.bullet("3. Admin user seeded (created or updated to ensure super_admin role)")
pdf.bullet("4. Sample data seeded if collections are empty (categories, tags, articles, pages)")
pdf.bullet("5. Object storage initialized (deferred if unavailable)")

pdf.section_title("Build & Run", 2)
pdf.section_title("Backend", 3)
pdf.code_block("""
cd backend
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001
""")
pdf.section_title("Frontend", 3)
pdf.code_block("""
cd frontend
yarn install
yarn start    # Development (port 3000)
yarn build    # Production build
""")

# ═══════════════════════════════════════════════════════════
# 17. FUTURE ROADMAP
# ═══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("17. Future Roadmap")

pdf.section_title("P2 - Next Phase", 2)
pdf.bullet("Article revision history with diff comparison")
pdf.bullet("RSS feed generation")
pdf.bullet("Multi-author collaboration workflow")

pdf.section_title("P3 - Future Enhancements", 2)
pdf.bullet("Public commenting system with moderation")
pdf.bullet("Newsletter subscription and email digest")
pdf.bullet("Analytics dashboard (pageviews, popular articles, user engagement)")
pdf.bullet("Ad slot management for monetization")
pdf.bullet("Multi-factor authentication (MFA) for admin accounts")
pdf.bullet("IP allowlisting for admin panel access")
pdf.bullet("Trending articles section powered by view counts")
pdf.bullet("Social sharing buttons with share count tracking")
pdf.bullet("Article bookmarking for registered users")
pdf.bullet("Push notifications for breaking news")

pdf.ln(10)
pdf.set_draw_color(212, 175, 55)
pdf.line(10, pdf.get_y(), 200, pdf.get_y())
pdf.ln(8)
pdf.set_font("Helvetica", "I", 11)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 8, "End of Blueprint Document", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, "FinNews v3.0 - April 2026", align="C", new_x="LMARGIN", new_y="NEXT")

# Save
output_path = "/app/FinNews_Technical_Blueprint.pdf"
pdf.output(output_path)
print(f"PDF saved to {output_path}")
print(f"Pages: {pdf.pages_count}")
