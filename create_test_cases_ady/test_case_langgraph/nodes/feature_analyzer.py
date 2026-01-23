"""
Node: Feature Analyzer

Analyzes the feature context and extracts user flows and test scenarios.
"""

from typing import Any, Dict

from ..state import TestCaseState
from ..utils.parsers import parse_llm_json
from ..utils.prompt_templates import PromptTemplates


def analyze_feature_node(state: TestCaseState, llm: Any) -> Dict[str, Any]:
    """
    Analyze feature to extract user flows and test scenarios.

    This runs ONCE at the start of the workflow.
    """

    prompt = PromptTemplates.FEATURE_ANALYSIS.format(
        feature_name=state["feature_name"],
        feature_description=state["feature_description"],
        platform=state["platform"],
        user_guide_text=state["user_guide_text"],
        feature_summary_text=state["feature_summary_text"],
        screen_contracts_json=state["screen_contracts_json"],
    )

    response = llm.invoke(prompt)
    content = response.content if hasattr(response, "content") else str(response)

    try:
        analysis_data = parse_llm_json(content)

        user_flows = analysis_data.get("user_flows", [])
        test_scenarios = analysis_data.get("test_scenarios", [])

        return {
            "feature_analysis": content,
            "user_flows": user_flows,
            "test_scenarios": test_scenarios,
            "messages": [
                f"✓ Feature analysis complete: {len(user_flows)} flows, {len(test_scenarios)} scenarios identified"
            ],
        }

    except Exception as exc:
        print(f"[WARN] Feature analysis parsing failed: {exc}")
        return {
            "feature_analysis": content,
            "user_flows": [],
            "test_scenarios": [],
            "messages": ["⚠ Feature analysis completed with parsing issues"],
        }
