"""Property test for cost estimate based on length.

**Property 37: Cost Estimate Based on Length**
**Validates: Requirements 18.4**

This test verifies that longer requests have higher cost estimates.
"""

import pytest
from hypothesis import given, strategies as st, assume
from app.services.cost_estimator import CostEstimator


# Strategy for generating request lengths (reasonable range)
request_length_strategy = st.integers(min_value=10, max_value=5000)


@given(
    length1=request_length_strategy,
    length2=request_length_strategy
)
def test_longer_requests_have_higher_estimates(length1, length2):
    """Property: Longer requests have higher cost estimates.
    
    **Validates: Requirements 18.4**
    
    For any two request lengths where length1 < length2, the cost estimate
    for length2 should be greater than or equal to the estimate for length1.
    
    This ensures that cost estimates scale appropriately with request complexity.
    """
    # Ensure length1 < length2
    assume(length1 < length2)
    
    estimator = CostEstimator()
    
    # Test for all execution modes
    for mode in ["fast", "balanced", "best_quality"]:
        cost1 = estimator.estimate_cost_for_mode(length1, mode)
        cost2 = estimator.estimate_cost_for_mode(length2, mode)
        
        assert cost2 >= cost1, (
            f"Cost for longer request (length={length2}, cost={cost2}) should be ≥ "
            f"cost for shorter request (length={length1}, cost={cost1}) in {mode} mode"
        )


@given(
    base_length=st.integers(min_value=10, max_value=2500),
    multiplier=st.integers(min_value=2, max_value=10)
)
def test_cost_scales_with_length_multiplier(base_length, multiplier):
    """Property: Cost increases when length is multiplied.
    
    **Validates: Requirements 18.4**
    
    When request length is multiplied by N, the cost should increase
    (though not necessarily by exactly N due to fixed overhead).
    """
    estimator = CostEstimator()
    
    longer_length = base_length * multiplier
    
    for mode in ["fast", "balanced", "best_quality"]:
        base_cost = estimator.estimate_cost_for_mode(base_length, mode)
        longer_cost = estimator.estimate_cost_for_mode(longer_length, mode)
        
        # Cost should increase
        assert longer_cost > base_cost, (
            f"Cost for {multiplier}x longer request should be greater. "
            f"Base: length={base_length}, cost={base_cost}. "
            f"Longer: length={longer_length}, cost={longer_cost} in {mode} mode"
        )
        
        # Cost should scale reasonably (at least proportional to multiplier)
        # Allow some tolerance for rounding and overhead
        min_expected_cost = base_cost * (multiplier * 0.8)  # 80% of linear scaling
        assert longer_cost >= min_expected_cost, (
            f"Cost should scale reasonably with length. "
            f"Expected at least {min_expected_cost}, got {longer_cost} "
            f"for {multiplier}x increase in {mode} mode"
        )


@given(request_length=request_length_strategy)
def test_zero_length_has_minimal_cost(request_length):
    """Property: Very short requests have lower cost than longer requests.
    
    **Validates: Requirements 18.4**
    
    A minimal request (10 chars) should have lower cost than any longer request.
    """
    assume(request_length > 10)
    
    estimator = CostEstimator()
    
    minimal_length = 10
    
    for mode in ["fast", "balanced", "best_quality"]:
        minimal_cost = estimator.estimate_cost_for_mode(minimal_length, mode)
        longer_cost = estimator.estimate_cost_for_mode(request_length, mode)
        
        assert longer_cost >= minimal_cost, (
            f"Longer request (length={request_length}, cost={longer_cost}) should have "
            f"cost ≥ minimal request (length={minimal_length}, cost={minimal_cost}) "
            f"in {mode} mode"
        )


