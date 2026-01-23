"""
Node: Reflexion Evaluator

Evaluates generated test cases for quality, authenticity, and redundancy.
Provides feedback for the next generation iteration.
"""

import json
from typing import Any, Dict

from ..state import TestCaseState
from ..utils.parsers import parse_llm_json
from ..utils.prompt_templates import PromptTemplates


def evaluate_test_cases_node(state: TestCaseState, llm: Any) -> Dict[str, Any]:
    """
    Evaluate the current batch of test cases using Reflexion.

    Outputs:
    - approved_testcases (append to cumulative list)
    - rejected_testcases (append to cumulative list)
    - reflexion_feedback (for next iteration)
    - should_continue (termination decision)
    """

    current_batch = state.get("current_batch", [])

    if not current_batch:
        return {
            "reflexion_feedback": "No test cases generated in this iteration.",
            "should_continue": False,
            "termination_reason": "Generation produced no test cases",
            "messages": ["⚠ No test cases to evaluate"],
        }

    current_batch_json = json.dumps(current_batch, indent=2)
    approved_testcases_json = json.dumps(
        state.get("approved_testcases", []), indent=2
    )

    prompt = PromptTemplates.REFLEXION_EVALUATION.format(
        feature_name=state["feature_name"],
        current_batch_json=current_batch_json,
        approved_testcases_json=approved_testcases_json,
    )

    response = llm.invoke(prompt)
    content = response.content if hasattr(response, "content") else str(response)

    try:
        eval_data = parse_llm_json(content)

        evaluations = eval_data.get("evaluations", [])
        overall_feedback = eval_data.get("overall_feedback", "")
        suggestions = eval_data.get("suggestions_for_next_batch", [])

        newly_approved = []
        newly_rejected = []

        for eval_item in evaluations:
            tc_id = eval_item.get("TC_ID")
            decision = (eval_item.get("decision") or "").upper()

            tc = next((t for t in current_batch if t.get("TC_ID") == tc_id), None)
            if not tc:
                continue

            if decision == "APPROVE":
                tc["approval_scores"] = {
                    "authenticity": eval_item.get("authenticity_score", 0),
                    "redundancy": eval_item.get("redundancy_score", 0),
                    "quality": eval_item.get("quality_score", 0),
                }
                tc["approval_reason"] = eval_item.get("reason", "")
                newly_approved.append(tc)
            else:
                tc["rejection_reason"] = eval_item.get("reason", "")
                tc["rejection_issues"] = eval_item.get("issues", [])
                newly_rejected.append(tc)

        covered_scenarios = state.get("covered_scenarios", [])[:]
        covered_test_titles = state.get("covered_test_titles", [])[:]

        for tc in newly_approved:
            scenario = tc.get("scenario_covered", "")
            title = tc.get("Testcase name", "")
            if scenario and scenario not in covered_scenarios:
                covered_scenarios.append(scenario)
            if title and title not in covered_test_titles:
                covered_test_titles.append(title)

        feedback_parts = [f"Overall: {overall_feedback}"]
        if suggestions:
            feedback_parts.append("Suggestions:")
            feedback_parts.extend(f"- {s}" for s in suggestions)
        reflexion_feedback = "\n".join(feedback_parts)

        iteration = state.get("iteration", 0)
        max_iterations = state.get("max_iterations", 5)
        max_testcases = state.get("max_testcases", 15)

        total_approved = len(state.get("approved_testcases", [])) + len(
            newly_approved
        )

        should_continue = True
        termination_reason = None

        if total_approved >= max_testcases:
            should_continue = False
            termination_reason = (
                f"Reached target: {total_approved} approved test cases"
            )
        elif iteration >= max_iterations:
            should_continue = False
            termination_reason = f"Max iterations reached ({max_iterations})"
        elif len(newly_approved) == 0:
            should_continue = False
            termination_reason = "No new approvals in this iteration"

        messages = [
            "✓ Reflexion evaluation complete:",
            f"  - Approved: {len(newly_approved)} test cases",
            f"  - Rejected: {len(newly_rejected)} test cases",
            f"  - Total approved so far: {total_approved}",
        ]

        if not should_continue:
            messages.append(f"🛑 Stopping: {termination_reason}")

        return {
            "approved_testcases": newly_approved,
            "rejected_testcases": newly_rejected,
            "reflexion_feedback": reflexion_feedback,
            "covered_scenarios": covered_scenarios,
            "covered_test_titles": covered_test_titles,
            "should_continue": should_continue,
            "termination_reason": termination_reason,
            "messages": messages,
        }

    except Exception as exc:
        print(f"[ERROR] Reflexion evaluation failed: {exc}")
        return {
            "reflexion_feedback": f"Evaluation failed: {str(exc)}",
            "should_continue": False,
            "termination_reason": "Evaluation error",
            "messages": [f"✗ Reflexion evaluation failed: {str(exc)}"],
        }
