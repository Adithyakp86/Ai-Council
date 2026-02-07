"""Property test for cost estimates ordering.

**Property 36: Cost Estimates for All Modes**
**Validates: Requirements 18.1, 18.2, 18.3**

This test verifies that fast_cost ≤ balanced_cost ≤ best_quality_cost.
"""

import pytest
from hypothesis import given, strategies as st
from app.services.cost_estimator import CostEstimator


# Strategy for generating request lengths (reasonable range)
request_length_strategy = st.integers(min_value=10, max_value=5000)


@given(request_length=request_length_strategy)
def test_cost_estimates_ordering(request_length):
    """Property: fast_cost ≤ balanced_cost ≤ best_quality_cost.
    
    **Validates: Requirements 18.1, 18.2, 18.3**
    
    For any request length, the cost estimates should follow the ordering:
    FAST mode (cheapest) ≤ BALANCED mode ≤ BEST_QUALITY mode (most expensive)
    
    This ensures that users can make informed decisions about execution modes
    based on their budget constraints.
    """
    estimator = CostEstimator()
    
    # Get estimates for all modes
    estimates = estimator.estimate_all_modes(request_length)
    
    fast_cost = estimates["fast"]
    balanced_cost = estimates["balanced"]
    best_quality_cost = estimates["best_quality"]
    
    # Verify ordering
    assert fast_cost <= balanced_cost, (
        f"FAST cost ({fast_cost}) should be ≤ BALANCED cost ({balanced_cost}) "
        f"for request length {request_length}"
    )
    
    assert balanced_cost <= best_quality_cost, (
        f"BALANCED cost ({balanced_cost}) should be ≤ BEST_QUALITY cost ({best_quality_cost}) "
        f"for request length {request_length}"
    )
    
    # Transitive property: fast ≤ best_quality
    assert fast_cost <= best_quality_cost, (
        f"FAST cost ({fast_cost}) should be ≤ BEST_QUALITY cost ({best_quality_cost}) "
        f"for request length {request_length}"
    )


@given(request_length=request_length_strategy)
def test_all_estimates_non_negative(request_length):
    """Property: All cost estimates are non-negative.
    
    **Validates: Requirements 18.1, 18.2, 18.3**
    
    Cost estimates should never be negative for any execution mode.
    """
    estimator = CostEstimator()
    
    estimates = estimator.estimate_all_modes(request_length)
    
    for mode, cost in estimates.items():
        assert cost >= 0, (
            f"Cost estimate for {mode} mode should be non-negative, "
            f"got {cost} for request length {request_length}"
        )


@given(request_length=request_length_strategy)
def test_all_modes_present_in_estimates(request_length):
    """Property: Estimates include all three execution modes.
    
    **Validates: Requirements 18.1, 18.2, 18.3**
    
    The estimate_all_modes function should return estimates for all three modes.
    """
    estimator = CostEstimator()
    
    estimates = estimator.estimate_all_modes(request_length)
    
    required_modes = {"fast", "balanced", "best_quality"}
    actual_modes = set(estimates.keys())
    
    assert actual_modes == required_modes, (
        f"Estimates should include all modes. "
        f"Expected: {required_modes}, Got: {actual_modes}"
    )


@given(request_length=request_length_strategy)
def test_estimates_with_time_include_both_metrics(request_length):
    """Property: Estimates with time include both cost and time.
    
    **Validates: Requirements 18.1, 18.2, 18.3**
    
    When requesting estimates with time, both cost and time should be included.
    """
    estimator = CostEstimator()
    
    estimates = estimator.estimate_all_modes_with_time(request_length)
    
    for mode, estimate in estimates.items():
        assert "estimated_cost" in estimate, (
            f"Estimate for {mode} should include estimated_cost"
        )
        assert "estimated_time_seconds" in estimate, (
            f"Estimate for {mode} should include estimated_time_seconds"
        )
        
        # Both should be non-negative
        assert estimate["estimated_cost"] >= 0, (
            f"Cost for {mode} should be non-negative"
        )
        assert estimate["estimated_time_seconds"] >= 0, (
            f"Time for {mode} should be non-negative"
        )


@given(request_length=request_length_strategy)
def test_time_estimates_ordering(request_length):
    """Property: fast_time ≤ balanced_time ≤ best_quality_time.
    
    **Validates: Requirements 18.1, 18.2, 18.3**
    
    Time estimates should also follow the expected ordering, with FAST being
    quickest and BEST_QUALITY taking the longest.
    """
    estimator = CostEstimator()
    
    estimates = estimator.estimate_all_modes_with_time(request_length)
    
    fast_time = estimates["fast"]["estimated_time_seconds"]
    balanced_time = estimates["balanced"]["estimated_time_seconds"]
    best_quality_time = estimates["best_quality"]["estimated_time_seconds"]
    
    # Verify ordering
    assert fast_time <= balanced_time, (
        f"FAST time ({fast_time}s) should be ≤ BALANCED time ({balanced_time}s) "
        f"for request length {request_length}"
    )
    
    assert balanced_time <= best_quality_time, (
        f"BALANCED time ({balanced_time}s) should be ≤ BEST_QUALITY time ({best_quality_time}s) "
        f"for request length {request_length}"
    )


@given(
    request_length=request_length_strategy,
    mode=st.sampled_from(["fast", "balanced", "best_quality"])
)
def test_individual_mode_estimate_matches_all_modes(request_length, mode):
    """Property: Individual mode estimate matches the same mode in all_modes.
    
    **Validates: Requirements 18.1, 18.2, 18.3**
    
    Estimating a single mode should give the same result as getting all modes
    and selecting that mode.
    """
    estimator = CostEstimator()
    
    # Get individual estimate
    individual_cost = estimator.estimate_cost_for_mode(request_length, mode)
    
    # Get all estimates
    all_estimates = estimator.estimate_all_modes(request_length)
    all_modes_cost = all_estimates[mode]
    
    # They should match
    assert abs(individual_cost - all_modes_cost) < 1e-10, (
        f"Individual estimate for {mode} ({individual_cost}) should match "
        f"all_modes estimate ({all_modes_cost}) for request length {request_length}"
    )


@given(request_length=request_length_strategy)
def test_estimates_are_deterministic(request_length):
    """Property: Cost estimates are deterministic.
    
    **Validates: Requirements 18.1, 18.2, 18.3**
    
    Calling estimate_all_modes multiple times with the same input should
    return the same results.
    """
    estimator = CostEstimator()
    
    # Get estimates twice
    estimates1 = estimator.estimate_all_modes(request_length)
    estimates2 = estimator.estimate_all_modes(request_length)
    
    # They should be identical
    for mode in ["fast", "balanced", "best_quality"]:
        assert estimates1[mode] == estimates2[mode], (
            f"Estimates for {mode} should be deterministic. "
            f"Got {estimates1[mode]} and {estimates2[mode]} for length {request_length}"
        )
