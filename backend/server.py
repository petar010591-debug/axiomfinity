from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends, Query
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import logging
import bcrypt
import jwt
import httpx
import secrets
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field
from typing import List, Optional
from slugify import slugify

# Config
JWT_ALGORITHM = "HS256"
JWT_SECRET = os.environ["JWT_SECRET"]
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

# MongoDB
mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

app = FastAPI()
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ─── CORS ───
frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── PASSWORD HELPERS ───
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

# ─── JWT HELPERS ───
def create_access_token(user_id: str, email: str, role: str) -> str:
    payload = {"sub": user_id, "email": email, "role": role, "exp": datetime.now(timezone.utc) + timedelta(hours=24), "type": "access"}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    payload = {"sub": user_id, "exp": datetime.now(timezone.utc) + timedelta(days=7), "type": "refresh"}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# ─── AUTH DEPENDENCY ───
async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return {"id": str(user["_id"]), "email": user["email"], "name": user["name"], "role": user["role"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def serialize_doc(doc):
    if doc is None:
        return None
    doc["id"] = str(doc.pop("_id"))
    return doc

def serialize_list(docs):
    return [serialize_doc(d) for d in docs]

# ─── PYDANTIC MODELS ───
class LoginRequest(BaseModel):
    email: str
    password: str

class ArticleCreate(BaseModel):
    title: str
    excerpt: Optional[str] = ""
    content: str = ""
    featured_image: Optional[str] = ""
    category_id: Optional[str] = ""
    tags: List[str] = []
    status: str = "draft"
    is_sponsored: bool = False
    meta_title: Optional[str] = ""
    meta_description: Optional[str] = ""

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = ""

class TagCreate(BaseModel):
    name: str

class PageCreate(BaseModel):
    title: str
    slug: Optional[str] = ""
    content: str = ""
    page_type: str = "educational"

class HomepageSlotsUpdate(BaseModel):
    hero_primary: Optional[str] = None
    hero_secondary: List[str] = []

class ContactMessage(BaseModel):
    name: str
    email: str
    subject: str = ""
    message: str

# ─── AUTH ROUTES ───
@api_router.post("/auth/login")
async def login(req: LoginRequest, response: Response):
    email = req.email.strip().lower()
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    uid = str(user["_id"])
    access = create_access_token(uid, email, user["role"])
    refresh = create_refresh_token(uid)
    response.set_cookie(key="access_token", value=access, httponly=True, secure=False, samesite="lax", max_age=86400, path="/")
    response.set_cookie(key="refresh_token", value=refresh, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")
    return {"id": uid, "email": user["email"], "name": user["name"], "role": user["role"], "token": access}

@api_router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"message": "Logged out"}

@api_router.get("/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    return user

# ─── PUBLIC ARTICLE ROUTES ───
@api_router.get("/articles")
async def get_articles(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=50),
    status: Optional[str] = "published"
):
    query = {}
    if status:
        query["status"] = status
    if category:
        query["category_slug"] = category
    if tag:
        query["tags"] = tag
    skip = (page - 1) * limit
    total = await db.articles.count_documents(query)
    articles = await db.articles.find(query, {"_id": 1, "title": 1, "slug": 1, "excerpt": 1, "featured_image": 1, "category_name": 1, "category_slug": 1, "author_name": 1, "tags": 1, "status": 1, "is_sponsored": 1, "published_at": 1, "created_at": 1}).sort("published_at", -1).skip(skip).limit(limit).to_list(limit)
    return {"articles": serialize_list(articles), "total": total, "page": page, "pages": (total + limit - 1) // limit}

@api_router.get("/articles/featured")
async def get_featured():
    slots = await db.homepage_slots.find_one({"_id": "config"}, {"_id": 0})
    if not slots:
        articles = await db.articles.find({"status": "published"}).sort("published_at", -1).limit(5).to_list(5)
        result = serialize_list(articles)
        return {"hero_primary": result[0] if result else None, "hero_secondary": result[1:5]}
    hero_primary = None
    hero_secondary = []
    if slots.get("hero_primary"):
        try:
            doc = await db.articles.find_one({"_id": ObjectId(slots["hero_primary"]), "status": "published"})
            if doc:
                hero_primary = serialize_doc(doc)
        except Exception:
            pass
    for aid in slots.get("hero_secondary", []):
        try:
            doc = await db.articles.find_one({"_id": ObjectId(aid), "status": "published"})
            if doc:
                hero_secondary.append(serialize_doc(doc))
        except Exception:
            pass
    if not hero_primary:
        articles = await db.articles.find({"status": "published"}).sort("published_at", -1).limit(1).to_list(1)
        if articles:
            hero_primary = serialize_doc(articles[0])
    if len(hero_secondary) < 2:
        exclude_ids = []
        if hero_primary:
            exclude_ids.append(ObjectId(hero_primary["id"]))
        for s in hero_secondary:
            exclude_ids.append(ObjectId(s["id"]))
        more = await db.articles.find({"status": "published", "_id": {"$nin": exclude_ids}}).sort("published_at", -1).limit(4 - len(hero_secondary)).to_list(4)
        hero_secondary.extend(serialize_list(more))
    return {"hero_primary": hero_primary, "hero_secondary": hero_secondary}

@api_router.get("/articles/by-slug/{slug}")
async def get_article_by_slug(slug: str):
    article = await db.articles.find_one({"slug": slug, "status": "published"})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    result = serialize_doc(article)
    # Get related articles
    related_query = {"status": "published", "slug": {"$ne": slug}}
    if result.get("category_slug"):
        related_query["category_slug"] = result["category_slug"]
    related = await db.articles.find(related_query).sort("published_at", -1).limit(3).to_list(3)
    result["related"] = serialize_list(related)
    return result

@api_router.get("/articles/search")
async def search_articles(q: str = Query("", min_length=1), page: int = 1, limit: int = 12):
    if not q.strip():
        return {"articles": [], "total": 0, "page": 1, "pages": 0}
    query = {"status": "published", "$or": [
        {"title": {"$regex": q, "$options": "i"}},
        {"excerpt": {"$regex": q, "$options": "i"}},
        {"content": {"$regex": q, "$options": "i"}},
        {"tags": {"$regex": q, "$options": "i"}},
    ]}
    skip = (page - 1) * limit
    total = await db.articles.count_documents(query)
    articles = await db.articles.find(query, {"content": 0}).sort("published_at", -1).skip(skip).limit(limit).to_list(limit)
    return {"articles": serialize_list(articles), "total": total, "page": page, "pages": (total + limit - 1) // limit}

# ─── PUBLIC CATEGORY / TAG ROUTES ───
@api_router.get("/categories")
async def get_categories():
    cats = await db.categories.find({}, {"_id": 1, "name": 1, "slug": 1, "description": 1}).to_list(100)
    return serialize_list(cats)

@api_router.get("/tags")
async def get_tags():
    tags = await db.tags.find({}, {"_id": 1, "name": 1, "slug": 1}).to_list(200)
    return serialize_list(tags)

# ─── PUBLIC PAGES ───
@api_router.get("/pages")
async def get_pages(page_type: Optional[str] = None):
    query = {}
    if page_type:
        query["page_type"] = page_type
    pages = await db.pages.find(query).to_list(100)
    return serialize_list(pages)

@api_router.get("/pages/{slug}")
async def get_page_by_slug(slug: str):
    page = await db.pages.find_one({"slug": slug})
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return serialize_doc(page)

# ─── CONTACT ───
@api_router.post("/contact")
async def submit_contact(msg: ContactMessage):
    doc = msg.model_dump()
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    await db.contact_messages.insert_one(doc)
    return {"message": "Thank you for your message. We'll get back to you soon."}

# ─── MARKET TICKER ───
@api_router.get("/market/ticker")
async def market_ticker():
    FALLBACK_TICKERS = [
        {"symbol": "BTC", "price": 97542.00, "change_24h": 2.34},
        {"symbol": "ETH", "price": 3845.00, "change_24h": 1.87},
        {"symbol": "SOL", "price": 178.50, "change_24h": -0.45},
        {"symbol": "DOGE", "price": 0.1823, "change_24h": 3.12},
        {"symbol": "ADA", "price": 0.6542, "change_24h": -1.23},
        {"symbol": "XRP", "price": 2.15, "change_24h": 0.98},
        {"symbol": "DOT", "price": 7.85, "change_24h": -0.67},
        {"symbol": "AVAX", "price": 35.20, "change_24h": 1.45},
    ]
    try:
        async with httpx.AsyncClient(timeout=10) as hclient:
            resp = await hclient.get("https://api.coingecko.com/api/v3/simple/price", params={
                "ids": "bitcoin,ethereum,solana,dogecoin,cardano,ripple,polkadot,avalanche-2",
                "vs_currencies": "usd",
                "include_24hr_change": "true"
            })
            if resp.status_code == 200:
                data = resp.json()
                tickers = []
                names = {"bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL", "dogecoin": "DOGE", "cardano": "ADA", "ripple": "XRP", "polkadot": "DOT", "avalanche-2": "AVAX"}
                for cid, symbol in names.items():
                    if cid in data:
                        tickers.append({
                            "symbol": symbol,
                            "price": data[cid].get("usd", 0),
                            "change_24h": round(data[cid].get("usd_24h_change", 0), 2)
                        })
                if tickers:
                    return {"tickers": tickers, "updated_at": datetime.now(timezone.utc).isoformat()}
            return {"tickers": FALLBACK_TICKERS, "updated_at": datetime.now(timezone.utc).isoformat(), "note": "Using cached data"}
    except Exception as e:
        logger.error(f"Ticker fetch error: {e}")
        return {"tickers": FALLBACK_TICKERS, "updated_at": datetime.now(timezone.utc).isoformat(), "note": "Using cached data"}

# ─── ADMIN ROUTES ───
@api_router.get("/admin/articles")
async def admin_list_articles(user: dict = Depends(get_current_user), page: int = 1, limit: int = 20, status: Optional[str] = None):
    query = {}
    if status:
        query["status"] = status
    skip = (page - 1) * limit
    total = await db.articles.count_documents(query)
    articles = await db.articles.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return {"articles": serialize_list(articles), "total": total, "page": page, "pages": (total + limit - 1) // limit}

@api_router.get("/admin/articles/{article_id}")
async def admin_get_article(article_id: str, user: dict = Depends(get_current_user)):
    article = await db.articles.find_one({"_id": ObjectId(article_id)})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return serialize_doc(article)

@api_router.post("/admin/articles")
async def admin_create_article(data: ArticleCreate, user: dict = Depends(get_current_user)):
    slug = slugify(data.title)
    existing = await db.articles.find_one({"slug": slug})
    if existing:
        slug = f"{slug}-{secrets.token_hex(3)}"
    cat_name = ""
    cat_slug = ""
    if data.category_id:
        try:
            cat = await db.categories.find_one({"_id": ObjectId(data.category_id)})
            if cat:
                cat_name = cat["name"]
                cat_slug = cat["slug"]
        except Exception:
            pass
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "title": data.title,
        "slug": slug,
        "excerpt": data.excerpt,
        "content": data.content,
        "featured_image": data.featured_image,
        "category_id": data.category_id,
        "category_name": cat_name,
        "category_slug": cat_slug,
        "tags": data.tags,
        "author_id": user["id"],
        "author_name": user["name"],
        "status": data.status,
        "is_sponsored": data.is_sponsored,
        "published_at": now if data.status == "published" else None,
        "meta_title": data.meta_title or data.title,
        "meta_description": data.meta_description or data.excerpt,
        "created_at": now,
        "updated_at": now,
    }
    result = await db.articles.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc.pop("_id", None)
    return doc

@api_router.put("/admin/articles/{article_id}")
async def admin_update_article(article_id: str, data: ArticleCreate, user: dict = Depends(get_current_user)):
    existing = await db.articles.find_one({"_id": ObjectId(article_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Article not found")
    cat_name = ""
    cat_slug = ""
    if data.category_id:
        try:
            cat = await db.categories.find_one({"_id": ObjectId(data.category_id)})
            if cat:
                cat_name = cat["name"]
                cat_slug = cat["slug"]
        except Exception:
            pass
    now = datetime.now(timezone.utc).isoformat()
    update = {
        "title": data.title,
        "excerpt": data.excerpt,
        "content": data.content,
        "featured_image": data.featured_image,
        "category_id": data.category_id,
        "category_name": cat_name,
        "category_slug": cat_slug,
        "tags": data.tags,
        "status": data.status,
        "is_sponsored": data.is_sponsored,
        "meta_title": data.meta_title or data.title,
        "meta_description": data.meta_description or data.excerpt,
        "updated_at": now,
    }
    if data.status == "published" and existing.get("status") != "published":
        update["published_at"] = now
    # Update slug only if title changed
    if data.title != existing.get("title"):
        new_slug = slugify(data.title)
        dup = await db.articles.find_one({"slug": new_slug, "_id": {"$ne": ObjectId(article_id)}})
        if dup:
            new_slug = f"{new_slug}-{secrets.token_hex(3)}"
        update["slug"] = new_slug
    await db.articles.update_one({"_id": ObjectId(article_id)}, {"$set": update})
    updated = await db.articles.find_one({"_id": ObjectId(article_id)})
    return serialize_doc(updated)

@api_router.delete("/admin/articles/{article_id}")
async def admin_delete_article(article_id: str, user: dict = Depends(get_current_user)):
    result = await db.articles.delete_one({"_id": ObjectId(article_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"message": "Article deleted"}

# ─── ADMIN CATEGORIES ───
@api_router.post("/admin/categories")
async def admin_create_category(data: CategoryCreate, user: dict = Depends(get_current_user)):
    slug = slugify(data.name)
    existing = await db.categories.find_one({"slug": slug})
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    doc = {"name": data.name, "slug": slug, "description": data.description, "created_at": datetime.now(timezone.utc).isoformat()}
    result = await db.categories.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc.pop("_id", None)
    return doc

@api_router.put("/admin/categories/{cat_id}")
async def admin_update_category(cat_id: str, data: CategoryCreate, user: dict = Depends(get_current_user)):
    slug = slugify(data.name)
    await db.categories.update_one({"_id": ObjectId(cat_id)}, {"$set": {"name": data.name, "slug": slug, "description": data.description}})
    # Update category name/slug in all articles
    await db.articles.update_many({"category_id": cat_id}, {"$set": {"category_name": data.name, "category_slug": slug}})
    updated = await db.categories.find_one({"_id": ObjectId(cat_id)})
    return serialize_doc(updated)

@api_router.delete("/admin/categories/{cat_id}")
async def admin_delete_category(cat_id: str, user: dict = Depends(get_current_user)):
    await db.categories.delete_one({"_id": ObjectId(cat_id)})
    return {"message": "Category deleted"}

# ─── ADMIN TAGS ───
@api_router.post("/admin/tags")
async def admin_create_tag(data: TagCreate, user: dict = Depends(get_current_user)):
    slug = slugify(data.name)
    existing = await db.tags.find_one({"slug": slug})
    if existing:
        raise HTTPException(status_code=400, detail="Tag already exists")
    doc = {"name": data.name, "slug": slug, "created_at": datetime.now(timezone.utc).isoformat()}
    result = await db.tags.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc.pop("_id", None)
    return doc

@api_router.delete("/admin/tags/{tag_id}")
async def admin_delete_tag(tag_id: str, user: dict = Depends(get_current_user)):
    await db.tags.delete_one({"_id": ObjectId(tag_id)})
    return {"message": "Tag deleted"}

# ─── ADMIN PAGES ───
@api_router.post("/admin/pages")
async def admin_create_page(data: PageCreate, user: dict = Depends(get_current_user)):
    slug = data.slug or slugify(data.title)
    now = datetime.now(timezone.utc).isoformat()
    doc = {"title": data.title, "slug": slug, "content": data.content, "page_type": data.page_type, "created_at": now, "updated_at": now}
    result = await db.pages.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc.pop("_id", None)
    return doc

@api_router.put("/admin/pages/{page_id}")
async def admin_update_page(page_id: str, data: PageCreate, user: dict = Depends(get_current_user)):
    now = datetime.now(timezone.utc).isoformat()
    update = {"title": data.title, "content": data.content, "page_type": data.page_type, "updated_at": now}
    if data.slug:
        update["slug"] = data.slug
    await db.pages.update_one({"_id": ObjectId(page_id)}, {"$set": update})
    updated = await db.pages.find_one({"_id": ObjectId(page_id)})
    return serialize_doc(updated)

@api_router.delete("/admin/pages/{page_id}")
async def admin_delete_page(page_id: str, user: dict = Depends(get_current_user)):
    await db.pages.delete_one({"_id": ObjectId(page_id)})
    return {"message": "Page deleted"}

# ─── ADMIN HOMEPAGE CURATION ───
@api_router.get("/admin/homepage")
async def admin_get_homepage(user: dict = Depends(get_current_user)):
    slots = await db.homepage_slots.find_one({"_id": "config"})
    if not slots:
        return {"hero_primary": None, "hero_secondary": []}
    return {"hero_primary": slots.get("hero_primary"), "hero_secondary": slots.get("hero_secondary", [])}

@api_router.put("/admin/homepage")
async def admin_update_homepage(data: HomepageSlotsUpdate, user: dict = Depends(get_current_user)):
    await db.homepage_slots.update_one({"_id": "config"}, {"$set": {"hero_primary": data.hero_primary, "hero_secondary": data.hero_secondary}}, upsert=True)
    return {"message": "Homepage updated"}

# ─── ADMIN DASHBOARD STATS ───
@api_router.get("/admin/stats")
async def admin_stats(user: dict = Depends(get_current_user)):
    total_articles = await db.articles.count_documents({})
    published = await db.articles.count_documents({"status": "published"})
    drafts = await db.articles.count_documents({"status": "draft"})
    categories = await db.categories.count_documents({})
    tags = await db.tags.count_documents({})
    pages = await db.pages.count_documents({})
    return {"total_articles": total_articles, "published": published, "drafts": drafts, "categories": categories, "tags": tags, "pages": pages}

# ─── INCLUDE ROUTER ───
app.include_router(api_router)

# ─── SEED DATA ───
SAMPLE_CATEGORIES = [
    {"name": "Crypto", "slug": "crypto", "description": "Cryptocurrency news and analysis"},
    {"name": "Markets", "slug": "markets", "description": "Stock market and traditional finance"},
    {"name": "DeFi", "slug": "defi", "description": "Decentralized finance protocols and trends"},
    {"name": "Analysis", "slug": "analysis", "description": "Deep dives and technical analysis"},
    {"name": "Regulation", "slug": "regulation", "description": "Government policy and regulatory updates"},
]

SAMPLE_TAGS = [
    {"name": "Bitcoin", "slug": "bitcoin"},
    {"name": "Ethereum", "slug": "ethereum"},
    {"name": "Altcoins", "slug": "altcoins"},
    {"name": "Trading", "slug": "trading"},
    {"name": "Blockchain", "slug": "blockchain"},
    {"name": "NFT", "slug": "nft"},
    {"name": "Web3", "slug": "web3"},
    {"name": "Stablecoins", "slug": "stablecoins"},
]

SAMPLE_ARTICLES = [
    {
        "title": "Bitcoin Surges Past $100K as Institutional Demand Hits New Highs",
        "slug": "bitcoin-surges-past-100k-institutional-demand",
        "excerpt": "Bitcoin has broken through the $100,000 barrier as major financial institutions increase their cryptocurrency holdings, signaling a new era of mainstream adoption.",
        "content": "<h2>A Historic Milestone</h2><p>Bitcoin reached a historic milestone today, surging past the $100,000 mark for the first time as institutional investors continue to pour capital into the cryptocurrency market. The move represents a significant psychological breakthrough for the world's largest digital asset.</p><h2>Institutional Momentum</h2><p>Major banks and asset managers have been steadily increasing their Bitcoin allocations throughout 2026, driven by growing client demand and clearer regulatory frameworks. BlackRock's spot Bitcoin ETF has accumulated over $50 billion in assets under management, while several sovereign wealth funds have disclosed Bitcoin positions for the first time.</p><h2>Market Analysis</h2><p>Technical analysts point to strong support levels and increasing on-chain activity as indicators of sustained bullish momentum. The current rally differs from previous cycles in its foundation of institutional infrastructure and regulatory clarity.</p><p>\"This isn't just retail speculation anymore,\" said Sarah Chen, Chief Investment Officer at Digital Asset Capital. \"We're seeing pension funds, endowments, and family offices all making strategic allocations to Bitcoin.\"</p><h2>What's Next?</h2><p>While some analysts warn of potential short-term pullbacks, the consensus view remains bullish. The combination of limited supply, increasing demand, and supportive macroeconomic conditions suggests further upside potential.</p>",
        "featured_image": "https://images.unsplash.com/photo-1643962579399-705ba9e9cc0b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1NzB8MHwxfHNlYXJjaHwxfHxiaXRjb2luJTIwc3RvY2slMjBtYXJrZXQlMjBkYXJrfGVufDB8fHx8MTc3NTA1ODUwNXww&ixlib=rb-4.1.0&q=85",
        "category_slug": "crypto",
        "category_name": "Crypto",
        "tags": ["Bitcoin", "Trading"],
        "is_sponsored": False,
    },
    {
        "title": "Ethereum's Layer 2 Ecosystem Reaches $50B in Total Value Locked",
        "slug": "ethereum-layer-2-ecosystem-50b-tvl",
        "excerpt": "The combined total value locked across Ethereum Layer 2 networks has surpassed $50 billion, highlighting the growing scalability of the Ethereum ecosystem.",
        "content": "<h2>Scaling Milestone</h2><p>Ethereum's Layer 2 ecosystem has achieved a remarkable milestone, with combined total value locked (TVL) surpassing $50 billion across various rollup networks. This represents a 300% increase from the beginning of the year.</p><h2>Leading Networks</h2><p>Arbitrum and Optimism continue to lead the pack, with Base gaining significant ground thanks to its integration with Coinbase's user base. ZK-rollups including zkSync and StarkNet are also seeing rapid adoption as their technology matures.</p><p>The growth in L2 activity has contributed to a significant reduction in mainnet gas fees, making Ethereum more accessible to everyday users while maintaining the security guarantees of the base layer.</p><h2>DeFi Renaissance</h2><p>The lower costs and faster transactions on L2 networks have sparked a renaissance in DeFi applications, with new protocols launching daily across lending, trading, and yield optimization categories.</p>",
        "featured_image": "https://static.prod-images.emergentagent.com/jobs/0356c6e3-d9fe-4e34-b671-3b8a5d7d214f/images/a93bc06ad761fa1cee1bcc03f9f82eb5ffb38dddbd06acdd028acf9e70b95a52.png",
        "category_slug": "defi",
        "category_name": "DeFi",
        "tags": ["Ethereum", "Blockchain"],
        "is_sponsored": False,
    },
    {
        "title": "SEC Approves Comprehensive Crypto Regulatory Framework",
        "slug": "sec-approves-comprehensive-crypto-framework",
        "excerpt": "The SEC has voted to approve a comprehensive regulatory framework for digital assets, providing long-awaited clarity for the cryptocurrency industry.",
        "content": "<h2>Regulatory Clarity at Last</h2><p>In a landmark decision, the U.S. Securities and Exchange Commission has approved a comprehensive regulatory framework for digital assets. The new rules provide clear guidelines for token classification, exchange operations, and investor protections.</p><h2>Key Provisions</h2><p>The framework establishes a clear taxonomy for digital assets, distinguishing between securities, commodities, and utility tokens. Exchanges will be required to register under a new licensing regime that addresses the unique characteristics of crypto markets.</p><p>\"This framework strikes the right balance between protecting investors and fostering innovation,\" said SEC Chair in the official announcement. \"It provides the certainty that the industry has been seeking.\"</p><h2>Industry Reaction</h2><p>The crypto industry has largely welcomed the new rules, with major exchanges and projects expressing support for the clarity they provide. Several international jurisdictions have indicated interest in adopting similar frameworks.</p>",
        "featured_image": "https://images.pexels.com/photos/10628030/pexels-photo-10628030.png?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "category_slug": "regulation",
        "category_name": "Regulation",
        "tags": ["Bitcoin", "Ethereum", "Altcoins"],
        "is_sponsored": False,
    },
    {
        "title": "Solana DeFi Sees Record Volume as New Protocols Launch",
        "slug": "solana-defi-record-volume-new-protocols",
        "excerpt": "Solana's DeFi ecosystem is experiencing unprecedented growth with record trading volumes and a wave of innovative new protocols.",
        "content": "<h2>Explosive Growth</h2><p>Solana's decentralized finance ecosystem has recorded its highest-ever daily trading volume, driven by a surge in activity across multiple protocols. The network processed over 50 million transactions in a single day without significant performance degradation.</p><h2>New Protocol Launches</h2><p>Several high-profile DeFi protocols have launched on Solana in recent weeks, including advanced perpetual trading platforms, cross-chain bridges, and novel yield farming strategies. The combination of low fees and high throughput continues to attract builders.</p><p>Market makers and institutional trading firms have increasingly deployed strategies on Solana, citing its performance characteristics and growing liquidity.</p><h2>Technical Improvements</h2><p>Recent network upgrades have significantly improved Solana's reliability, addressing concerns that previously limited institutional adoption. The Firedancer validator client has contributed to network stability and throughput improvements.</p>",
        "featured_image": "https://static.prod-images.emergentagent.com/jobs/0356c6e3-d9fe-4e34-b671-3b8a5d7d214f/images/49f82beb8b9fd6e716ec4539493ca67d272193ac046693ecbaf6ba88c533d0a8.png",
        "category_slug": "defi",
        "category_name": "DeFi",
        "tags": ["Altcoins", "Trading"],
        "is_sponsored": False,
    },
    {
        "title": "Central Banks Accelerate Digital Currency Development in 2026",
        "slug": "central-banks-accelerate-digital-currency-2026",
        "excerpt": "More than 130 countries are now actively developing central bank digital currencies, with several major economies preparing for pilot launches.",
        "content": "<h2>Global CBDC Race</h2><p>The race to develop central bank digital currencies (CBDCs) has accelerated dramatically in 2026, with over 130 countries in various stages of research, development, or pilot testing. The European Central Bank, Bank of England, and Federal Reserve have all announced advanced pilot programs.</p><h2>Privacy Considerations</h2><p>Privacy remains the most debated aspect of CBDC design. Several central banks have adopted hybrid models that provide transaction privacy for small amounts while maintaining regulatory visibility for larger transfers.</p><p>\"The key challenge is designing a system that serves both the public interest and individual privacy rights,\" noted Dr. Maria Torres, a CBDC researcher at the Bank for International Settlements.</p><h2>Impact on Crypto</h2><p>The relationship between CBDCs and existing cryptocurrencies continues to evolve. Some analysts argue that CBDCs will legitimize the broader digital asset ecosystem, while others warn of potential competitive pressures on stablecoins.</p>",
        "featured_image": "https://images.unsplash.com/photo-1732111816779-aeec50f788ba?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1NzB8MHwxfHNlYXJjaHw0fHxiaXRjb2luJTIwc3RvY2slMjBtYXJrZXQlMjBkYXJrfGVufDB8fHx8MTc3NTA1ODUwNXww&ixlib=rb-4.1.0&q=85",
        "category_slug": "regulation",
        "category_name": "Regulation",
        "tags": ["Blockchain", "Stablecoins"],
        "is_sponsored": False,
    },
    {
        "title": "Technical Analysis: Key Support Levels to Watch This Week",
        "slug": "technical-analysis-key-support-levels-week",
        "excerpt": "Our weekly technical analysis covers critical support and resistance levels for Bitcoin, Ethereum, and top altcoins heading into a pivotal trading week.",
        "content": "<h2>Weekly Market Overview</h2><p>The crypto market enters a pivotal week with several key technical levels in focus. After a period of consolidation, multiple assets are approaching critical support and resistance zones that could determine the next major directional move.</p><h2>Bitcoin (BTC)</h2><p>Bitcoin continues to trade within a narrowing range between $98,000 and $103,000. The 50-day moving average at $96,500 represents strong support, while a break above $103,000 could trigger a move toward $110,000. Volume has been declining during consolidation, suggesting a significant move is imminent.</p><h2>Ethereum (ETH)</h2><p>Ethereum has shown relative strength, maintaining its position above the key $4,200 support level. The ETH/BTC ratio has been trending upward, suggesting potential outperformance in the near term. Watch the $4,500 resistance for a potential breakout signal.</p><h2>Altcoin Outlook</h2><p>Several altcoins are forming bullish technical patterns. Solana, Avalanche, and Polkadot all show constructive chart structures with potential for significant upside if Bitcoin maintains its current range.</p>",
        "featured_image": "https://static.prod-images.emergentagent.com/jobs/0356c6e3-d9fe-4e34-b671-3b8a5d7d214f/images/f712192f1e093a330071590147681b698bb15be3b4c11acf87b28c9958efedf3.png",
        "category_slug": "analysis",
        "category_name": "Analysis",
        "tags": ["Bitcoin", "Ethereum", "Trading"],
        "is_sponsored": False,
    },
    {
        "title": "Understanding DeFi Yield Farming: A Beginner's Guide",
        "slug": "understanding-defi-yield-farming-beginners-guide",
        "excerpt": "Learn the fundamentals of DeFi yield farming, including how it works, the risks involved, and strategies for getting started safely.",
        "content": "<h2>What is Yield Farming?</h2><p>Yield farming is a method of earning rewards by providing liquidity to decentralized finance protocols. By depositing your crypto assets into liquidity pools, you earn fees and token rewards from the protocol.</p><h2>How Does It Work?</h2><p>When you provide liquidity to a DeFi protocol, you're essentially lending your assets to be used by other traders. In return, you receive a share of the trading fees and often additional token incentives. The annual percentage yield (APY) can vary significantly depending on the protocol and the assets involved.</p><h2>Key Risks</h2><p><strong>Impermanent Loss:</strong> When the price ratio of your deposited assets changes, you may end up with less value than if you had simply held the assets. This is the most common risk in yield farming.</p><p><strong>Smart Contract Risk:</strong> DeFi protocols are built on smart contracts that may contain bugs or vulnerabilities. Always use well-audited protocols.</p><p><strong>Regulatory Risk:</strong> The regulatory landscape for DeFi is still evolving, which could impact the availability of certain protocols.</p><h2>Getting Started Safely</h2><p>Start with well-established protocols like Aave, Compound, or Uniswap. Begin with small amounts to understand the mechanics before committing larger sums. Always research the protocol's audit history and team background.</p>",
        "featured_image": "https://static.prod-images.emergentagent.com/jobs/0356c6e3-d9fe-4e34-b671-3b8a5d7d214f/images/a93bc06ad761fa1cee1bcc03f9f82eb5ffb38dddbd06acdd028acf9e70b95a52.png",
        "category_slug": "defi",
        "category_name": "DeFi",
        "tags": ["Blockchain", "Web3"],
        "is_sponsored": False,
    },
    {
        "title": "Global Stock Markets Rally on Positive Economic Data",
        "slug": "global-stock-markets-rally-positive-economic-data",
        "excerpt": "Major stock indices around the world posted gains as economic data exceeded expectations, boosting investor confidence across all asset classes.",
        "content": "<h2>Markets Surge</h2><p>Global stock markets rallied broadly today following the release of stronger-than-expected economic data from the United States, Europe, and Asia. The S&P 500 rose 2.1%, while the Nasdaq Composite gained 2.8%.</p><h2>Economic Indicators</h2><p>U.S. jobs data came in well above consensus, with 350,000 new positions added in January. Manufacturing PMI data from Europe also surprised to the upside, suggesting that recession fears may have been overdone.</p><p>The positive economic backdrop has supported risk assets broadly, with both traditional equities and cryptocurrencies benefiting from improved sentiment.</p><h2>Crypto Correlation</h2><p>Bitcoin and Ethereum both posted gains in sympathy with traditional markets, highlighting the increasing correlation between digital assets and broader financial markets during risk-on periods.</p>",
        "featured_image": "https://images.pexels.com/photos/10628030/pexels-photo-10628030.png?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "category_slug": "markets",
        "category_name": "Markets",
        "tags": ["Trading", "Bitcoin"],
        "is_sponsored": False,
    },
]

SAMPLE_PAGES = [
    {
        "title": "What is Blockchain Technology?",
        "slug": "what-is-blockchain",
        "page_type": "educational",
        "content": "<h2>Introduction to Blockchain</h2><p>Blockchain is a distributed ledger technology that enables secure, transparent, and immutable record-keeping without the need for a central authority. It forms the foundation of cryptocurrencies like Bitcoin and Ethereum, but its applications extend far beyond digital currencies.</p><h2>How Does It Work?</h2><p>A blockchain consists of a chain of blocks, each containing a set of transactions. When a new transaction occurs, it is broadcast to a network of computers (nodes) that validate the transaction using consensus mechanisms. Once validated, the transaction is added to a new block, which is then linked to the previous block, creating an unbreakable chain.</p><h2>Key Properties</h2><p><strong>Decentralization:</strong> No single entity controls the network.</p><p><strong>Immutability:</strong> Once recorded, data cannot be altered retroactively.</p><p><strong>Transparency:</strong> All transactions are visible to network participants.</p><p><strong>Security:</strong> Cryptographic techniques protect data integrity.</p>",
    },
    {
        "title": "Understanding Cryptocurrency Wallets",
        "slug": "understanding-crypto-wallets",
        "page_type": "educational",
        "content": "<h2>What is a Crypto Wallet?</h2><p>A cryptocurrency wallet is a tool that allows you to store, send, and receive digital currencies. Unlike traditional wallets, crypto wallets don't actually store your coins—they store the private keys that give you access to your assets on the blockchain.</p><h2>Types of Wallets</h2><p><strong>Hot Wallets:</strong> Connected to the internet. Convenient but more vulnerable. Examples: MetaMask, Trust Wallet.</p><p><strong>Cold Wallets:</strong> Offline storage. More secure for long-term holding. Examples: Ledger, Trezor.</p><p><strong>Paper Wallets:</strong> Physical printout of your keys. Very secure but inconvenient for regular use.</p><h2>Best Practices</h2><p>Never share your private keys or seed phrase. Use hardware wallets for large holdings. Enable two-factor authentication wherever possible. Keep backup copies of your seed phrase in secure locations.</p>",
    },
    {
        "title": "Privacy Policy",
        "slug": "privacy-policy",
        "page_type": "legal",
        "content": "<h2>Privacy Policy</h2><p>Last updated: February 2026</p><p>This Privacy Policy describes how we collect, use, and protect your personal information when you visit our website. We are committed to maintaining the privacy and security of your information.</p><h2>Information We Collect</h2><p>We may collect information that you provide directly, such as when you subscribe to our newsletter, submit a contact form, or create an account. We also collect certain technical information automatically, including browser type, IP address, and pages visited.</p><h2>How We Use Your Information</h2><p>We use your information to provide and improve our services, communicate with you, and comply with legal obligations. We do not sell your personal information to third parties.</p><h2>Contact Us</h2><p>If you have questions about this Privacy Policy, please contact us through our contact page.</p>",
    },
    {
        "title": "Terms and Conditions",
        "slug": "terms-and-conditions",
        "page_type": "legal",
        "content": "<h2>Terms and Conditions</h2><p>Last updated: February 2026</p><p>By accessing this website, you agree to be bound by these Terms and Conditions. If you do not agree with any part of these terms, you may not access the website.</p><h2>Content Disclaimer</h2><p>The content on this website is for informational purposes only and does not constitute financial advice. Always do your own research before making investment decisions.</p><h2>Intellectual Property</h2><p>All content on this website, including text, images, and graphics, is the property of our organization and is protected by copyright laws.</p>",
    },
    {
        "title": "Financial Disclaimer",
        "slug": "financial-disclaimer",
        "page_type": "legal",
        "content": "<h2>Financial Disclaimer</h2><p>The information provided on this website is for general informational and educational purposes only. It is not intended as, and should not be construed as, financial, investment, or trading advice.</p><h2>Risk Warning</h2><p>Cryptocurrency and other digital asset investments are highly volatile and carry significant risk. You could lose some or all of your invested capital. Past performance is not indicative of future results.</p><h2>Not Financial Advice</h2><p>Nothing on this website should be interpreted as a recommendation to buy, sell, or hold any investment. Always consult with a qualified financial advisor before making investment decisions.</p>",
    },
    {
        "title": "About Us",
        "slug": "about",
        "page_type": "about",
        "content": "<h2>About Our Mission</h2><p>We are a team of financial journalists, analysts, and blockchain enthusiasts dedicated to providing clear, accurate, and timely information about the rapidly evolving world of digital finance.</p><h2>What We Do</h2><p>Our editorial team covers the latest developments in cryptocurrency, decentralized finance, blockchain technology, and traditional financial markets. We believe in providing balanced, well-researched reporting that helps our readers make informed decisions.</p><h2>Our Values</h2><p><strong>Accuracy:</strong> We verify our information through multiple sources.</p><p><strong>Independence:</strong> Our editorial content is independent of advertisers and sponsors.</p><p><strong>Transparency:</strong> Sponsored content is always clearly labeled.</p><p><strong>Accessibility:</strong> We make complex financial topics understandable for everyone.</p>",
    },
]

async def seed_admin():
    existing = await db.users.find_one({"email": ADMIN_EMAIL.lower()})
    if existing is None:
        hashed = hash_password(ADMIN_PASSWORD)
        await db.users.insert_one({
            "email": ADMIN_EMAIL.lower(),
            "password_hash": hashed,
            "name": "Admin",
            "role": "admin",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        logger.info(f"Admin user created: {ADMIN_EMAIL}")
    elif not verify_password(ADMIN_PASSWORD, existing["password_hash"]):
        await db.users.update_one({"email": ADMIN_EMAIL.lower()}, {"$set": {"password_hash": hash_password(ADMIN_PASSWORD)}})
        logger.info("Admin password updated")

async def seed_data():
    # Seed categories
    if await db.categories.count_documents({}) == 0:
        for cat in SAMPLE_CATEGORIES:
            cat["created_at"] = datetime.now(timezone.utc).isoformat()
            await db.categories.insert_one(cat)
        logger.info("Categories seeded")

    # Seed tags
    if await db.tags.count_documents({}) == 0:
        for tag in SAMPLE_TAGS:
            tag["created_at"] = datetime.now(timezone.utc).isoformat()
            await db.tags.insert_one(tag)
        logger.info("Tags seeded")

    # Seed articles
    if await db.articles.count_documents({}) == 0:
        admin = await db.users.find_one({"role": "admin"})
        author_id = str(admin["_id"]) if admin else ""
        author_name = admin.get("name", "Admin") if admin else "Admin"
        now = datetime.now(timezone.utc)
        for i, article in enumerate(SAMPLE_ARTICLES):
            pub_time = (now - timedelta(hours=i * 6)).isoformat()
            cat = await db.categories.find_one({"slug": article["category_slug"]})
            article["category_id"] = str(cat["_id"]) if cat else ""
            article["author_id"] = author_id
            article["author_name"] = author_name
            article["status"] = "published"
            article["published_at"] = pub_time
            article["created_at"] = pub_time
            article["updated_at"] = pub_time
            article["meta_title"] = article["title"]
            article["meta_description"] = article["excerpt"]
            await db.articles.insert_one(article)
        logger.info("Articles seeded")

    # Seed pages
    if await db.pages.count_documents({}) == 0:
        now = datetime.now(timezone.utc).isoformat()
        for page in SAMPLE_PAGES:
            page["created_at"] = now
            page["updated_at"] = now
            await db.pages.insert_one(page)
        logger.info("Pages seeded")

@app.on_event("startup")
async def startup():
    await db.users.create_index("email", unique=True)
    await seed_admin()
    await seed_data()
    # Write test credentials
    os.makedirs("/app/memory", exist_ok=True)
    with open("/app/memory/test_credentials.md", "w") as f:
        f.write(f"# Test Credentials\n\n## Admin\n- Email: {ADMIN_EMAIL}\n- Password: {ADMIN_PASSWORD}\n- Role: admin\n\n## Auth Endpoints\n- POST /api/auth/login\n- POST /api/auth/logout\n- GET /api/auth/me\n")
    logger.info("Startup complete")

@app.on_event("shutdown")
async def shutdown():
    client.close()
