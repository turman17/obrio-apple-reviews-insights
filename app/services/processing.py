import re
import unicodedata
from typing import List

def combine_title_and_text(title, text) -> str:
    parts = []

    if isinstance(title, str):
        title = title.strip()
        if title:
            parts.append(title)

    if isinstance(text, str):
        text = text.strip()
        if text:
            parts.append(text)

    return " ".join(parts)

def clean_text(text: str) -> str:
    if not isinstance(text, str) or not text:
        return ""
    
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)

    # removes emojis
    text = re.sub(
        r"["
        "\U0001f600-\U0001f64f"
        "\U0001f300-\U0001f5ff"
        "\U0001f680-\U0001f6ff"
        "\U0001f1e0-\U0001f1ff"
        "]+",
        "",
        text,
    )

    text = _filter_text(text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def _filter_text(text: str) -> str:
    allowed = {" ", "'", "’"}
    filtered = []

    for ch in text:
        if ch in allowed:
            filtered.append(ch)
            continue

        cat = unicodedata.category(ch)
        if cat.startswith("L") or cat.startswith("N"):
            filtered.append(ch)
            continue

        filtered.append(" ")

    return "".join(filtered)

def preprocess_reviews(reviews: List[dict]) -> List[dict]:
    processed = []

    for r in reviews:
        combined_text = combine_title_and_text(
            r.get("title"),
            r.get("text")
        )

        cleaned_text = clean_text(combined_text)

        if not cleaned_text:
            continue

        processed.append({
            **r,
            "clean_text": cleaned_text,
            "clean_text_raw": combined_text 
        })

    return processed
