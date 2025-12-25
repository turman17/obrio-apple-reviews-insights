import os
import random
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
BASE_URL = "https://serpapi.com/search"


def _fetch_page(app_id: int, page: int):
    params = {
        "engine": "apple_reviews",
        "product_id": app_id,
        "page": page,
        "no_cache": "false",
        "api_key": SERPAPI_API_KEY,
    }

    response = requests.get(BASE_URL, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def collect_reviews(app_id: int, limit: int = 100, pool_multiplier: int = 2):
    if not SERPAPI_API_KEY:
        raise RuntimeError("SERPAPI_API_KEY is not set")

    target_pool_size = limit * pool_multiplier
    first_page = _fetch_page(app_id, page=1)
    reviews = first_page.get("reviews", [])

    if not reviews:
        raise ValueError("No reviews returned by SerpApi")

    all_reviews = _parse_reviews(reviews)

    total_pages = first_page.get("search_information", {}).get(
        "total_page_count", 1
    )

    avg_page_size = len(reviews)
    pages_needed = min(
        total_pages,
        (target_pool_size // avg_page_size) + 1
    )

    for page in range(2, pages_needed + 1):
        data = _fetch_page(app_id, page)
        page_reviews = data.get("reviews", [])

        if not page_reviews:
            break

        all_reviews.extend(_parse_reviews(page_reviews))

        if len(all_reviews) >= target_pool_size:
            break

    if len(all_reviews) < limit:
        raise ValueError(
            f"Only {len(all_reviews)} reviews available, cannot sample {limit}"
        )

    return random.sample(all_reviews, limit)


def _parse_reviews(reviews):
    parsed = []
    for r in reviews:
        rating = _safe_int(r.get("rating"))
        if rating is None:
            logger.warning("Skipping review with invalid rating: %r", r.get("rating"))
            continue

        parsed.append({
            "review_id": r.get("id"),
            "title": (r.get("title") or "").strip(),
            "text": (r.get("text") or "").strip(),
            "rating": rating,
        })
    return parsed


def _safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
