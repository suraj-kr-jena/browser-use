# LangGraph Test Case Generation with Reflexion

## Overview

This module implements a Reflexion-based test case generation system using LangGraph. It generates high-quality UI test cases through an iterative generate-evaluate-refine loop.

## Architecture

```
+-----------+
| ANALYZE   |  <- Understand feature context
+-----+-----+
      |
      v
+-----------+
| GENERATE  |  <- Create batch of test cases
+-----+-----+
      |
      v
+-----------+
| EVALUATE  |  <- Reflexion critic (approve/reject)
+-----+-----+
      |
      v
+-----------+
| FINALIZE  |  <- Renumber and return approved cases
+-----------+
```

## Project Layout

```
test_case_langgraph/
├── __init__.py
├── agent.py
├── graph.py
├── state.py
├── config.py
├── nodes/
│   ├── feature_analyzer.py
│   ├── test_generator.py
│   ├── reflexion_evaluator.py
│   └── result_aggregator.py
└── utils/
    ├── prompt_templates.py
    └── parsers.py
```

## How It Runs

- `create_test_cases.py` builds the LLM using `llm.py` and then creates `TestCaseAgent`.
- `TestCaseAgent.generate_test_cases(...)` builds the initial state and runs the LangGraph workflow.
- The graph loops `generate -> evaluate` until it reaches `max_testcases`, hits `max_iterations`, or a batch yields zero approvals.

## Inputs and Outputs

Input arguments (passed from `create_test_cases.py`):
- `feature` (dict with `feature_id`, `feature_name`, `feature_description`)
- `user_guide_text`
- `feature_summary_text`
- `screen_contracts_json` (optional; defaults to "[]")
- `max_cases_per_feature`
- `platform`

Output:
- List of approved test case dicts with keys:
  `TC_ID`, `category`, `Testcase name`, `Precondition`, `Test steps`,
  `Test data`, `Expected Result`

## Configuration

Defaults live in `config.py`:
- `max_iterations`: 8
- `batch_size`: 8
- `max_testcases`: 50

These can be overridden by passing a custom `GenerationConfig` to `TestCaseAgent`.

## Notes

- The evaluator is LLM-based (not strict string dedupe). It checks authenticity, redundancy, and quality per prompt.
- `result_aggregator` is deterministic; it renumbers approved test cases as `TC001`, `TC002`, etc.