@given(
    length1=request_length_strategy,
    length2=request_length_strategy,
    length3=request_length_strategy
)
def test_cost_ordering_is_transitive(length1, length2, length3):
    """Property: Cost ordering is transitive.
    
    **Validates: Requirements 18.4**
    
    If length1 < length2 < length3, then cost1 ≤ cost2 ≤ cost3.
    """
    # Sort lengths
    lengths = sorted([length1, length2, length3])
    assume(lengths[0] < lengths[1] < lengths[2])  # Ensure strict ordering
    
    estimator = CostEstimator()
    
    for mode in ["fast", "balanced", "best_quality"]:
        cost1 = estimator.estimate_cost_for_mode(lengths[0], mode)
        cost2 = estimator.estimate_cost_for_mode(lengths[1], mode)
        cost3 = estimator.estimate_cost_for_mode(lengths[2], mode)
        
        # Verify transitive ordering
        assert cost1 <= cost2 <= cost3, (
            f"Cost ordering should be transitive in {mode} mode. "
            f"Lengths: {lengths[0]} < {lengths[1]} < {lengths[2]}. "
            f"Costs: {cost1}, {cost2}, {cost3}"
        )


@given(
    base_length=st.integers(min_value=100, max_value=1000),
    increment=st.integers(min_value=1, max_value=100)
)
def test_cost_increases_monotonically(base_length, increment):
    """Property: Cost increases monotonically with length.
    
    **Validates: Requirements 18.4**
    
    Adding any positive increment to request length should not decrease cost.
    """
    estimator = CostEstimator()
    
    longer_length = base_length + increment
    
    for mode in ["fast", "balanced", "best_quality"]:
        base_cost = estimator.estimate_cost_for_mode(base_length, mode)
        longer_cost = estimator.estimate_cost_for_mode(longer_length, mode)
        
        assert longer_cost >= base_cost, (
            f"Adding {increment} chars should not decrease cost in {mode} mode. "
            f"Base: length={base_length}, cost={base_cost}. "
            f"Longer: length={longer_length}, cost={longer_cost}"
        )


@given(request_length=request_length_strategy)
def test_time_estimate_increases_with_length(request_length):
    """Property: Time estimates also increase with request length.
    
    **Validates: Requirements 18.4**
    
    Similar to cost, time estimates should increase with request length.
    """
    estimator = CostEstimator()
    
    # Compare with a shorter request
    shorter_length = max(10, request_length // 2)
    assume(shorter_length < request_length)
    
    for mode in ["fast", "balanced", "best_quality"]:
        shorter_estimate = estimator.estimate_with_time(shorter_length, mode)
        longer_estimate = estimator.estimate_with_time(request_length, mode)
        
        shorter_time = shorter_estimate["estimated_time_seconds"]
        longer_time = longer_estimate["estimated_time_seconds"]
        
        assert longer_time >= shorter_time, (
            f"Time for longer request (length={request_length}, time={longer_time}s) "
            f"should be ≥ time for shorter request (length={shorter_length}, time={shorter_time}s) "
            f"in {mode} mode"
        )


@given(
    length1=request_length_strategy,
    length2=request_length_strategy
)
def test_cost_difference_proportional_to_length_difference(length1, length2):
    """Property: Cost difference is roughly proportional to length difference.
    
    **Validates: Requirements 18.4**
    
    The ratio of costs should be related to the ratio of lengths.
    """
    assume(length1 > 10 and length2 > 10)  # Avoid division by very small numbers
    assume(abs(length1 - length2) > 10)  # Ensure meaningful difference
    
    estimator = CostEstimator()
    
    for mode in ["fast", "balanced", "best_quality"]:
        cost1 = estimator.estimate_cost_for_mode(length1, mode)
        cost2 = estimator.estimate_cost_for_mode(length2, mode)
        
        # Both costs should be positive
        assume(cost1 > 0 and cost2 > 0)
        
        # Calculate ratios
        length_ratio = max(length1, length2) / min(length1, length2)
        cost_ratio = max(cost1, cost2) / min(cost1, cost2)
        
        # Cost ratio should be at least somewhat related to length ratio
        # Allow generous tolerance since there's overhead and rounding
        assert cost_ratio >= 1.0, (
            f"Cost ratio should be ≥ 1 when lengths differ in {mode} mode"
        )
        
        # Cost shouldn't scale wildly more than length
        # (e.g., 2x length shouldn't be 100x cost)
        max_reasonable_ratio = length_ratio * 2  # Allow 2x overhead
        assert cost_ratio <= max_reasonable_ratio, (
            f"Cost ratio ({cost_ratio:.2f}) should not exceed {max_reasonable_ratio:.2f} "
            f"for length ratio {length_ratio:.2f} in {mode} mode. "
            f"Lengths: {length1}, {length2}. Costs: {cost1}, {cost2}"
        )
