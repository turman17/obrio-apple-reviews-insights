import re
from typing import List

from nltk.tokenize import sent_tokenize

PROBLEM_VERBS = [
    "crash", "crashed", "vanish", "vanished", "disappear", "disappeared",
    "stop", "stopped", "freeze", "frozen",
    "cannot", "can't", "unable", "won't",
    "delete", "deleted", "lost", "missing", "blocked"
]

def normalize_sentence(sentence: str) -> str:
    sentence = sentence.strip()

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


def map_phrase_to_area(phrase: str) -> str:
    areas = map_phrase_to_areas(phrase)
    return areas[0] if areas else "other"


def map_phrase_to_areas(phrase: str) -> list[str]:
    areas = []
    s = phrase.lower()

    if any(w in s for w in ["crash", "vanish", "disappear", "lag", "freeze"]):
        areas.append("stability")
    if any(w in s for w in ["cant", "unable", "hard", "using", "controls"]):
        areas.append("usability")
    if any(w in s for w in ["login", "account", "ban", "blocked"]):
        areas.append("account_access")
    if any(w in s for w in ["juego", "jugar", "idioma"]):
        areas.append("localization")

    return areas or ["other"]
