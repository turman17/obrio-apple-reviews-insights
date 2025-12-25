import logging
from typing import List

from app.llm.client import LMStudioClient
from app.llm.prompts import (
    SYSTEM_INSIGHTS_PROMPT,
    SYSTEM_OTHER_CATEGORIES_PROMPT,
    insights_prompt,
    other_categories_prompt,
)
from app.services.insights import generate_insights as fallback_insights
from app.utils.json_utils import extract_json_from_llm


logger = logging.getLogger(__name__)


def generate_ai_insights(
    app_name: str,
    negative_phrases: List[str],
    metrics: dict,
    max_phrases: int = 15,
    max_other_categories: int = 3,
):
    """
    Try to generate insights using LLM.
    If anything fails → fallback to rule-based insights.
    """

    if not negative_phrases:
        return fallback_insights(metrics, [])

    phrases = [p for p in negative_phrases if isinstance(p, str) and p.strip()]
    phrases = phrases[:max_phrases]

    base_insights = fallback_insights(metrics, phrases)
    if not phrases:
        return base_insights

    client = LMStudioClient()

    try:
        rewritten = _rewrite_non_other(
            client=client,
            app_name=app_name,
            base_insights=base_insights,
        )
        split_other = _split_other_bucket(
            client=client,
            app_name=app_name,
            base_insights=base_insights,
            max_categories=max_other_categories,
        )

        merged = [*rewritten, *split_other]
        merged.sort(
            key=lambda x: (x.get("area") == "other", -x.get("confidence", 0))
        )
        return merged

    except Exception as e:
        logger.warning(
            "LLM insights failed, using fallback. Reason: %s", str(e)
        )
        return base_insights


def build_llm_payload(insights: List[dict]) -> List[dict]:
    return [
        {
            "area": i.get("area", "other"),
            "problem_summary": i.get("problem_summary", ""),
            "recommendation": i.get("recommendation", ""),
        }
        for i in insights
    ]


def overlay_llm_text(base: List[dict], llm: List[dict]) -> List[dict]:
    merged = []
    for index, base_item in enumerate(base):
        llm_item = llm[index] if index < len(llm) else {}
        if not isinstance(llm_item, dict):
            llm_item = {}

        merged.append({
            **base_item,
            "problem_summary": llm_item.get("problem_summary", base_item.get("problem_summary", "")),
            "recommendation": llm_item.get("recommendation", base_item.get("recommendation", "")),
        })

    return merged


def _rewrite_non_other(
    client: LMStudioClient,
    app_name: str,
    base_insights: List[dict],
) -> List[dict]:
    non_other = [i for i in base_insights if i.get("area") != "other"]
    if not non_other:
        return []

    llm_payload = build_llm_payload(non_other)
    prompt = insights_prompt(app_name, llm_payload)

    raw_response = client.run(
        system_prompt=SYSTEM_INSIGHTS_PROMPT,
        user_prompt=prompt,
    )
    parsed = extract_json_from_llm(raw_response)
    if not isinstance(parsed, list):
        raise ValueError("LLM response is not a list")
    for item in parsed:
        if not isinstance(item, dict):
            raise ValueError("Insight item is not an object")

    return overlay_llm_text(non_other, parsed)


def _split_other_bucket(
    client: LMStudioClient,
    app_name: str,
    base_insights: List[dict],
    max_categories: int,
) -> List[dict]:
    other = next((i for i in base_insights if i.get("area") == "other"), None)
    if not other:
        return []

    evidence = other.get("evidence") or []
    if not evidence:
        return [other]

    prompt = other_categories_prompt(
        app_name=app_name,
        evidence=evidence,
        max_categories=max_categories,
    )
    raw_response = client.run(
        system_prompt=SYSTEM_OTHER_CATEGORIES_PROMPT,
        user_prompt=prompt,
    )
    parsed = extract_json_from_llm(raw_response)
    if not isinstance(parsed, list):
        return [other]

    total = int(other.get("total", len(evidence)))
    split = []
    for item in parsed:
        if not isinstance(item, dict):
            continue
        area = item.get("area")
        if not area:
            continue
        ev = item.get("evidence")
        if not isinstance(ev, list) or not ev:
            continue

        count = len(ev)
        confidence = round(count / total, 2) if total else 0.0
        split.append(
            {
                "area": area,
                "problem_summary": item.get("problem_summary", ""),
                "evidence": ev[:5],
                "count": count,
                "total": total,
                "confidence": confidence,
                "recommendation": item.get("recommendation", ""),
            }
        )

    return split or [other]
