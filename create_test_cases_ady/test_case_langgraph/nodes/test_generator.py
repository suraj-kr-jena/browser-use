"""
Node: Test Case Generator

Generates a batch of test cases based on feedback and coverage tracking.
"""

import json
from typing import Any, Dict

from ..state import TestCaseState
from ..utils.parsers import parse_llm_json
from ..utils.prompt_templates import PromptTemplates


def generate_test_cases_node(state: TestCaseState, llm: Any) -> Dict[str, Any]:
    """
    Generate a new batch of test cases using the dedicated prompt.
    """

    approved_so_far = len(state.get("approved_testcases", []))
    max_testcases = state.get("max_testcases", 0) or 0
    remaining = max(0, max_testcases - approved_so_far) if max_testcases else state.get("batch_size", 5)

    if remaining == 0:
        return {
            "current_batch": [],
            "iteration": state.get("iteration", 0) + 1,
            "messages": ["⚠ No remaining test cases requested; skipping generation"],
        }

    batch_target = min(state.get("batch_size", 5), remaining)

    prompt = PromptTemplates.build_test_case_prompt(
        feature_name=state["feature_name"],
        feature_description=state["feature_description"],
        user_guide_text=state["user_guide_text"],
        feature_summary_text=state["feature_summary_text"],
        screen_contracts_json=state["screen_contracts_json"],
        max_cases=batch_target,
        platform=state["platform"],
    )

    response = llm.invoke(prompt)
    content = response.content if hasattr(response, "content") else str(response)

    try:
        test_cases = parse_llm_json(content)

        if not isinstance(test_cases, list):
            test_cases = []

        valid_cases = []
        for tc in test_cases:
            if not isinstance(tc, dict):
                continue
            if not tc.get("Testcase name") or not tc.get("Test steps"):
                continue
            valid_cases.append(tc)

        iteration = state.get("iteration", 0) + 1

        return {
            "current_batch": valid_cases,
            "iteration": iteration,
            "messages": [
                f"✓ Iteration {iteration}: Generated {len(valid_cases)} test cases (target {batch_target})"
            ],
        }

    except Exception as exc:
        print(f"[ERROR] Test generation failed: {exc}")
        return {
            "current_batch": [],
            "iteration": state.get("iteration", 0) + 1,
            "messages": [f"✗ Generation failed: {str(exc)}"],
        }
