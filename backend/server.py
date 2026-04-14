from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends, Query, UploadFile, File, Body
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import logging
import bcrypt
import jwt
import httpx
import secrets
import uuid
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field
from typing import List, Optional
from slugify import slugify
import time

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
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
    payload = {"sub": user_id, "email": email, "role": role, "exp": datetime.now(timezone.utc) + timedelta(days=7), "type": "access"}
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

# ─── CLOUDINARY STORAGE ───
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_to_cloudinary(data: bytes, filename: str, content_type: str) -> str:
    result = cloudinary.uploader.upload(
        data,
        folder="finnews",
        public_id=filename.rsplit(".", 1)[0],
        resource_type="image"
    )
    return result["secure_url"]

# ─── RBAC ───
ROLES_HIERARCHY = {"super_admin": 4, "admin": 3, "editor": 2, "author": 1}

def require_role(*roles):
    async def check(request: Request):
        user = await get_current_user(request)
        if user["role"] not in roles and user["role"] != "super_admin":
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return Depends(check)

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
    secondary_categories: List[str] = []
    tags: List[str] = []
    status: str = "draft"
    is_sponsored: bool = False
    meta_title: Optional[str] = ""
    meta_description: Optional[str] = ""
    scheduled_at: Optional[str] = None
    og_image: Optional[str] = ""
    faqs: List[dict] = []  # [{question: str, answer: str}, ...]
    custom_slug: Optional[str] = ""

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = ""
    avatar_url: Optional[str] = ""
    social_twitter: Optional[str] = ""
    social_linkedin: Optional[str] = ""
    website: Optional[str] = ""

class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    role: str = "author"
    bio: Optional[str] = ""

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
    full_user = await db.users.find_one({"_id": ObjectId(user["id"])}, {"password_hash": 0})
    if full_user:
        return serialize_doc(full_user)
    return user

# Helper to build public article query (handles scheduled)
def build_public_query():
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {"$or": [
        {"status": "published"},
        {"status": "scheduled", "scheduled_at": {"$lte": now}}
    ]}


# Auto-promote scheduled articles whose time has passed
async def auto_promote_scheduled():
    now = datetime.now(timezone.utc)
    # 1. Revert incorrectly promoted articles (scheduled_at in the future but status=published with no real publish)
    future_scheduled = await db.articles.find(
        {"scheduled_at": {"$exists": True, "$ne": ""}, "status": "published"},
        {"_id": 1, "scheduled_at": 1, "published_at": 1}
    ).to_list(500)
    for art in future_scheduled:
        try:
            sched_str = str(art["scheduled_at"]).replace("Z", "+00:00")
            sched_dt = datetime.fromisoformat(sched_str)
            pub_at = art.get("published_at")
            # If scheduled_at is in the future AND published_at matches scheduled_at (set by old buggy code), revert
            if sched_dt > now and pub_at and str(pub_at) == str(art["scheduled_at"]):
                await db.articles.update_one(
                    {"_id": art["_id"]},
                    {"$set": {"status": "scheduled", "published_at": None}}
                )
        except Exception:
            continue
    # 2. Promote scheduled articles whose time has passed
    scheduled = await db.articles.find(
        {"status": "scheduled", "scheduled_at": {"$exists": True, "$ne": ""}},
        {"_id": 1, "scheduled_at": 1}
    ).to_list(500)
    promoted = 0
    for art in scheduled:
        try:
            sched_str = str(art["scheduled_at"]).replace("Z", "+00:00")
            sched_dt = datetime.fromisoformat(sched_str)
            if sched_dt <= now:
                await db.articles.update_one(
                    {"_id": art["_id"]},
                    {"$set": {"status": "published", "published_at": art["scheduled_at"]}}
                )
                promoted += 1
        except Exception:
            continue
    return promoted

