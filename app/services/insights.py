from typing import List, Dict
from collections import Counter, defaultdict
import logging

from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.data import find

from sklearn.feature_extraction.text import CountVectorizer

logger = logging.getLogger(__name__)
_SIA = None


class _NeutralSentiment:
    def polarity_scores(self, text: str) -> dict:
        return {"compound": 0.0}


def get_sia():
    global _SIA
    if _SIA is not None:
        return _SIA

    try:
        _SIA = SentimentIntensityAnalyzer()
    except LookupError:
        logger.warning(
            "NLTK VADER lexicon not found; falling back to neutral sentiment."
        )
        _SIA = _NeutralSentiment()

    return _SIA


def analyze_sentiment(text: str) -> str:
    score = get_sia().polarity_scores(text)["compound"]

    if score >= 0.05:
        return "positive"
    elif score <= -0.05:
        return "negative"
    return "neutral"


def add_sentiment(reviews: List[dict]) -> List[dict]:
    for r in reviews:
        r["sentiment"] = analyze_sentiment(r.get("clean_text", ""))
    return reviews


def get_stopwords():
    extra = {
        "its",
        "it's",
        "it’s",
        "im",
        "i'm",
        "i’m",
        "dont",
        "don't",
        "don’t",
        "cant",
        "can't",
        "can’t",
        "wont",
        "won't",
        "won’t",
        "even",
    }
    try:
        find("corpora/stopwords")
        return set(stopwords.words("english")) | extra
    except LookupError:
        return {
            "the",
            "and",
            "is",
            "in",
            "to",
            "of",
            "for",
            "on",
            "with",
            "this",
            "that",
            "it",
            "as",
            "are",
            "was",
            "but",
            "be",
            "have",
            "not",
            "you",
            "your",
            "i",
        } | extra


def extract_negative_keywords(reviews: List[dict], top_n: int = 10):
    stop_words = get_stopwords()
    words = []

    for r in reviews:
        if r.get("sentiment") == "negative":
            for w in r.get("clean_text", "").split():
                if w not in stop_words and len(w) > 3:
                    words.append(w)

    return Counter(words).most_common(top_n)


def extract_negative_phrases(reviews: List[dict], top_n: int = 10):
    texts = [
        r["clean_text"]
        for r in reviews
        if r.get("sentiment") == "negative" and r.get("clean_text")
    ]

    if not texts:
        return []

    vectorizer = CountVectorizer(ngram_range=(2, 3), min_df=2, stop_words="english")

    X = vectorizer.fit_transform(texts)
    phrases = vectorizer.get_feature_names_out()
    counts = X.sum(axis=0).A1

    ranked = sorted(zip(phrases, counts), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]


def map_phrase_to_area(text: str) -> str:
    areas = map_phrase_to_areas(text)
    return areas[0] if areas else "other"


def map_phrase_to_areas(text: str) -> List[str]:
    t = text.lower()
    areas = []

    if any(
        w in t
        for w in [
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
        ]
    ):
        areas.append("account_access")

    if any(
        w in t
        for w in [
            "crash",
            "crashes",
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
        ]
    ):
        areas.append("stability")

    if any(
        w in t
        for w in [
            "settings",
            "ui",
            "interface",
            "hard to",
            "difficult",
            "annoying",
            "switching",
            "controls",
            "layout",
            "navigation",
            "design",
        ]
    ):
        areas.append("usability")

    if any(
        w in t
        for w in [
            "ads",
            "advertisement",
            "advertisements",
            "sponsored",
            "promoted",
            "ad spam",
            "too many ads",
        ]
    ):
        areas.append("ads_monetization")

    if any(
        w in t
        for w in [
            "support",
            "customer service",
            "customer support",
            "no response",
            "cannot get in touch",
            "cant reach",
        ]
    ):
        areas.append("customer_support")

    if any(w in t for w in ["juego", "jugar", "idioma"]):
        areas.append("localization")

    return areas or ["other"]


