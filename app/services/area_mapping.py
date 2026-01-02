from collections import defaultdict
from typing import Dict, List

AREA_KEYWORDS = {
    "account_access": [
        "ban",
        "banned",
        "suspend",
        "suspended",
        "login",
        "account",
        "blocked",
        "verification",
        "delete",
        "deleted",
        "removed",
        "community guidelines",
        "violat",
        "appeal",
    ],
    "stability": [
        "crash",
        "crashes",
        "vanish",
        "vanished",
        "disappear",
        "disappeared",
        "freeze",
        "frozen",
        "lag",
        "glitch",
        "bug",
        "stops working",
        "not working",
        "won't open",
        "doesn't open",
        "keeps crashing",
    ],
    "usability": [
        "cant",
        "can't",
        "cannot",
        "unable",
        "hard",
        "using",
        "controls",
        "settings",
        "ui",
        "interface",
        "hard to",
        "difficult",
        "annoying",
        "switching",
        "layout",
        "navigation",
        "design",
    ],
    "ads_monetization": [
        "ads",
        "advertisement",
        "advertisements",
        "sponsored",
        "promoted",
        "ad spam",
        "too many ads",
    ],
    "customer_support": [
        "support",
        "customer service",
        "customer support",
        "no response",
        "cannot get in touch",
        "cant reach",
    ],
    "localization": [
        "juego",
        "jugar",
        "idioma",
    ],
}


def map_phrase_to_areas(text: str) -> List[str]:
    t = text.lower()
    areas = [area for area, keywords in AREA_KEYWORDS.items() if _has_any(t, keywords)]
    return areas or ["other"]


def map_phrase_to_area(text: str) -> str:
    areas = map_phrase_to_areas(text)
    return areas[0] if areas else "other"


def score_phrase_areas(text: str) -> Dict[str, int]:
    t = text.lower()
    scores = defaultdict(int)

    for area, keywords in AREA_KEYWORDS.items():
        for kw in keywords:
            if kw in t:
                scores[area] += 1

    return scores


def _has_any(text: str, keywords: List[str]) -> bool:
    return any(kw in text for kw in keywords)
