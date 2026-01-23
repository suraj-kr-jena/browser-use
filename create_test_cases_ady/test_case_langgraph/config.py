"""
Configuration and constants for test case generation.
"""

from dataclasses import dataclass


@dataclass
class GenerationConfig:
    """Configuration for the test case generation workflow."""

    # Generation limits
    max_iterations: int = 8
    batch_size: int = 8  # Test cases per iteration
    max_testcases: int = 50

    # Quality thresholds
    min_approval_rate: float = 0.6  # 60% of batch must be approved

    # Termination conditions
    min_new_approvals_per_iteration: int = 1  # Must get at least 1 approval
    stagnation_threshold: int = 2  # Stop if no progress for N iterations

    # Defaults
    created_type: str = "llm_reflexion"
    created_by: str = "langgraph_reflexion"
