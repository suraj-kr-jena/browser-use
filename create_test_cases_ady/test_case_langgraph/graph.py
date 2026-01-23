"""
LangGraph workflow definition with Reflexion feedback loop.
"""

from langgraph.graph import END, StateGraph

from .nodes import (
    aggregate_results_node,
    analyze_feature_node,
    evaluate_test_cases_node,
    generate_test_cases_node,
)
from .state import TestCaseState


def should_continue_generation(state: TestCaseState) -> str:
    """
    Routing function: decide whether to continue or finalize.
    """
    if state.get("should_continue", True):
        return "generate"
    return "finalize"


def create_test_case_graph(llm):
    """
    Build the LangGraph workflow.
    """

    workflow = StateGraph(TestCaseState)

    workflow.add_node("analyze", lambda state: analyze_feature_node(state, llm))
    workflow.add_node("generate", lambda state: generate_test_cases_node(state, llm))
    workflow.add_node("evaluate", lambda state: evaluate_test_cases_node(state, llm))
    workflow.add_node("finalize", aggregate_results_node)

    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "generate")
    workflow.add_edge("generate", "evaluate")

    workflow.add_conditional_edges(
        "evaluate",
        should_continue_generation,
        {
            "generate": "generate",
            "finalize": "finalize",
        },
    )

    workflow.add_edge("finalize", END)

    return workflow.compile()
