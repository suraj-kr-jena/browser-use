"""
Callable wrapper for TestCaseAgent.
"""

from typing import Any, Optional
import json

from llm import LLM
from test_case_langgraph import TestCaseAgent
from test_case_langgraph.config import GenerationConfig


def generate_test_cases(
    user_guide_text: str,
    max_cases_per_feature: int,
    platform: str,
    llm: Optional[Any] = None,
    config: Optional[GenerationConfig] = None,
    output_path: Optional[str] = None,
) -> str:
    """
    Create an LLM + TestCaseAgent and return generated test cases.
    """
    if llm is None:
        llm_wrapper = LLM()
        llm = llm_wrapper.create_llm()

    # if config is None:
    #     config = GenerationConfig()

    agent = TestCaseAgent(llm, config=config)
    cases = agent.generate_test_cases(
        user_guide_text=user_guide_text,
        max_cases_per_feature=max_cases_per_feature,
        platform=platform,
    )
    cases_json = json.dumps(cases, ensure_ascii=False, indent=2)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(cases_json)
    return cases_json


def main() -> None:
    with open("C:/Users/SurajKumarJenaClouda/Documents/cursor/browser-use-ca/create_test_cases_ady/output_files/user_guide_flipkart.txt", "r", encoding="utf-8") as f:
        user_guide_text = f.read()
    max_cases_per_feature = 5
    platform = "web"

    cases_json = generate_test_cases(
        user_guide_text=user_guide_text,
        max_cases_per_feature=max_cases_per_feature,
        platform=platform,
        output_path="test_cases.txt",
    )

    print("Wrote test cases to test_cases.txt")


if __name__ == "__main__":
    main()