def score_phrase_areas(text: str) -> Dict[str, int]:
    t = text.lower()
    scores = defaultdict(int)

    def add(area: str, keywords: List[str]) -> None:
        for kw in keywords:
            if kw in t:
                scores[area] += 1

    add(
        "account_access",
        [
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
    )
    add(
        "stability",
        [
            "crash",
            "crashes",
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
    )
    add(
        "usability",
        [
            "settings",
            "ui",
            "interface",
            "hard to",
            "difficult",
            "annoying",
            "switching",
            "controls",
            "layout",
            "navigation",
            "design",
        ],
    )
    add(
        "customer_support",
        [
            "support",
            "customer service",
            "customer support",
            "no response",
            "cannot get in touch",
            "cant reach",
        ],
    )
    add(
        "ads_monetization",
        [
            "ads",
            "advertisement",
            "advertisements",
            "sponsored",
            "promoted",
            "ad spam",
            "too many ads",
        ],
    )
    add("localization", ["juego", "jugar", "idioma"])

    return scores


AREA_TEMPLATES = {
    "stability": {
        "summary": "Users report stability issues such as crashes, freezes, or malfunctioning features.",
        "recommendation": (
            "Analyze crash logs and performance metrics from recent releases "
            "to identify and resolve stability regressions."
        ),
    },
    "usability": {
        "summary": "Users experience usability or interaction issues with the app.",
        "recommendation": (
            "Review recent UX changes and validate them through usability testing "
            "to reduce friction in common user flows."
        ),
    },
    "account_access": {
        "summary": "Users face problems related to account access, bans, or login.",
        "recommendation": (
            "Improve transparency of account actions and provide clearer recovery "
            "and appeal mechanisms."
        ),
    },
    "customer_support": {
        "summary": "Users report poor or inaccessible customer support.",
        "recommendation": (
            "Improve support responsiveness and ensure clear escalation paths, "
            "especially for business and verified accounts."
        ),
    },
    "ads_monetization": {
        "summary": "Users report excessive ads or aggressive monetization.",
        "recommendation": (
            "Review ad density and targeting rules to reduce disruption to core usage."
        ),
    },
    "localization": {
        "summary": "Users report language or region-specific issues.",
        "recommendation": (
            "Review localization coverage and ensure correct behavior "
            "for affected regions."
        ),
    },
    "other": {
        "summary": "Users report issues that do not fit common categories.",
        "recommendation": (
            "Manually review these reports to identify emerging or uncategorized problems."
        ),
    },
}


def is_low_signal_sentence(text: str) -> bool:
    t = text.lower().strip()
    if not t:
        return True

    if len(t.split()) < 6 and any(
        x in t for x in ["hate", "love", "annoying", "trash", "bad"]
    ):
        return True

    if any(
        x in t
        for x in ["stop using", "delete this app", "uninstall", "never use again"]
    ):
        return True

    return False


def generate_insights(metrics: dict, problem_sentences: List[str]) -> List[dict]:
    problem_sentences = [s for s in problem_sentences if not is_low_signal_sentence(s)]
    if not problem_sentences:
        return [
            {
                "area": "data_quality",
                "problem_summary": (
                    "Insufficient high-quality negative feedback to generate actionable insights."
                ),
                "evidence": [],
                "confidence": 0.0,
                "recommendation": (
                    "Collect more detailed user feedback or apply additional filtering "
                    "before generating insights."
                ),
            }
        ]

    total = len(problem_sentences)
    buckets = defaultdict(list)

    for sentence in problem_sentences:
        scores = score_phrase_areas(sentence)
        if not scores:
            buckets["other"].append(sentence)
            continue

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_areas = [ranked[0][0]]
        if len(ranked) > 1 and ranked[1][1] == ranked[0][1]:
            top_areas.append(ranked[1][0])

        for area in top_areas:
            if sentence not in buckets[area]:
                buckets[area].append(sentence)

    insights = []

    for area, sentences in buckets.items():
        template = AREA_TEMPLATES.get(area, AREA_TEMPLATES["other"])
        confidence = round(len(sentences) / total, 2)

        insights.append(
            {
                "area": area,
                "problem_summary": template["summary"],
                "evidence": sentences[:5],
                "count": len(sentences),
                "total": total,
                "confidence": round(len(sentences) / total, 2),
                "recommendation": template["recommendation"],
            }
        )

    insights.sort(key=lambda x: x["confidence"], reverse=True)

    return normalize_insights_schema(insights)


def normalize_insights_schema(insights: List[dict]) -> List[dict]:
    normalized = []

    for item in insights or []:
        if not isinstance(item, dict):
            continue

        normalized.append(
            {
                "area": item.get("area", "other"),
                "problem_summary": item.get("problem_summary")
                or item.get("summary")
                or "",
                "evidence": item.get("evidence", []),
                "count": int(item.get("count", 0)),
                "total": int(item.get("total", 0)),
                "confidence": round(float(item.get("confidence", 0.0)), 2),
                "recommendation": item.get("recommendation", ""),
            }
        )

    return normalized
