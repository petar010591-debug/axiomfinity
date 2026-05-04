"""
IndexNow integration — pings Bing + Yandex + Naver + Seznam + Yep instantly
when articles are published, updated, or deleted.

Docs: https://www.indexnow.org/documentation
No API key registration required. The key is a self-generated UUID served
at /{key}.txt so search engines can verify site ownership.
"""
import os
import logging
import httpx

logger = logging.getLogger(__name__)

INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"


def get_key() -> str:
    """Return the IndexNow key from env (required in production)."""
    return os.environ.get("INDEXNOW_KEY", "")


def get_site_host() -> str:
    """Return the bare host (no scheme) for IndexNow."""
    site = os.environ.get("SITE_URL", "https://www.axiomfinity.com")
    return site.replace("https://", "").replace("http://", "").rstrip("/")


def get_base_url() -> str:
    return os.environ.get("SITE_URL", "https://www.axiomfinity.com").rstrip("/")


async def ping_urls(urls: list[str]) -> dict:
    """
    Notify IndexNow of new/updated/deleted URLs.
    Returns {"ok": bool, "status": int, "body": str}.
    Silently no-ops if INDEXNOW_KEY is missing.
    """
    key = get_key()
    if not key or not urls:
        return {"ok": False, "status": 0, "body": "missing key or empty urls"}

    host = get_site_host()
    base = get_base_url()

    # Filter: IndexNow requires same-host URLs, absolute, max 10,000 per call
    clean_urls = [u for u in urls if u.startswith(base)][:10000]
    if not clean_urls:
        return {"ok": False, "status": 0, "body": "no matching-host urls"}

    payload = {
        "host": host,
        "key": key,
        "keyLocation": f"{base}/{key}.txt",
        "urlList": clean_urls,
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                INDEXNOW_ENDPOINT,
                json=payload,
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
            ok = r.status_code in (200, 202)
            if ok:
                logger.info(f"IndexNow pinged {len(clean_urls)} URL(s), status={r.status_code}")
            else:
                logger.warning(f"IndexNow ping failed: status={r.status_code} body={r.text[:200]}")
            return {"ok": ok, "status": r.status_code, "body": r.text[:500]}
    except Exception as e:
        logger.warning(f"IndexNow ping exception: {e}")
        return {"ok": False, "status": 0, "body": str(e)}


def build_article_url(article: dict) -> str:
    """Build the canonical article URL from a DB doc."""
    base = get_base_url()
    cat = article.get("category_slug") or "crypto"
    slug = article.get("slug", "")
    return f"{base}/{cat}/{slug}"
