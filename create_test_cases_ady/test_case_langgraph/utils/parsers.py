"""
Utilities for parsing LLM JSON responses.
"""

import json
import re
from typing import Any, Dict, Optional


def _extract_first_json_block(content: str) -> str:
    """
    Return the first balanced JSON object/array substring, or empty string if not found.
    """
    start_positions = [pos for pos in (content.find("{"), content.find("[")) if pos != -1]
    if not start_positions:
        return ""
    start = min(start_positions)
    open_char = content[start]
    close_char = "}" if open_char == "{" else "]"
    depth = 0
    for idx in range(start, len(content)):
        ch = content[idx]
        if ch == open_char:
            depth += 1
        elif ch == close_char:
            depth -= 1
            if depth == 0:
                return content[start : idx + 1]
    return ""


def parse_llm_json(content: str) -> Any:
    """
    Parse JSON from LLM response, handling markdown code blocks and extra text.
    """
    content = content.strip()

    # Strip fenced code blocks
    content = re.sub(r"^```json\s*", "", content, flags=re.MULTILINE)
    content = re.sub(r"^```\s*$", "", content, flags=re.MULTILINE)
    content = content.strip()

    # If the model returned raw key-value lines without braces, try to wrap.
    if content and "{" not in content and "[" not in content and '"evaluations"' in content:
        content = "{" + content + "}"

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    extracted = _extract_first_json_block(content)
    if extracted:
        try:
            return json.loads(extracted)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}\nContent: {content[:500]}")

    raise ValueError(f"Failed to parse JSON: no JSON block found\nContent: {content[:500]}")


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get value from dict with default."""
    return data.get(key, default) if isinstance(data, dict) else default


def extract_test_case_summary(tc: Dict[str, Any]) -> str:
    """Create a brief summary of a test case for logging."""
    tc_id = tc.get("TC_ID", "???")
    title = tc.get("Testcase name", "Untitled")
    category = tc.get("category", "unknown")
    return f"{tc_id}: {title} [{category}]"
