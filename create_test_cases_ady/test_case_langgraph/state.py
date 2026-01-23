"""
Shared state that flows through the LangGraph workflow.
"""

from operator import add
from typing import Any, Dict, List, Optional, TypedDict

from typing_extensions import Annotated


class TestCaseState(TypedDict):
    """
    State object shared across all nodes in the graph.
    """

    # ========================================================================
    # INPUT CONTEXT (initialized at start)
    # ========================================================================
    feature_id: int
    feature_name: str
    feature_description: str
    platform: str  # "web" or "android"
    user_guide_text: str
    feature_summary_text: str
    screen_contracts_json: str  # JSON string of screen/page contracts
    max_testcases: int

    # ========================================================================
    # ANALYSIS PHASE (output from feature_analyzer)
    # ========================================================================
    feature_analysis: Optional[str]
    user_flows: List[Dict[str, Any]]
    test_scenarios: List[Dict[str, Any]]

    # ========================================================================
    # GENERATION TRACKING
    # ========================================================================
    iteration: int  # Current iteration number
    max_iterations: int  # Maximum allowed iterations (default: 5)
    batch_size: int  # Test cases to generate per iteration (default: 5)

    # Current batch of generated test cases
    current_batch: List[Dict[str, Any]]

    # ========================================================================
    # REFLEXION EVALUATION (output from reflexion_evaluator)
    # ========================================================================
    # Cumulative lists (use 'add' operator to append across iterations)
    approved_testcases: Annotated[List[Dict[str, Any]], add]
    rejected_testcases: Annotated[List[Dict[str, Any]], add]

    # Feedback for next generation iteration
    reflexion_feedback: Optional[str]
    quality_issues: List[str]

    # Tracking coverage to avoid duplicates
    covered_scenarios: List[str]  # Scenario names already covered
    covered_test_titles: List[str]  # Test case titles already used

    # ========================================================================
    # TERMINATION CONTROL
    # ========================================================================
    should_continue: bool  # Whether to continue generating
    termination_reason: Optional[str]  # Why we stopped

    # ========================================================================
    # LOGGING & METRICS
    # ========================================================================
    messages: Annotated[List[str], add]  # Progress log messages
    metrics: Dict[str, Any]  # Quality metrics
