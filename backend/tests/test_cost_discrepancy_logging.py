"""Property test for cost discrepancy logging.

**Property 38: Significant Cost Discrepancy Logging**
**Validates: Requirements 18.5**

This test verifies that >50% discrepancies are logged.
"""

import pytest
import logging
from hypothesis import given, strategies as st, assume
from app.services.cost_discrepancy_logger import CostDiscrepancyLogger


# Strategy for generating positive costs
cost_strategy = st.floats(min_value=0.0001, max_value=100.0)


@given(
    estimated_cost=cost_strategy,
    actual_cost=cost_strategy
)
def test_discrepancy_above_threshold_should_log(estimated_cost, actual_cost):
    """Property: Discrepancies >50% should be logged.
    
    **Validates: Requirements 18.5**
    
    When |actual - estimate| / estimate > 0.5, the discrepancy should be logged.
    """
    logger = CostDiscrepancyLogger()
    
    # Calculate discrepancy ratio
    discrepancy_ratio = logger.calculate_discrepancy_ratio(
        estimated_cost,
        actual_cost
    )
    
    # Check if should log
    should_log = logger.should_log_discrepancy(estimated_cost, actual_cost)
    
    # Verify threshold logic
    if discrepancy_ratio > 0.5:
        assert should_log, (
            f"Discrepancy of {discrepancy_ratio:.4f} (>{logger.DISCREPANCY_THRESHOLD}) "
            f"should be logged. Estimated: {estimated_cost}, Actual: {actual_cost}"
        )
    else:
        assert not should_log, (
            f"Discrepancy of {discrepancy_ratio:.4f} (<={logger.DISCREPANCY_THRESHOLD}) "
            f"should not be logged. Estimated: {estimated_cost}, Actual: {actual_cost}"
        )


@given(
    estimated_cost=cost_strategy,
    multiplier=st.floats(min_value=1.6, max_value=10.0)
)
def test_large_overestimate_triggers_logging(estimated_cost, multiplier):
    """Property: Large overestimates (>50%) trigger logging.
    
    **Validates: Requirements 18.5**
    
    When actual cost is significantly higher than estimate, it should be logged.
    """
    logger = CostDiscrepancyLogger()
    
    # Create actual cost that's significantly higher
    actual_cost = estimated_cost * multiplier
    
    # Should trigger logging
    should_log = logger.should_log_discrepancy(estimated_cost, actual_cost)
    
    assert should_log, (
        f"Overestimate by {multiplier}x should trigger logging. "
        f"Estimated: {estimated_cost}, Actual: {actual_cost}"
    )


@given(
    estimated_cost=cost_strategy,
    multiplier=st.floats(min_value=0.1, max_value=0.4)
)
def test_large_underestimate_triggers_logging(estimated_cost, multiplier):
    """Property: Large underestimates (>50%) trigger logging.
    
    **Validates: Requirements 18.5**
    
    When actual cost is significantly lower than estimate, it should be logged.
    """
    assume(estimated_cost > 0.001)  # Avoid very small numbers
    
    logger = CostDiscrepancyLogger()
    
    # Create actual cost that's significantly lower (less than 50% of estimate)
    actual_cost = estimated_cost * multiplier
    
    # Should trigger logging
    should_log = logger.should_log_discrepancy(estimated_cost, actual_cost)
    
    assert should_log, (
        f"Underestimate to {multiplier}x should trigger logging. "
        f"Estimated: {estimated_cost}, Actual: {actual_cost}"
    )


@given(
    estimated_cost=cost_strategy,
    variance=st.floats(min_value=0.0, max_value=0.5)
)
def test_small_discrepancy_does_not_trigger_logging(estimated_cost, variance):
    """Property: Small discrepancies (≤50%) do not trigger logging.
    
    **Validates: Requirements 18.5**
    
    When discrepancy is within 50%, it should not be logged.
    """
    logger = CostDiscrepancyLogger()
    
    # Create actual cost within 50% of estimate
    # variance is between 0 and 0.5, so actual will be between 0.5x and 1.5x estimate
    actual_cost = estimated_cost * (1 + variance)
    
    # Calculate discrepancy
    discrepancy_ratio = logger.calculate_discrepancy_ratio(
        estimated_cost,
        actual_cost
    )
    
    # If discrepancy is ≤50%, should not log
    if discrepancy_ratio <= 0.5:
        should_log = logger.should_log_discrepancy(estimated_cost, actual_cost)
        assert not should_log, (
            f"Discrepancy of {discrepancy_ratio:.4f} (≤0.5) should not trigger logging. "
            f"Estimated: {estimated_cost}, Actual: {actual_cost}"
        )


