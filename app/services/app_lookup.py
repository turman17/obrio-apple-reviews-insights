import requests


def resolve_app_id_by_name(app_name: str) -> int:
    """
    Resolve Apple App Store app_id by app name using iTunes Search API.
    """
    url = "https://itunes.apple.com/search"
    params = {
        "term": app_name,
        "entity": "software",
        "limit": 1,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    if not data.get("results"):
        raise ValueError(f"App '{app_name}' not found")

    return data["results"][0]["trackId"]
