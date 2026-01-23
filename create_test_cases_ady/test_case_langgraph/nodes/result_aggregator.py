"""
Node: Result Aggregator

Finalizes approved test cases with sequential IDs.
"""

from typing import Any, Dict

from ..state import TestCaseState


def aggregate_results_node(state: TestCaseState) -> Dict[str, Any]:
    """
    Finalize the approved test cases.
    """

    approved = state.get("approved_testcases", [])

    for idx, tc in enumerate(approved, start=1):
        tc["TC_ID"] = f"TC{idx:03d}"

    return {"messages": [f"✓ Finalized {len(approved)} approved test cases"]}
