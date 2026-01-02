import re
from typing import List

from nltk.tokenize import sent_tokenize
from app.services.area_mapping import map_phrase_to_area, map_phrase_to_areas

PROBLEM_VERBS = [
    "crash", "crashed", "vanish", "vanished", "disappear", "disappeared",
    "stop", "stopped", "freeze", "frozen",
    "cannot", "can't", "unable", "won't",
    "delete", "deleted", "lost", "missing", "blocked"
]

def normalize_sentence(sentence: str) -> str:
    sentence = sentence.strip()
    sentence = sentence.rstrip(".!?")

    prefixes = [
        "so while", "i’m gonna", "i am gonna",
        "i love", "to be honest", "cut to the chase"
    ]

    s = sentence.lower()
    for p in prefixes:
        if s.startswith(p):
            return sentence[len(p):].strip().capitalize()

    return sentence

def extract_problem_sentences(
    reviews: List[dict],
    max_results: int = 50
) -> list[str]:

    sentences = []

    for r in reviews:
        if r.get("sentiment") != "negative":
            continue

        text = r.get("clean_text_raw")
        if not text:
            continue

        for sent in split_sentences(text):
            sent = normalize_sentence(sent)
            if not sent:
                continue
            if not is_problem_sentence(sent):
                continue
            sentences.append(sent)

    seen = set()
    unique = []
    for s in sentences:
        if s not in seen:
            seen.add(s)
            unique.append(s)

    return unique[:max_results]


def split_sentences(text: str) -> list[str]:
    try:
        return sent_tokenize(text)
    except LookupError:
        return re.split(r"[.!?]", text)


def is_problem_sentence(sentence: str) -> bool:
    s = sentence.lower()

    if len(s.split()) < 4:
        return False

    if any(v in s for v in PROBLEM_VERBS):
        return True

    extra_signals = [
        "bug",
        "broken",
        "ads",
        "ad",
        "annoying",
        "slow",
        "lag",
        "error",
        "issue",
        "problem",
    ]

    if not any(v in s for v in extra_signals):
        return False

    return True


__all__ = [
    "extract_problem_sentences",
    "split_sentences",
    "is_problem_sentence",
    "map_phrase_to_area",
    "map_phrase_to_areas",
]
