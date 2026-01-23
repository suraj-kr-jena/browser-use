"""
Main TestCaseAgent class - entry point for create_test_cases.py
"""

from typing import Any, Dict, List, Optional

from .config import GenerationConfig
from .graph import create_test_case_graph
from .state import TestCaseState


class TestCaseAgent:
    """
    Main agent for test case generation using LangGraph + Reflexion.
    """

    def __init__(self, llm: Any, config: Optional[GenerationConfig] = None):
        self.llm = llm
        self.config = config or GenerationConfig()
        self.graph = create_test_case_graph(llm)

    def generate_test_cases(
        self,
        user_guide_text: str,
        max_cases_per_feature: int,
        platform: str,
    ) -> List[Dict[str, Any]]:
        """
        Generate test cases using the Reflexion workflow.
        """

        max_testcases = max_cases_per_feature or self.config.max_testcases

        initial_state: TestCaseState = {
            "feature_id": 0,
            "feature_name": "",
            "feature_description": "",
            "platform": platform,
            "user_guide_text": user_guide_text,
            "feature_summary_text": "",
            "screen_contracts_json": "[]",
            "max_testcases": max_testcases,
            # Analysis outputs
            "feature_analysis": None,
            "user_flows": [],
            "test_scenarios": [],
            # Generation tracking
            "iteration": 0,
            "max_iterations": self.config.max_iterations,
            "batch_size": self.config.batch_size,
            "current_batch": [],
            # Reflexion outputs
            "approved_testcases": [],
            "rejected_testcases": [],
            "reflexion_feedback": None,
            "quality_issues": [],
            "covered_scenarios": [],
            "covered_test_titles": [],
            # Termination
            "should_continue": True,
            "termination_reason": None,
            # Logging
            "messages": [],
            "metrics": {},
        }

        print("\n[AGENT] Starting Reflexion workflow")
        print(
            f"[AGENT] Target: {max_cases_per_feature} test cases, Max iterations: {self.config.max_iterations}"
        )

        try:
            final_state = self.graph.invoke(initial_state)

            for msg in final_state.get("messages", []):
                print(f"[AGENT] {self._safe_console_text(str(msg))}")

            approved = final_state.get("approved_testcases", [])

            print(
                f"\n[AGENT] Workflow complete: {len(approved)} approved test cases"
            )
            if final_state.get("termination_reason"):
                print(f"[AGENT] Reason: {final_state['termination_reason']}")

            return approved

        except Exception as exc:
            print(f"[AGENT] Workflow failed: {exc}")
            import traceback

            traceback.print_exc()
            return []

    @staticmethod
    def _safe_console_text(text: str) -> str:
        replacements = {
            "✓": "OK",
            "⚠": "WARN",
            "✗": "ERR",
            "🛑": "STOP",
        }
        for src, dst in replacements.items():
            text = text.replace(src, dst)
        return text.encode("ascii", "backslashreplace").decode("ascii")