# ─── PUBLIC ARTICLE ROUTES ───
@api_router.get("/articles")
async def get_articles(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=50),
    status: Optional[str] = "published"
):
    await auto_promote_scheduled()
    if status == "published":
        query = build_public_query()
    else:
        query = {"status": status} if status else {}
    if category:
        query["categories"] = category
    if tag:
        query["tags"] = tag
    skip = (page - 1) * limit
    total = await db.articles.count_documents(query)
    articles = await db.articles.find(query, {"_id": 1, "title": 1, "slug": 1, "excerpt": 1, "featured_image": 1, "category_name": 1, "category_slug": 1, "categories": 1, "author_name": 1, "author_slug": 1, "tags": 1, "status": 1, "is_sponsored": 1, "published_at": 1, "created_at": 1}).sort("published_at", -1).skip(skip).limit(limit).to_list(limit)
    return {"articles": serialize_list(articles), "total": total, "page": page, "pages": (total + limit - 1) // limit}

@api_router.get("/articles/featured")
async def get_featured():
    await auto_promote_scheduled()
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
    pub_query = build_public_query()
    article = await db.articles.find_one({"slug": slug, **pub_query})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    result = serialize_doc(article)
    # Ensure OG fields
    result["og_image"] = result.get("og_image") or result.get("featured_image", "")
    result["og_title"] = result.get("meta_title") or result.get("title", "")
    result["og_description"] = result.get("meta_description") or result.get("excerpt", "")
    # Get author info
    if result.get("author_id"):
        author = await db.users.find_one({"_id": ObjectId(result["author_id"])}, {"password_hash": 0})
        if author:
            result["author"] = serialize_doc(author)
    # Get related articles
    related_query = {**build_public_query(), "slug": {"$ne": slug}}
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

# ─── MARKET TICKER (with caching) ───
_ticker_cache = {"data": None, "timestamp": 0}
TICKER_CACHE_TTL = 120  # Cache for 2 minutes

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

@api_router.get("/market/ticker")
async def market_ticker():
    now = time.time()
    if _ticker_cache["data"] and (now - _ticker_cache["timestamp"]) < TICKER_CACHE_TTL:
        return _ticker_cache["data"]
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
                        tickers.append({"symbol": symbol, "price": data[cid].get("usd", 0), "change_24h": round(data[cid].get("usd_24h_change", 0), 2)})
                if tickers:
                    result = {"tickers": tickers, "updated_at": datetime.now(timezone.utc).isoformat()}
                    _ticker_cache["data"] = result
                    _ticker_cache["timestamp"] = now
                    return result
        result = {"tickers": FALLBACK_TICKERS, "updated_at": datetime.now(timezone.utc).isoformat(), "note": "cached"}
        _ticker_cache["data"] = result
        _ticker_cache["timestamp"] = now
        return result
    except Exception as e:
        logger.error(f"Ticker fetch error: {e}")
        result = {"tickers": FALLBACK_TICKERS, "updated_at": datetime.now(timezone.utc).isoformat(), "note": "cached"}
        _ticker_cache["data"] = result
        _ticker_cache["timestamp"] = now
        return result

# ─── HOMEPAGE SECTIONS ───
@api_router.get("/articles/homepage-sections")
async def get_homepage_sections():
    await auto_promote_scheduled()
    base_query = build_public_query()
    # Latest (all articles, for hero)
    latest = await db.articles.find(base_query).sort("published_at", -1).limit(5).to_list(5)
    latest_ids = [a["_id"] for a in latest]
    latest_serialized = serialize_list(latest)

    # Category sections
    sections = {}
    for cat_slug in ["crypto", "press-releases", "sponsored"]:
        cat_articles = await db.articles.find({**base_query, "categories": cat_slug, "_id": {"$nin": latest_ids[:1]}}).sort("published_at", -1).limit(4).to_list(4)
        sections[cat_slug] = serialize_list(cat_articles)

    # Others (Markets, DeFi, Analysis, Educational)
    shown_ids = set()
    for a in latest_serialized:
        shown_ids.add(a["id"])
    for cat_arts in sections.values():
        for a in cat_arts:
            shown_ids.add(a["id"])
    other_articles = await db.articles.find({**base_query, "_id": {"$nin": [ObjectId(i) for i in shown_ids]}}).sort("published_at", -1).limit(6).to_list(6)

    all_sections = {
        "latest": latest_serialized,
        "crypto": sections.get("crypto", []),
        "press_releases": sections.get("press-releases", []),
        "sponsored": sections.get("sponsored", []),
        "others": serialize_list(other_articles),
    }

    # Get custom order
    order_config = await db.site_settings.find_one({"_id": "homepage_order"})
    if order_config and order_config.get("sections"):
        ordered = {}
        for key in order_config["sections"]:
            if key in all_sections:
                ordered[key] = all_sections[key]
        for key in all_sections:
            if key not in ordered:
                ordered[key] = all_sections[key]
        return ordered

    return all_sections

# ─── ADMIN ROUTES ───
@api_router.get("/admin/articles")
async def admin_list_articles(user: dict = Depends(get_current_user), page: int = 1, limit: int = 20, status: Optional[str] = None):
    await auto_promote_scheduled()
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

@api_router.post("/admin/articles", status_code=201)
async def admin_create_article(data: ArticleCreate, user: dict = Depends(get_current_user)):
    slug = data.custom_slug.strip().lower().replace(" ", "-") if data.custom_slug and data.custom_slug.strip() else slugify(data.title)
    existing = await db.articles.find_one({"slug": slug})
    if existing:
        # Find a unique slug by appending -2, -3, etc.
        counter = 2
        while await db.articles.find_one({"slug": f"{slug}-{counter}"}):
            counter += 1
        slug = f"{slug}-{counter}"
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
    # Build categories array
    all_categories = [cat_slug] if cat_slug else []
    for sc_slug in data.secondary_categories:
        if sc_slug and sc_slug not in all_categories:
            all_categories.append(sc_slug)
    doc = {
        "title": data.title,
        "slug": slug,
        "excerpt": data.excerpt,
        "content": data.content,
        "featured_image": data.featured_image,
        "category_id": data.category_id,
        "category_name": cat_name,
        "category_slug": cat_slug,
        "categories": all_categories,
        "tags": data.tags,
        "author_id": user["id"],
        "author_name": user["name"],
        "author_slug": (await db.users.find_one({"_id": ObjectId(user["id"])}, {"slug": 1})).get("slug", ""),
        "status": data.status,
        "is_sponsored": data.is_sponsored,
        "published_at": now if data.status == "published" else None,
        "scheduled_at": data.scheduled_at,
        "og_image": data.og_image or data.featured_image,
        "meta_title": data.meta_title or data.title,
        "meta_description": data.meta_description or data.excerpt,
        "faqs": data.faqs,
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
    # Build categories array
    all_categories = [cat_slug] if cat_slug else []
    for sc_slug in data.secondary_categories:
        if sc_slug and sc_slug not in all_categories:
            all_categories.append(sc_slug)
    update = {
        "title": data.title,
        "excerpt": data.excerpt,
        "content": data.content,
        "featured_image": data.featured_image,
        "category_id": data.category_id,
        "category_name": cat_name,
        "category_slug": cat_slug,
        "categories": all_categories,
        "tags": data.tags,
        "status": data.status,
        "is_sponsored": data.is_sponsored,
        "scheduled_at": data.scheduled_at,
        "og_image": data.og_image or data.featured_image,
        "meta_title": data.meta_title or data.title,
        "meta_description": data.meta_description or data.excerpt,
        "faqs": data.faqs,
        "updated_at": now,
    }
    if data.status == "published" and existing.get("status") != "published":
        update["published_at"] = now
    if data.status == "scheduled":
        update["published_at"] = None
    # Update slug only if title changed
    if data.custom_slug and data.custom_slug.strip():
        new_slug = data.custom_slug.strip().lower().replace(" ", "-")
        if new_slug != existing.get("slug"):
            dup = await db.articles.find_one({"slug": new_slug, "_id": {"$ne": ObjectId(article_id)}})
            if dup:
                counter = 2
                while await db.articles.find_one({"slug": f"{new_slug}-{counter}", "_id": {"$ne": ObjectId(article_id)}}):
                    counter += 1
                new_slug = f"{new_slug}-{counter}"
            update["slug"] = new_slug
    elif data.title != existing.get("title"):
        new_slug = slugify(data.title)
        dup = await db.articles.find_one({"slug": new_slug, "_id": {"$ne": ObjectId(article_id)}})
        if dup:
            counter = 2
            while await db.articles.find_one({"slug": f"{new_slug}-{counter}", "_id": {"$ne": ObjectId(article_id)}}):
                counter += 1
            new_slug = f"{new_slug}-{counter}"
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
@api_router.post("/admin/categories", status_code=201)
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
@api_router.post("/admin/tags", status_code=201)
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
    scheduled = await db.articles.count_documents({"status": "scheduled"})
    categories = await db.categories.count_documents({})
    tags = await db.tags.count_documents({})
    pages = await db.pages.count_documents({})
    users = await db.users.count_documents({})
    return {"total_articles": total_articles, "published": published, "drafts": drafts, "scheduled": scheduled, "categories": categories, "tags": tags, "pages": pages, "users": users}

# ─── FILE UPLOAD ───
@api_router.post("/upload")
async def upload_file(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")
    max_size = 10 * 1024 * 1024  # 10MB
    data = await file.read()
    if len(data) > max_size:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "png"
    filename = f"{uuid.uuid4().hex}.{ext}"
    try:
        url = upload_to_cloudinary(data, filename, file.content_type)
        # Track in media library
        await db.media.insert_one({
            "url": url,
            "filename": file.filename,
            "size": len(data),
            "content_type": file.content_type,
            "uploaded_by": user.get("email", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        return {"url": url, "path": filename, "size": len(data)}
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")


@api_router.get("/media")
async def list_media(q: str = "", page: int = 1, limit: int = 24, user: dict = Depends(get_current_user)):
    query = {}
    if q:
        query["filename"] = {"$regex": q, "$options": "i"}
    skip = (page - 1) * limit
    total = await db.media.count_documents(query)
    items = await db.media.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return {"items": items, "total": total, "pages": max(1, (total + limit - 1) // limit)}


@api_router.post("/media/sync-cloudinary")
async def sync_cloudinary_media(user: dict = Depends(get_current_user)):
    """One-time sync: import existing Cloudinary images into the media library."""
    if user["role"] not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    try:
        import cloudinary.api
        result = cloudinary.api.resources(type="upload", prefix="finnews", max_results=500, resource_type="image")
        imported = 0
        for r in result.get("resources", []):
            url = r.get("secure_url", "")
            if not url:
                continue
            exists = await db.media.find_one({"url": url})
            if not exists:
                await db.media.insert_one({
                    "url": url,
                    "filename": r.get("public_id", "").split("/")[-1] + "." + r.get("format", "jpg"),
                    "size": r.get("bytes", 0),
                    "content_type": f"image/{r.get('format', 'jpeg')}",
                    "uploaded_by": "cloudinary-sync",
                    "created_at": r.get("created_at", datetime.now(timezone.utc).isoformat()),
                })
                imported += 1
        return {"imported": imported, "total_in_cloudinary": len(result.get("resources", []))}
    except Exception as e:
        logger.error(f"Cloudinary sync error: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

# ─── AUTHOR PROFILES ───
async def ensure_unique_user_slug(name: str, exclude_id=None) -> str:
    base = slugify(name) or "author"
    slug = base
    counter = 1
    while True:
        query = {"slug": slug}
        if exclude_id:
            query["_id"] = {"$ne": exclude_id}
        if not await db.users.find_one(query):
            return slug
        slug = f"{base}-{counter}"
        counter += 1

@api_router.get("/authors/by-slug/{slug}")
async def get_author_by_slug(slug: str):
    user = await db.users.find_one({"slug": slug}, {"password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Author not found")
    profile = serialize_doc(user)
    articles = await db.articles.find({"author_id": profile["id"], "status": "published"}).sort("published_at", -1).limit(20).to_list(20)
    profile["articles"] = serialize_list(articles)
    return profile

@api_router.get("/authors/{author_id}")
async def get_author_profile(author_id: str):
    user = await db.users.find_one({"_id": ObjectId(author_id)}, {"password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Author not found")
    profile = serialize_doc(user)
    articles = await db.articles.find({"author_id": author_id, "status": "published"}).sort("published_at", -1).limit(20).to_list(20)
    profile["articles"] = serialize_list(articles)
    return profile

@api_router.put("/admin/profile")
async def update_profile(data: UserProfileUpdate, user: dict = Depends(get_current_user)):
    update = {}
    if data.name is not None:
        update["name"] = data.name
    if data.bio is not None:
        update["bio"] = data.bio
    if data.avatar_url is not None:
        update["avatar_url"] = data.avatar_url
    if data.social_twitter is not None:
        update["social_twitter"] = data.social_twitter
    if data.social_linkedin is not None:
        update["social_linkedin"] = data.social_linkedin
    if data.website is not None:
        update["website"] = data.website
    if update:
        if "name" in update:
            update["slug"] = await ensure_unique_user_slug(update["name"], ObjectId(user["id"]))
        await db.users.update_one({"_id": ObjectId(user["id"])}, {"$set": update})
        # Update author_name and author_slug on articles if name changed
        if "name" in update:
            await db.articles.update_many({"author_id": user["id"]}, {"$set": {"author_name": update["name"], "author_slug": update["slug"]}})
    updated = await db.users.find_one({"_id": ObjectId(user["id"])}, {"password_hash": 0})
    return serialize_doc(updated)

# ─── ADMIN USER MANAGEMENT (super_admin only) ───
@api_router.get("/admin/users")
async def admin_list_users(user: dict = Depends(get_current_user)):
    if user["role"] not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    users = await db.users.find({}, {"password_hash": 0}).to_list(100)
    return serialize_list(users)

@api_router.post("/admin/users", status_code=201)
async def admin_create_user(data: UserCreate, user: dict = Depends(get_current_user)):
    if user["role"] not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    email = data.email.strip().lower()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already in use")
    now = datetime.now(timezone.utc).isoformat()
    user_slug = await ensure_unique_user_slug(data.name)
    doc = {
        "email": email,
        "password_hash": hash_password(data.password),
        "name": data.name,
        "slug": user_slug,
        "role": data.role,
        "bio": data.bio or "",
        "avatar_url": "",
        "social_twitter": "",
        "social_linkedin": "",
        "website": "",
        "created_at": now,
    }
    result = await db.users.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc.pop("_id", None)
    doc.pop("password_hash", None)
    return doc

@api_router.put("/admin/users/{user_id}/role")
async def admin_update_user_role(user_id: str, role: str = Query(...), user: dict = Depends(get_current_user)):
    if user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Only super admin can change roles")
    if role not in ROLES_HIERARCHY:
        raise HTTPException(status_code=400, detail="Invalid role")
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": role}})
    return {"message": "Role updated"}

@api_router.delete("/admin/users/{user_id}")
async def admin_delete_user(user_id: str, user: dict = Depends(get_current_user)):
    if user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Only super admin can delete users")
    if user_id == user["id"]:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    await db.users.delete_one({"_id": ObjectId(user_id)})
    return {"message": "User deleted"}

# ─── OG META FOR SOCIAL CRAWLERS ───
@api_router.get("/og/{category_slug}/{article_slug}")
async def og_meta_page(category_slug: str, article_slug: str):
    """Serve HTML with dynamic OG meta tags for social crawlers (X, Facebook, CMC, etc.)."""
    from fastapi.responses import HTMLResponse
    from html import escape
    base_url = os.environ.get("SITE_URL", "https://www.axiomfinity.com")
    article = await db.articles.find_one(
        {"slug": article_slug, **build_public_query()},
        {"_id": 0, "title": 1, "excerpt": 1, "featured_image": 1, "og_image": 1,
         "meta_title": 1, "meta_description": 1, "category_slug": 1, "author_name": 1,
         "published_at": 1, "updated_at": 1, "slug": 1}
    )
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    title = escape(article.get("meta_title") or article.get("title", "AxiomFinity"))
    description = escape(article.get("meta_description") or article.get("excerpt", ""))
    image = article.get("og_image") or article.get("featured_image", f"{base_url}/logo192.png")
    canonical = f"{base_url}/{article.get('category_slug', category_slug)}/{article_slug}"
    author = escape(article.get("author_name", "AxiomFinity"))
    published_at = article.get("published_at", "")
    modified_at = article.get("updated_at", published_at)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{title} | AxiomFinity</title>
<meta name="description" content="{description}"/>
<meta property="og:type" content="article"/>
<meta property="og:title" content="{title}"/>
<meta property="og:description" content="{description}"/>
<meta property="og:image" content="{escape(image)}"/>
<meta property="og:url" content="{canonical}"/>
<meta property="og:site_name" content="AxiomFinity"/>
<meta property="article:author" content="{author}"/>
<meta property="article:published_time" content="{published_at}"/>
<meta property="article:modified_time" content="{modified_at}"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="{title}"/>
<meta name="twitter:description" content="{description}"/>
<meta name="twitter:image" content="{escape(image)}"/>
<link rel="canonical" href="{canonical}"/>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"NewsArticle","headline":"{title}","description":"{description}","image":["{escape(image)}"],"datePublished":"{published_at}","dateModified":"{modified_at}","author":{{"@type":"Person","name":"{author}"}},"publisher":{{"@type":"Organization","name":"AxiomFinity","logo":{{"@type":"ImageObject","url":"{base_url}/logo192.png"}}}},"mainEntityOfPage":{{"@type":"WebPage","@id":"{canonical}"}}}}
</script>
<meta http-equiv="refresh" content="0;url={canonical}"/>
</head>
<body><p>Redirecting to <a href="{canonical}">{title}</a>...</p></body>
</html>"""
    return HTMLResponse(content=html)


# ─── XML SITEMAP ───
@api_router.get("/sitemap.xml")
async def sitemap():
    from fastapi.responses import Response as FastResponse
    base_url = os.environ.get("SITE_URL", "https://www.axiomfinity.com")
    articles = await db.articles.find(build_public_query(), {"slug": 1, "category_slug": 1, "updated_at": 1}).to_list(5000)
    categories = await db.categories.find({}, {"slug": 1}).to_list(100)
    pages = await db.pages.find({}, {"slug": 1, "updated_at": 1}).to_list(100)

    urls = [f'  <url><loc>{base_url}/</loc><changefreq>hourly</changefreq><priority>1.0</priority></url>']
    urls.append(f'  <url><loc>{base_url}/latest</loc><changefreq>hourly</changefreq><priority>0.9</priority></url>')
    urls.append(f'  <url><loc>{base_url}/education</loc><changefreq>weekly</changefreq><priority>0.7</priority></url>')
    urls.append(f'  <url><loc>{base_url}/about</loc><changefreq>monthly</changefreq><priority>0.5</priority></url>')
    urls.append(f'  <url><loc>{base_url}/contact</loc><changefreq>monthly</changefreq><priority>0.5</priority></url>')

    for cat in categories:
        urls.append(f'  <url><loc>{base_url}/category/{cat["slug"]}</loc><changefreq>daily</changefreq><priority>0.8</priority></url>')

    for article in articles:
        slug = article.get("slug", "")
        cat_slug = article.get("category_slug", "news")
        lastmod = article.get("updated_at", "")
        mod_tag = f"<lastmod>{lastmod}</lastmod>" if lastmod else ""
        urls.append(f'  <url><loc>{base_url}/{cat_slug}/{slug}</loc>{mod_tag}<changefreq>weekly</changefreq><priority>0.7</priority></url>')

    for pg in pages:
        urls.append(f'  <url><loc>{base_url}/page/{pg["slug"]}</loc><changefreq>monthly</changefreq><priority>0.4</priority></url>')

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>'''
    return FastResponse(content=xml, media_type="application/xml")


@api_router.get("/rss.xml")
async def rss_feed():
    from fastapi.responses import Response as FastResponse
    from xml.sax.saxutils import escape
    base_url = os.environ.get("SITE_URL", "https://www.axiomfinity.com")
    articles = await db.articles.find(
        build_public_query(),
        {"_id": 0, "title": 1, "slug": 1, "excerpt": 1, "content": 1, "featured_image": 1,
         "category_name": 1, "category_slug": 1, "categories": 1,
         "author_name": 1, "published_at": 1, "tags": 1}
    ).sort("published_at", -1).limit(50).to_list(50)

    def to_rfc822(iso_str):
        try:
            from email.utils import format_datetime
            dt = datetime.fromisoformat(str(iso_str).replace("Z", "+00:00"))
            return format_datetime(dt)
        except Exception:
            return str(iso_str)

    items_xml = []
    for a in articles:
        slug = a.get("slug", "")
        cat_slug = a.get("category_slug", "news")
        link = f"{base_url}/{cat_slug}/{slug}"
        title = escape(a.get("title", ""))
        desc = escape(a.get("excerpt", ""))
        author = escape(a.get("author_name", "AxiomFinity"))
        pub_date = to_rfc822(a.get("published_at", ""))
        image = a.get("featured_image", "")
        categories_xml = ""
        for cat in (a.get("categories") or [a.get("category_slug", "")]):
            if cat:
                categories_xml += f"\n      <category>{escape(cat)}</category>"

        image_enclosure = ""
        if image:
            image_enclosure = f'\n      <enclosure url="{escape(image)}" type="image/jpeg" length="0" />'

        media_content = ""
        if image:
            media_content = f'\n      <media:content url="{escape(image)}" medium="image" />'
            media_content += f'\n      <media:thumbnail url="{escape(image)}" />'

        items_xml.append(f"""    <item>
      <title>{title}</title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <pubDate>{pub_date}</pubDate>
      <dc:creator>{author}</dc:creator>{categories_xml}
      <description>{desc}</description>{image_enclosure}{media_content}
    </item>""")

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:content="http://purl.org/rss/1.0/modules/content/"
  xmlns:atom="http://www.w3.org/2005/Atom"
  xmlns:media="http://search.yahoo.com/mrss/">
  <channel>
    <title>AxiomFinity | Crypto &amp; Financial News</title>
    <link>{base_url}</link>
    <description>Breaking crypto and financial news, analysis, and market insights from AxiomFinity.</description>
    <language>en-us</language>
    <lastBuildDate>{to_rfc822(datetime.now(timezone.utc).isoformat())}</lastBuildDate>
    <atom:link href="{base_url}/rss.xml" rel="self" type="application/rss+xml" />
    <image>
      <url>{base_url}/logo192.png</url>
      <title>AxiomFinity</title>
      <link>{base_url}</link>
    </image>
{chr(10).join(items_xml)}
  </channel>
</rss>"""
    return FastResponse(content=rss, media_type="application/rss+xml; charset=utf-8")


@api_router.get("/rss/quality.xml")
async def rss_quality_feed():
    """Editorial-only RSS feed for syndication partners (CoinStats, etc.). Excludes sponsored, press releases, and low-quality content."""
    from fastapi.responses import Response as FastResponse
    from xml.sax.saxutils import escape
    base_url = os.environ.get("SITE_URL", "https://www.axiomfinity.com")

    ALLOWED_PRIMARY = {"crypto", "analysis", "markets"}
    EXCLUDED_SLUGS = {"press-releases", "sponsored", "press-release"}
    EXCLUDED_TAGS = {"sponsored", "press release", "press-release", "press releases", "pr"}

    await auto_promote_scheduled()
    all_articles = await db.articles.find(
        build_public_query(),
        {"_id": 0, "title": 1, "slug": 1, "excerpt": 1, "featured_image": 1,
         "category_slug": 1, "categories": 1, "is_sponsored": 1,
         "author_name": 1, "published_at": 1, "tags": 1}
    ).sort("published_at", -1).to_list(5000)

    def to_rfc822(iso_str):
        try:
            from email.utils import format_datetime
            dt = datetime.fromisoformat(str(iso_str).replace("Z", "+00:00"))
            return format_datetime(dt)
        except Exception:
            return str(iso_str)

    items_xml = []
    for a in all_articles:
        # Primary category must be in allowed list
        primary = (a.get("category_slug") or "").lower()
        if primary not in ALLOWED_PRIMARY:
            continue
        # Exclude sponsored articles
        if a.get("is_sponsored"):
            continue
        # Exclude if any category is press-releases or sponsored
        cats = [c.lower() for c in (a.get("categories") or [])]
        if EXCLUDED_SLUGS & set(cats):
            continue
        # Exclude if any tag matches
        tags = [t.lower().strip() for t in (a.get("tags") or [])]
        if EXCLUDED_TAGS & set(tags):
            continue
        # Exclude articles with very short excerpts (likely test content)
        if len(a.get("excerpt", "")) < 20:
            continue

        slug = a.get("slug", "")
        link = f"{base_url}/{primary}/{slug}"
        title = escape(a.get("title", ""))
        desc = escape(a.get("excerpt", ""))
        pub_date = to_rfc822(a.get("published_at", ""))
        image = a.get("featured_image", "")

        image_tags = ""
        if image:
            image_tags = f'\n      <enclosure url="{escape(image)}" type="image/jpeg" length="0" />'
            image_tags += f'\n      <media:content url="{escape(image)}" medium="image" />'
            image_tags += f'\n      <media:thumbnail url="{escape(image)}" />'

        items_xml.append(f"""    <item>
      <title>{title}</title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <pubDate>{pub_date}</pubDate>
      <description>{desc}</description>{image_tags}
    </item>""")

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
  xmlns:atom="http://www.w3.org/2005/Atom"
  xmlns:media="http://search.yahoo.com/mrss/">
  <channel>
    <title>AxiomFinity | Editorial Crypto &amp; Market News</title>
    <link>{base_url}</link>
    <description>Curated editorial crypto and market analysis from AxiomFinity. No sponsored or press release content.</description>
    <language>en-us</language>
    <lastBuildDate>{to_rfc822(datetime.now(timezone.utc).isoformat())}</lastBuildDate>
    <atom:link href="{base_url}/rss/quality.xml" rel="self" type="application/rss+xml" />
    <image>
      <url>{base_url}/logo192.png</url>
      <title>AxiomFinity</title>
      <link>{base_url}</link>
    </image>
{chr(10).join(items_xml)}
  </channel>
</rss>"""
    return FastResponse(content=rss, media_type="application/rss+xml; charset=utf-8")


# ─── TEAM MEMBERS ───
@api_router.get("/team")
async def get_team_members():
    members = await db.team_members.find({}).sort("order", 1).to_list(50)
    return serialize_list(members)

@api_router.get("/admin/team")
async def admin_get_team(user: dict = Depends(get_current_user)):
    members = await db.team_members.find({}).sort("order", 1).to_list(50)
    return serialize_list(members)

@api_router.post("/admin/team", status_code=201)
async def admin_create_team_member(data: dict = Body(...), user: dict = Depends(get_current_user)):
    if user["role"] not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    count = await db.team_members.count_documents({})
    doc = {
        "name": data.get("name", ""),
        "role_title": data.get("role_title", ""),
        "bio": data.get("bio", ""),
        "avatar_url": data.get("avatar_url", ""),
        "order": data.get("order", count),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    result = await db.team_members.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc.pop("_id", None)
    return doc

@api_router.put("/admin/team/{member_id}")
async def admin_update_team_member(member_id: str, data: dict = Body(...), user: dict = Depends(get_current_user)):
    if user["role"] not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    update = {k: v for k, v in data.items() if k in ["name", "role_title", "bio", "avatar_url", "order"]}
    await db.team_members.update_one({"_id": ObjectId(member_id)}, {"$set": update})
    return {"message": "Updated"}

@api_router.delete("/admin/team/{member_id}")
async def admin_delete_team_member(member_id: str, user: dict = Depends(get_current_user)):
    if user["role"] not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    await db.team_members.delete_one({"_id": ObjectId(member_id)})
    return {"message": "Deleted"}

# ─── NOFOLLOW SETTINGS ───
@api_router.get("/admin/seo-settings")
async def admin_get_seo_settings(user: dict = Depends(get_current_user)):
    settings = await db.site_settings.find_one({"_id": "seo"})
    if not settings:
        return {"nofollow_enabled": True, "excluded_domains": ""}
    return {"nofollow_enabled": settings.get("nofollow_enabled", True), "excluded_domains": settings.get("excluded_domains", "")}

@api_router.put("/admin/seo-settings")
async def admin_update_seo_settings(data: dict = Body(...), user: dict = Depends(get_current_user)):
    if user["role"] not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    await db.site_settings.update_one(
        {"_id": "seo"},
        {"$set": {"nofollow_enabled": data.get("nofollow_enabled", True), "excluded_domains": data.get("excluded_domains", "")}},
        upsert=True,
    )
    return {"message": "SEO settings updated"}

@api_router.get("/seo-settings/nofollow")
async def get_nofollow_settings():
    settings = await db.site_settings.find_one({"_id": "seo"})
    if not settings:
        return {"nofollow_enabled": True, "excluded_domains": ""}
    return {"nofollow_enabled": settings.get("nofollow_enabled", True), "excluded_domains": settings.get("excluded_domains", "")}

# ─── HOMEPAGE ORDER ───
@api_router.get("/admin/homepage-order")
async def admin_get_homepage_order(user: dict = Depends(get_current_user)):
    config = await db.site_settings.find_one({"_id": "homepage_order"})
    if not config:
        return {"sections": ["latest", "crypto", "press_releases", "sponsored", "others"]}
    return {"sections": config.get("sections", ["latest", "crypto", "press_releases", "sponsored", "others"])}

@api_router.put("/admin/homepage-order")
async def admin_update_homepage_order(data: dict = Body(...), user: dict = Depends(get_current_user)):
    if user["role"] not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    await db.site_settings.update_one(
        {"_id": "homepage_order"},
        {"$set": {"sections": data.get("sections", [])}},
        upsert=True,
    )
    return {"message": "Homepage order updated"}

# ─── NEWS SITEMAP (for Google News) ───
@api_router.get("/news-sitemap.xml")
async def news_sitemap():
    from fastapi.responses import Response as FastResponse
    base_url = os.environ.get("SITE_URL", "https://www.axiomfinity.com")
    two_days_ago = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    articles = await db.articles.find({
        "status": "published",
        "published_at": {"$gte": two_days_ago}
    }).sort("published_at", -1).to_list(1000)

    entries = []
    for a in articles:
        cat_slug = a.get("category_slug", "news")
        slug = a.get("slug", "")
        title = a.get("title", "").replace("&", "&amp;").replace("<", "&lt;")
        pub_date = a.get("published_at", "")
        entries.append(f'''  <url>
    <loc>{base_url}/{cat_slug}/{slug}</loc>
    <news:news>
      <news:publication>
        <news:name>AxiomFinity</news:name>
        <news:language>en</news:language>
      </news:publication>
      <news:publication_date>{pub_date}</news:publication_date>
      <news:title>{title}</news:title>
    </news:news>
  </url>''')

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
{chr(10).join(entries)}
</urlset>'''
    return FastResponse(content=xml, media_type="application/xml")

# ─── INCLUDE ROUTER ───
app.include_router(api_router)

# ─── SEED DATA ───
SAMPLE_CATEGORIES = [
    {"name": "Crypto", "slug": "crypto", "description": "Cryptocurrency news and analysis"},
    {"name": "Markets", "slug": "markets", "description": "Stock market and traditional finance"},
    {"name": "DeFi", "slug": "defi", "description": "Decentralized finance protocols and trends"},
    {"name": "Analysis", "slug": "analysis", "description": "Deep dives and technical analysis"},
    {"name": "Educational", "slug": "educational", "description": "Learn about blockchain and finance"},
    {"name": "Sponsored", "slug": "sponsored", "description": "Sponsored content from our partners"},
    {"name": "Press Releases", "slug": "press-releases", "description": "Official announcements and press releases"},
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
        "content": "<h2>A Historic Milestone</h2><p>Bitcoin reached a historic milestone today, surging past the $100,000 mark for the first time as institutional investors continue to pour capital into the cryptocurrency market. The move represents a significant psychological breakthrough for the world's largest digital asset.</p><h2>Institutional Momentum</h2><p>Major banks and asset managers have been steadily increasing their Bitcoin allocations throughout 2026, driven by growing client demand and clearer regulatory frameworks. BlackRock's spot Bitcoin ETF has accumulated over $50 billion in assets under management, while several sovereign wealth funds have disclosed Bitcoin positions for the first time.</p><h2>What's Next?</h2><p>While some analysts warn of potential short-term pullbacks, the consensus view remains bullish. The combination of limited supply, increasing demand, and supportive macroeconomic conditions suggests further upside potential.</p>",
        "featured_image": "https://images.unsplash.com/photo-1643962579399-705ba9e9cc0b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1NzB8MHwxfHNlYXJjaHwxfHxiaXRjb2luJTIwc3RvY2slMjBtYXJrZXQlMjBkYXJrfGVufDB8fHx8MTc3NTA1ODUwNXww&ixlib=rb-4.1.0&q=85",
        "category_slug": "crypto",
        "category_name": "Crypto",
        "categories": ["crypto"],
        "tags": ["Bitcoin", "Trading"],
        "is_sponsored": False,
    },
    {
        "title": "Ethereum's Layer 2 Ecosystem Reaches $50B in Total Value Locked",
        "slug": "ethereum-layer-2-ecosystem-50b-tvl",
        "excerpt": "The combined total value locked across Ethereum Layer 2 networks has surpassed $50 billion, highlighting the growing scalability of the Ethereum ecosystem.",
        "content": "<h2>Scaling Milestone</h2><p>Ethereum's Layer 2 ecosystem has achieved a remarkable milestone, with combined total value locked (TVL) surpassing $50 billion across various rollup networks. This represents a 300% increase from the beginning of the year.</p><h2>Leading Networks</h2><p>Arbitrum and Optimism continue to lead the pack, with Base gaining significant ground. ZK-rollups including zkSync and StarkNet are also seeing rapid adoption as their technology matures.</p><h2>DeFi Renaissance</h2><p>The lower costs and faster transactions on L2 networks have sparked a renaissance in DeFi applications, with new protocols launching daily across lending, trading, and yield optimization categories.</p>",
        "featured_image": "https://static.prod-images.emergentagent.com/jobs/0356c6e3-d9fe-4e34-b671-3b8a5d7d214f/images/a93bc06ad761fa1cee1bcc03f9f82eb5ffb38dddbd06acdd028acf9e70b95a52.png",
        "category_slug": "crypto",
        "category_name": "Crypto",
        "categories": ["crypto", "defi"],
        "tags": ["Ethereum", "Blockchain"],
        "is_sponsored": False,
    },
    {
        "title": "Trezor Launches Next-Gen Hardware Wallet with Biometric Security",
        "slug": "trezor-next-gen-hardware-wallet-biometric",
        "excerpt": "Trezor unveils its latest hardware wallet featuring fingerprint authentication and enhanced security features. Our detailed review inside.",
        "content": "<h2>Next Generation Security</h2><p>Trezor has announced the launch of its next-generation hardware wallet, featuring breakthrough biometric authentication technology. The new device represents a significant leap forward in cryptocurrency security for retail investors.</p><h2>Key Features</h2><p>The new wallet includes fingerprint scanning, a larger touchscreen display, support for over 1,000 cryptocurrencies, and an improved backup system. The device is priced at $199 and available for pre-order.</p><p><strong>Disclosure:</strong> This article is sponsored by Trezor. All opinions remain those of our editorial team.</p>",
        "featured_image": "https://static.prod-images.emergentagent.com/jobs/0356c6e3-d9fe-4e34-b671-3b8a5d7d214f/images/49f82beb8b9fd6e716ec4539493ca67d272193ac046693ecbaf6ba88c533d0a8.png",
        "category_slug": "crypto",
        "category_name": "Crypto",
        "categories": ["crypto", "sponsored"],
        "tags": ["Bitcoin", "Blockchain"],
        "is_sponsored": True,
    },
    {
        "title": "Solana DeFi Sees Record Volume as New Protocols Launch",
        "slug": "solana-defi-record-volume-new-protocols",
        "excerpt": "Solana's DeFi ecosystem is experiencing unprecedented growth with record trading volumes and a wave of innovative new protocols.",
        "content": "<h2>Explosive Growth</h2><p>Solana's decentralized finance ecosystem has recorded its highest-ever daily trading volume, driven by a surge in activity across multiple protocols. The network processed over 50 million transactions in a single day.</p><h2>New Protocol Launches</h2><p>Several high-profile DeFi protocols have launched on Solana in recent weeks, including advanced perpetual trading platforms, cross-chain bridges, and novel yield farming strategies.</p><h2>Technical Improvements</h2><p>Recent network upgrades have significantly improved Solana's reliability. The Firedancer validator client has contributed to network stability and throughput improvements.</p>",
        "featured_image": "https://images.pexels.com/photos/10628030/pexels-photo-10628030.png?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "category_slug": "defi",
        "category_name": "DeFi",
        "categories": ["defi", "crypto"],
        "tags": ["Altcoins", "Trading"],
        "is_sponsored": False,
    },
    {
        "title": "BlockFi Partners with Major Bank for Crypto Lending Services",
        "slug": "blockfi-partners-major-bank-crypto-lending",
        "excerpt": "BlockFi announces a groundbreaking partnership with a top-tier banking institution to offer regulated crypto lending services to institutional clients.",
        "content": "<h2>Strategic Partnership</h2><p>BlockFi has entered into a strategic partnership with one of the world's largest banking institutions to provide regulated cryptocurrency lending services. This partnership marks a significant milestone in the integration of traditional finance and digital assets.</p><h2>Services Offered</h2><p>The new service will allow institutional clients to access Bitcoin-collateralized loans, yield products on digital assets, and custody solutions. All services will be fully compliant with existing financial regulations.</p><p>This is a press release from BlockFi.</p>",
        "featured_image": "https://images.unsplash.com/photo-1732111816779-aeec50f788ba?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1NzB8MHwxfHNlYXJjaHw0fHxiaXRjb2luJTIwc3RvY2slMjBtYXJrZXQlMjBkYXJrfGVufDB8fHx8MTc3NTA1ODUwNXww&ixlib=rb-4.1.0&q=85",
        "category_slug": "press-releases",
        "category_name": "Press Releases",
        "categories": ["press-releases", "crypto"],
        "tags": ["Bitcoin", "Blockchain"],
        "is_sponsored": False,
    },
    {
        "title": "Technical Analysis: Key Support Levels to Watch This Week",
        "slug": "technical-analysis-key-support-levels-week",
        "excerpt": "Our weekly technical analysis covers critical support and resistance levels for Bitcoin, Ethereum, and top altcoins heading into a pivotal trading week.",
        "content": "<h2>Weekly Market Overview</h2><p>The crypto market enters a pivotal week with several key technical levels in focus. After a period of consolidation, multiple assets are approaching critical support and resistance zones.</p><h2>Bitcoin (BTC)</h2><p>Bitcoin continues to trade within a narrowing range between $98,000 and $103,000. The 50-day moving average at $96,500 represents strong support.</p><h2>Ethereum (ETH)</h2><p>Ethereum has shown relative strength, maintaining its position above the key $4,200 support level. Watch the $4,500 resistance for a potential breakout signal.</p>",
        "featured_image": "https://static.prod-images.emergentagent.com/jobs/0356c6e3-d9fe-4e34-b671-3b8a5d7d214f/images/f712192f1e093a330071590147681b698bb15be3b4c11acf87b28c9958efedf3.png",
        "category_slug": "analysis",
        "category_name": "Analysis",
        "categories": ["analysis", "crypto"],
        "tags": ["Bitcoin", "Ethereum", "Trading"],
        "is_sponsored": False,
    },
    {
        "title": "Understanding DeFi Yield Farming: A Beginner's Guide",
        "slug": "understanding-defi-yield-farming-beginners-guide",
        "excerpt": "Learn the fundamentals of DeFi yield farming, including how it works, the risks involved, and strategies for getting started safely.",
        "content": "<h2>What is Yield Farming?</h2><p>Yield farming is a method of earning rewards by providing liquidity to decentralized finance protocols. By depositing your crypto assets into liquidity pools, you earn fees and token rewards.</p><h2>Key Risks</h2><p><strong>Impermanent Loss:</strong> When the price ratio of your deposited assets changes, you may end up with less value.</p><p><strong>Smart Contract Risk:</strong> DeFi protocols built on smart contracts may contain vulnerabilities.</p><h2>Getting Started Safely</h2><p>Start with well-established protocols like Aave, Compound, or Uniswap. Begin with small amounts to understand the mechanics.</p>",
        "featured_image": "https://static.prod-images.emergentagent.com/jobs/0356c6e3-d9fe-4e34-b671-3b8a5d7d214f/images/a93bc06ad761fa1cee1bcc03f9f82eb5ffb38dddbd06acdd028acf9e70b95a52.png",
        "category_slug": "educational",
        "category_name": "Educational",
        "categories": ["educational", "defi"],
        "tags": ["Blockchain", "Web3"],
        "is_sponsored": False,
    },
    {
        "title": "Global Stock Markets Rally on Positive Economic Data",
        "slug": "global-stock-markets-rally-positive-economic-data",
        "excerpt": "Major stock indices around the world posted gains as economic data exceeded expectations, boosting investor confidence across all asset classes.",
        "content": "<h2>Markets Surge</h2><p>Global stock markets rallied broadly today following the release of stronger-than-expected economic data from the United States, Europe, and Asia. The S&P 500 rose 2.1%, while the Nasdaq Composite gained 2.8%.</p><h2>Crypto Correlation</h2><p>Bitcoin and Ethereum both posted gains in sympathy with traditional markets, highlighting the increasing correlation between digital assets and broader financial markets.</p>",
        "featured_image": "https://images.pexels.com/photos/10628030/pexels-photo-10628030.png?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "category_slug": "markets",
        "category_name": "Markets",
        "categories": ["markets"],
        "tags": ["Trading", "Bitcoin"],
        "is_sponsored": False,
    },
    {
        "title": "CoinSwap Exchange Launches Zero-Fee Trading for Premium Members",
        "slug": "coinswap-exchange-zero-fee-trading-premium",
        "excerpt": "CoinSwap Exchange introduces zero-fee trading for its premium tier members, challenging industry giants with competitive pricing.",
        "content": "<h2>Zero-Fee Trading</h2><p>CoinSwap Exchange has announced the launch of its zero-fee trading program for premium members. The move is expected to attract high-volume traders looking to minimize transaction costs.</p><h2>Premium Features</h2><p>Premium members will also gain access to advanced trading tools, priority customer support, and early access to new token listings. The premium tier is priced at $29.99 per month.</p><p><strong>Disclosure:</strong> This article is sponsored by CoinSwap Exchange.</p>",
        "featured_image": "https://static.prod-images.emergentagent.com/jobs/0356c6e3-d9fe-4e34-b671-3b8a5d7d214f/images/49f82beb8b9fd6e716ec4539493ca67d272193ac046693ecbaf6ba88c533d0a8.png",
        "category_slug": "sponsored",
        "category_name": "Sponsored",
        "categories": ["sponsored", "crypto"],
        "tags": ["Trading", "Altcoins"],
        "is_sponsored": True,
    },
    {
        "title": "Chainlink Announces Cross-Chain Protocol Upgrade",
        "slug": "chainlink-announces-cross-chain-protocol-upgrade",
        "excerpt": "Chainlink releases official statement on its upcoming cross-chain interoperability protocol, promising seamless multi-chain data feeds.",
        "content": "<h2>CCIP Upgrade</h2><p>Chainlink has officially announced a major upgrade to its Cross-Chain Interoperability Protocol (CCIP). The upgrade will enable seamless data transfer and token bridging across 15+ blockchain networks.</p><h2>Key Improvements</h2><p>The upgraded protocol features faster finality, reduced gas costs, and enhanced security through Chainlink's decentralized oracle network. Several major DeFi protocols have already committed to integrating the new version.</p>",
        "featured_image": "https://images.unsplash.com/photo-1643962579399-705ba9e9cc0b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1NzB8MHwxfHNlYXJjaHwxfHxiaXRjb2luJTIwc3RvY2slMjBtYXJrZXQlMjBkYXJrfGVufDB8fHx8MTc3NTA1ODUwNXww&ixlib=rb-4.1.0&q=85",
        "category_slug": "press-releases",
        "category_name": "Press Releases",
        "categories": ["press-releases", "defi"],
        "tags": ["Blockchain", "Altcoins"],
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
    {
        "title": "Contact",
        "slug": "contact",
        "page_type": "about",
        "content": "<h2>Get in Touch</h2><p>Have questions, feedback, or business inquiries? We'd love to hear from you. Reach out to us and we'll get back to you as soon as possible.</p><h2>How to Reach Us</h2><p>For all inquiries, please email us directly. Whether you have a story tip, partnership proposal, advertising question, or general feedback, we're here to help.</p><h2>Business Inquiries</h2><p>For partnership opportunities, sponsored content, and advertising, please include details about your proposal in your email. We typically respond within 1-2 business days.</p>",
    },
]

async def seed_admin():
    email = ADMIN_EMAIL.lower()
    existing = await db.users.find_one({"email": email})
    if existing is None:
        hashed = hash_password(ADMIN_PASSWORD)
        await db.users.insert_one({
            "email": email,
            "password_hash": hashed,
            "name": "Admin",
            "role": "super_admin",
            "bio": "Chief Editor at AxiomFinity",
            "avatar_url": "",
            "social_twitter": "",
            "social_linkedin": "",
            "website": "",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        logger.info(f"Admin user created: {email}")
    else:
        # Always sync password and role from env vars on startup
        updates = {"role": "super_admin", "password_hash": hash_password(ADMIN_PASSWORD)}
        for field in ["bio", "avatar_url", "social_twitter", "social_linkedin", "website"]:
            if field not in existing:
                updates[field] = "Chief Editor at AxiomFinity" if field == "bio" else ""
        await db.users.update_one({"email": email}, {"$set": updates})
        logger.info(f"Admin user synced: {email}")

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
            if "categories" not in article:
                article["categories"] = [article["category_slug"]] if article.get("category_slug") else []
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
    else:
        # Ensure contact page exists in existing databases
        if not await db.pages.find_one({"slug": "contact"}):
            now = datetime.now(timezone.utc).isoformat()
            await db.pages.insert_one({
                "title": "Contact",
                "slug": "contact",
                "page_type": "about",
                "content": "<h2>Get in Touch</h2><p>Have questions, feedback, or business inquiries? We'd love to hear from you. Reach out to us and we'll get back to you as soon as possible.</p><h2>How to Reach Us</h2><p>For all inquiries, please email us directly. Whether you have a story tip, partnership proposal, advertising question, or general feedback, we're here to help.</p><h2>Business Inquiries</h2><p>For partnership opportunities, sponsored content, and advertising, please include details about your proposal in your email. We typically respond within 1-2 business days.</p>",
                "created_at": now,
                "updated_at": now,
            })
            logger.info("Contact page seeded")

@app.on_event("startup")
async def startup():
    await db.users.create_index("email", unique=True)
    await seed_admin()
    await seed_data()
    # Backfill slugs for users missing them
    users_no_slug = await db.users.find({"$or": [{"slug": {"$exists": False}}, {"slug": ""}]}).to_list(500)
    for u in users_no_slug:
        slug = await ensure_unique_user_slug(u.get("name", "author"), u["_id"])
        await db.users.update_one({"_id": u["_id"]}, {"$set": {"slug": slug}})
        await db.articles.update_many({"author_id": str(u["_id"])}, {"$set": {"author_slug": slug}})
        logger.info(f"Backfilled slug '{slug}' for user {u.get('name')}")
    # Verify Cloudinary config
    if os.environ.get("CLOUDINARY_CLOUD_NAME"):
        logger.info("Cloudinary configured")
    else:
        logger.warning("Cloudinary not configured - image uploads will fail")
    logger.info("Startup complete")

@app.on_event("shutdown")
async def shutdown():
    client.close()