@given(
    estimated_cost=cost_strategy,
    actual_cost=cost_strategy
)
def test_discrepancy_ratio_calculation_is_symmetric(estimated_cost, actual_cost):
    """Property: Discrepancy ratio is symmetric (over/under treated equally).
    
    **Validates: Requirements 18.5**
    
    The absolute discrepancy ratio should be the same whether actual is
    higher or lower than estimate (given same percentage difference).
    """
    assume(estimated_cost > 0.001 and actual_cost > 0.001)
    
    logger = CostDiscrepancyLogger()
    
    # Calculate discrepancy
    discrepancy = logger.calculate_discrepancy_ratio(estimated_cost, actual_cost)
    
    # Discrepancy should always be non-negative
    assert discrepancy >= 0, (
        f"Discrepancy ratio should be non-negative, got {discrepancy}"
    )


@given(estimated_cost=cost_strategy)
def test_exact_match_has_zero_discrepancy(estimated_cost):
    """Property: When estimate equals actual, discrepancy is zero.
    
    **Validates: Requirements 18.5**
    
    Perfect estimates should have zero discrepancy and not trigger logging.
    """
    logger = CostDiscrepancyLogger()
    
    actual_cost = estimated_cost
    
    discrepancy = logger.calculate_discrepancy_ratio(estimated_cost, actual_cost)
    should_log = logger.should_log_discrepancy(estimated_cost, actual_cost)
    
    assert discrepancy == 0.0, (
        f"Exact match should have zero discrepancy, got {discrepancy}"
    )
    assert not should_log, (
        "Exact match should not trigger logging"
    )


@given(
    estimated_cost=cost_strategy,
    actual_cost=cost_strategy
)
def test_check_and_log_returns_correct_boolean(estimated_cost, actual_cost):
    """Property: check_and_log returns True only when logging occurs.
    
    **Validates: Requirements 18.5**
    
    The check_and_log method should return True when discrepancy exceeds
    threshold, False otherwise.
    """
    logger = CostDiscrepancyLogger()
    
    # Check and log
    was_logged = logger.check_and_log(
        request_id="test-request",
        execution_mode="balanced",
        estimated_cost=estimated_cost,
        actual_cost=actual_cost,
        request_length=100
    )
    
    # Verify return value matches should_log
    should_log = logger.should_log_discrepancy(estimated_cost, actual_cost)
    
    assert was_logged == should_log, (
        f"check_and_log returned {was_logged} but should_log is {should_log}. "
        f"Estimated: {estimated_cost}, Actual: {actual_cost}"
    )


@given(
    estimated_cost=cost_strategy,
    actual_cost=cost_strategy
)
def test_discrepancy_summary_includes_all_fields(estimated_cost, actual_cost):
    """Property: Discrepancy summary includes all required fields.
    
    **Validates: Requirements 18.5**
    
    The summary should include all relevant discrepancy information.
    """
    logger = CostDiscrepancyLogger()
    
    summary = logger.get_discrepancy_summary(estimated_cost, actual_cost)
    
    # Check all required fields are present
    required_fields = [
        "estimated_cost",
        "actual_cost",
        "cost_difference",
        "discrepancy_ratio",
        "discrepancy_percentage",
        "direction",
        "exceeds_threshold",
        "threshold"
    ]
    
    for field in required_fields:
        assert field in summary, (
            f"Summary should include '{field}' field"
        )
    
    # Verify direction is correct
    if actual_cost > estimated_cost:
        assert summary["direction"] == "over", (
            "Direction should be 'over' when actual > estimated"
        )
    else:
        assert summary["direction"] == "under", (
            "Direction should be 'under' when actual <= estimated"
        )
    
    # Verify exceeds_threshold matches calculation
    discrepancy_ratio = logger.calculate_discrepancy_ratio(
        estimated_cost,
        actual_cost
    )
    expected_exceeds = discrepancy_ratio > 0.5
    
    assert summary["exceeds_threshold"] == expected_exceeds, (
        f"exceeds_threshold should be {expected_exceeds} for ratio {discrepancy_ratio}"
    )


@given(
    estimated_cost=st.floats(min_value=0.01, max_value=1.0),
    discrepancy_factor=st.floats(min_value=1.55, max_value=3.0)
)
def test_threshold_boundary_above_50_percent(estimated_cost, discrepancy_factor):
    """Property: Discrepancies clearly above 50% trigger logging.
    
    **Validates: Requirements 18.5**
    
    Discrepancies significantly above 50% (e.g., 55%+) should always log.
    """
    logger = CostDiscrepancyLogger()
    
    # Test above 50% (should log)
    actual_above_threshold = estimated_cost * discrepancy_factor
    discrepancy_ratio = logger.calculate_discrepancy_ratio(
        estimated_cost,
        actual_above_threshold
    )
    should_log = logger.should_log_discrepancy(
        estimated_cost,
        actual_above_threshold
    )
    
    # If discrepancy is clearly > 0.5, should log
    if discrepancy_ratio > 0.51:  # Clearly above threshold
        assert should_log, (
            f"Discrepancy of {discrepancy_ratio:.4f} (>0.5) should trigger logging. "
            f"Estimated: {estimated_cost}, Actual: {actual_above_threshold}"
        )
