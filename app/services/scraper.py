import json
from app.services.app_lookup import resolve_app_id_by_name
from app.services.serpapi_client import collect_reviews as serp_collect


def collect_reviews(app_name: str, limit=100):
    """
    Collect random Apple App Store reviews for a given app name.
    """
    app_id = resolve_app_id_by_name(app_name)

    return serp_collect(
        app_id=app_id,
        limit=limit,
    )
