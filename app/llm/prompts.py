import json

SYSTEM_INSIGHTS_PROMPT = """
You are given precomputed analytics for product issues.

Rules:
- Do NOT add or remove items.
- Do NOT change numeric values (you do not see them).
- Only rewrite: problem_summary, recommendation.
- Rephrase with new wording; avoid copying sentences from the input.
- Keep the same order.
- Return JSON array only.
"""

SYSTEM_OTHER_CATEGORIES_PROMPT = """
You are given uncategorized user problem statements.

Rules:
- Group only the provided statements into new categories.
- Do NOT invent new evidence.
- Return JSON array only.
"""


def insights_prompt(app_name: str, insights_payload: list[dict]) -> str:
    payload_json = json.dumps(insights_payload, ensure_ascii=False, indent=2)
    return f"""
App: {app_name}

Rewrite the fields in each item while preserving structure and order.
Return only objects with: area, problem_summary, recommendation.

Input JSON:
{payload_json}
"""


def other_categories_prompt(app_name: str, evidence: list[str], max_categories: int = 3) -> str:
    evidence_json = json.dumps(evidence, ensure_ascii=False, indent=2)
    return f"""
App: {app_name}

Group the following evidence into at most {max_categories} new categories.
Return JSON array with objects:
[
  {{
    "area": "<short category name>",
    "problem_summary": "<concise summary>",
    "recommendation": "<actionable recommendation>",
    "evidence": ["sentence 1", "sentence 2"]
  }}
]

Evidence:
{evidence_json}
"""
