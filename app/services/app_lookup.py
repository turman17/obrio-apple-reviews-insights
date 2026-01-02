import httpx
from app.services.cache import TTLCache

_APP_ID_CACHE = TTLCache(ttl_seconds=3600, max_items=512)


async def resolve_app_id_by_name(app_name: str) -> int:
    """
    Resolve Apple App Store app_id by app name using iTunes Search API.
    """
    url = "https://itunes.apple.com/search"
    cache_key = app_name.strip().lower()
    cached = _APP_ID_CACHE.get(cache_key)
    if cached is not None:
        return cached

    params = {
        "term": app_name,
        "entity": "software",
        "limit": 1,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    if not data.get("results"):
        raise ValueError(f"App '{app_name}' not found")

    app_id = data["results"][0]["trackId"]
    _APP_ID_CACHE.set(cache_key, app_id)
    return app_id
