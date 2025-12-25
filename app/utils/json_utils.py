import json
import re

def extract_json_from_llm(text: str):
    """
    Extract the first JSON object or array from LLM response.
    Handles ```json blocks and raw JSON with surrounding text.
    """
    if not isinstance(text, str) or not text:
        return None

    cleaned = re.sub(r"```json|```", "", text).strip()
    start = _find_json_start(cleaned)
    if start is None:
        return None

    payload = _extract_json_payload(cleaned, start)
    if payload is None:
        return None

    try:
        return json.loads(payload)
    except Exception:
        return None


def _find_json_start(text: str):
    for i, ch in enumerate(text):
        if ch in "{[":
            return i
    return None


def _extract_json_payload(text: str, start_index: int):
    stack = []
    in_string = False
    escape = False

    for i in range(start_index, len(text)):
        ch = text[i]

        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
            continue

        if ch in "{[":
            stack.append(ch)
        elif ch in "}]":
            if not stack:
                return None
            opening = stack.pop()
            if (opening == "{" and ch != "}") or (opening == "[" and ch != "]"):
                return None
            if not stack:
                return text[start_index : i + 1]

    return None
