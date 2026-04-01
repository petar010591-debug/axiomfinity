from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends, Query, UploadFile, File
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
import requests as sync_requests
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

# ─── OBJECT STORAGE ───
STORAGE_URL = "https://integrations.emergentagent.com/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")
APP_NAME = "finnews"
_storage_key = None

def init_storage():
    global _storage_key
    if _storage_key:
        return _storage_key
    resp = sync_requests.post(f"{STORAGE_URL}/init", json={"emergent_key": EMERGENT_KEY}, timeout=30)
    resp.raise_for_status()
    _storage_key = resp.json()["storage_key"]
    return _storage_key

def put_object(path: str, data: bytes, content_type: str) -> dict:
    key = init_storage()
    resp = sync_requests.put(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key, "Content-Type": content_type}, data=data, timeout=120)
    resp.raise_for_status()
    return resp.json()

def get_object(path: str):
    key = init_storage()
    resp = sync_requests.get(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key}, timeout=60)
    resp.raise_for_status()
    return resp.content, resp.headers.get("Content-Type", "application/octet-stream")

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
    now = datetime.now(timezone.utc).isoformat()
    return {"$or": [
        {"status": "published"},
        {"status": "scheduled", "scheduled_at": {"$lte": now}}
    ]}

# ─── PUBLIC ARTICLE ROUTES ───
@api_router.get("/articles")
async def get_articles(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=50),
    status: Optional[str] = "published"
):
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
    articles = await db.articles.find(query, {"_id": 1, "title": 1, "slug": 1, "excerpt": 1, "featured_image": 1, "category_name": 1, "category_slug": 1, "categories": 1, "author_name": 1, "tags": 1, "status": 1, "is_sponsored": 1, "published_at": 1, "created_at": 1}).sort("published_at", -1).skip(skip).limit(limit).to_list(limit)
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
        author = await db.users.find_one({"_id": ObjectId(result["author_id"])}, {"password_hash": 0, "_id": 1, "name": 1, "bio": 1, "avatar_url": 1, "social_twitter": 1})
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

    return {
        "latest": latest_serialized,
        "crypto": sections.get("crypto", []),
        "press_releases": sections.get("press-releases", []),
        "sponsored": sections.get("sponsored", []),
        "others": serialize_list(other_articles),
    }

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

@api_router.post("/admin/articles", status_code=201)
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
        "status": data.status,
        "is_sponsored": data.is_sponsored,
        "published_at": now if data.status == "published" else None,
        "scheduled_at": data.scheduled_at,
        "og_image": data.og_image or data.featured_image,
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
        "updated_at": now,
    }
    if data.status == "published" and existing.get("status") != "published":
        update["published_at"] = now
    if data.status == "scheduled" and data.scheduled_at:
        update["published_at"] = data.scheduled_at
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
    filename = f"{APP_NAME}/{uuid.uuid4().hex}.{ext}"
    try:
        result = put_object(filename, data, file.content_type)
        return {"url": result.get("url", ""), "path": filename, "size": len(data)}
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")

# ─── AUTHOR PROFILES ───
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
        await db.users.update_one({"_id": ObjectId(user["id"])}, {"$set": update})
        # Update author_name on articles if name changed
        if "name" in update:
            await db.articles.update_many({"author_id": user["id"]}, {"$set": {"author_name": update["name"]}})
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
    doc = {
        "email": email,
        "password_hash": hash_password(data.password),
        "name": data.name,
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

# ─── XML SITEMAP ───
@api_router.get("/sitemap.xml")
async def sitemap():
    from fastapi.responses import Response as FastResponse
    base_url = os.environ.get("SITE_URL", "https://finnews.com")
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
]

async def seed_admin():
    existing = await db.users.find_one({"email": ADMIN_EMAIL.lower()})
    if existing is None:
        hashed = hash_password(ADMIN_PASSWORD)
        await db.users.insert_one({
            "email": ADMIN_EMAIL.lower(),
            "password_hash": hashed,
            "name": "Admin",
            "role": "super_admin",
            "bio": "Chief Editor at FinNews",
            "avatar_url": "",
            "social_twitter": "",
            "social_linkedin": "",
            "website": "",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        logger.info(f"Admin user created: {ADMIN_EMAIL}")
    else:
        # Ensure super_admin role and profile fields
        updates = {}
        if existing.get("role") != "super_admin":
            updates["role"] = "super_admin"
        if "bio" not in existing:
            updates["bio"] = "Chief Editor at FinNews"
        if "avatar_url" not in existing:
            updates["avatar_url"] = ""
        if "social_twitter" not in existing:
            updates["social_twitter"] = ""
        if "social_linkedin" not in existing:
            updates["social_linkedin"] = ""
        if "website" not in existing:
            updates["website"] = ""
        if not verify_password(ADMIN_PASSWORD, existing["password_hash"]):
            updates["password_hash"] = hash_password(ADMIN_PASSWORD)
        if updates:
            await db.users.update_one({"email": ADMIN_EMAIL.lower()}, {"$set": updates})
            logger.info("Admin user updated")

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

@app.on_event("startup")
async def startup():
    await db.users.create_index("email", unique=True)
    await seed_admin()
    await seed_data()
    # Init storage
    try:
        init_storage()
        logger.info("Object storage initialized")
    except Exception as e:
        logger.warning(f"Storage init deferred: {e}")
    # Write test credentials
    os.makedirs("/app/memory", exist_ok=True)
    with open("/app/memory/test_credentials.md", "w") as f:
        f.write(f"# Test Credentials\n\n## Admin\n- Email: {ADMIN_EMAIL}\n- Password: {ADMIN_PASSWORD}\n- Role: admin\n\n## Auth Endpoints\n- POST /api/auth/login\n- POST /api/auth/logout\n- GET /api/auth/me\n")
    logger.info("Startup complete")

@app.on_event("shutdown")
async def shutdown():
    client.close()
