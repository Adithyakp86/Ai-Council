"""Property test for cost calculation accuracy.

**Property 3: Cost Calculation Accuracy**
**Validates: Requirements 1.6**

This test verifies that the calculated cost matches the sum of individual token costs.
"""

import pytest
from hypothesis import given, strategies as st, assume
from app.services.cost_calculator import CostCalculator
from app.services.cloud_ai.model_registry import MODEL_REGISTRY, get_cloud_models_only


# Strategy for generating valid model IDs
@st.composite
def model_id_strategy(draw):
    """Generate a valid model ID from the registry."""
    cloud_models = get_cloud_models_only()
    assume(len(cloud_models) > 0)
    return draw(st.sampled_from(cloud_models))


# Strategy for generating token counts (reasonable range)
token_count_strategy = st.integers(min_value=1, max_value=100000)


# Strategy for generating subtask cost data
@st.composite
def subtask_cost_data_strategy(draw):
    """Generate a subtask cost data dictionary."""
    model_id = draw(model_id_strategy())
    input_tokens = draw(token_count_strategy)
    output_tokens = draw(token_count_strategy)
    
    return {
        "subtask_id": f"subtask-{draw(st.integers(min_value=1, max_value=1000))}",
        "model_id": model_id,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens
    }


# Strategy for generating a list of subtask costs
subtask_costs_list_strategy = st.lists(
    subtask_cost_data_strategy(),
    min_size=1,
    max_size=20
)


@given(
    model_id=model_id_strategy(),
    input_tokens=token_count_strategy,
    output_tokens=token_count_strategy
)
def test_subtask_cost_matches_manual_calculation(model_id, input_tokens, output_tokens):
    """Property: Subtask cost equals input_tokens × cost_per_input + output_tokens × cost_per_output.
    
    **Validates: Requirements 1.6**
    
    For any valid model and token counts, the calculated cost should exactly match
    the manual calculation using the model's pricing.
    """
    calculator = CostCalculator()
    
    # Get model pricing
    model_config = MODEL_REGISTRY[model_id]
    cost_per_input = model_config["cost_per_input_token"]
    cost_per_output = model_config["cost_per_output_token"]
    
    # Calculate cost using the service
    calculated_cost = calculator.calculate_subtask_cost(
        model_id=model_id,
        input_tokens=input_tokens,
        output_tokens=output_tokens
    )
    
    # Manual calculation
    expected_cost = (input_tokens * cost_per_input) + (output_tokens * cost_per_output)
    
    # Verify they match (using small epsilon for floating point comparison)
    assert abs(calculated_cost - expected_cost) < 1e-10, (
        f"Cost mismatch for {model_id}: "
        f"calculated={calculated_cost}, expected={expected_cost}"
    )


@given(subtask_costs=subtask_costs_list_strategy)
def test_total_cost_equals_sum_of_subtask_costs(subtask_costs):
    """Property: Total cost equals the sum of all individual subtask costs.
    
    **Validates: Requirements 1.6**
    
    For any list of subtasks, the total cost should equal the sum of
    calculating each subtask's cost individually.
    """
    calculator = CostCalculator()
    
    # Calculate total cost using the service
    total_cost = calculator.calculate_total_cost(subtask_costs)
    
    # Calculate sum of individual costs
    expected_total = 0.0
    for subtask in subtask_costs:
        individual_cost = calculator.calculate_subtask_cost(
            model_id=subtask["model_id"],
            input_tokens=subtask["input_tokens"],
            output_tokens=subtask["output_tokens"]
        )
        expected_total += individual_cost
    
    # Verify they match (using small epsilon for floating point comparison)
    assert abs(total_cost - expected_total) < 1e-8, (
        f"Total cost mismatch: calculated={total_cost}, expected={expected_total}"
    )


@given(subtask_costs=subtask_costs_list_strategy)
def test_cost_breakdown_total_matches_sum(subtask_costs):
    """Property: Cost breakdown total matches the sum of all subtask costs.
    
    **Validates: Requirements 1.6**
    
    The total_cost in the breakdown should equal the sum of costs in by_subtask.
    """
    calculator = CostCalculator()
    
    # Create cost breakdown
    breakdown = calculator.create_cost_breakdown(subtask_costs)
    
    # Sum costs from by_subtask
    sum_by_subtask = sum(item["cost"] for item in breakdown["by_subtask"])
    
    # Verify total_cost matches
    assert abs(breakdown["total_cost"] - sum_by_subtask) < 1e-8, (
        f"Breakdown total mismatch: total_cost={breakdown['total_cost']}, "
        f"sum_by_subtask={sum_by_subtask}"
    )


@given(subtask_costs=subtask_costs_list_strategy)
def test_cost_breakdown_by_model_matches_sum(subtask_costs):
    """Property: Sum of costs by model equals total cost.
    
    **Validates: Requirements 1.6**
    
    The sum of all model costs in by_model should equal the total_cost.
    """
    calculator = CostCalculator()
    
    # Create cost breakdown
    breakdown = calculator.create_cost_breakdown(subtask_costs)
    
    # Sum costs from by_model
    sum_by_model = sum(breakdown["by_model"].values())
    
    # Verify total_cost matches
    assert abs(breakdown["total_cost"] - sum_by_model) < 1e-8, (
        f"By-model sum mismatch: total_cost={breakdown['total_cost']}, "
        f"sum_by_model={sum_by_model}"
    )


@given(subtask_costs=subtask_costs_list_strategy)
def test_token_counts_aggregate_correctly(subtask_costs):
    """Property: Total token counts equal sum of individual token counts.
    
    **Validates: Requirements 1.6**
    
    The total_input_tokens and total_output_tokens should equal the sum
    of all individual subtask token counts.
    """
    calculator = CostCalculator()
    
    # Create cost breakdown
    breakdown = calculator.create_cost_breakdown(subtask_costs)
    
    # Calculate expected totals
    expected_input = sum(st["input_tokens"] for st in subtask_costs)
    expected_output = sum(st["output_tokens"] for st in subtask_costs)
    
    # Verify they match
    assert breakdown["total_input_tokens"] == expected_input, (
        f"Input token mismatch: got={breakdown['total_input_tokens']}, "
        f"expected={expected_input}"
    )
    assert breakdown["total_output_tokens"] == expected_output, (
        f"Output token mismatch: got={breakdown['total_output_tokens']}, "
        f"expected={expected_output}"
    )


@given(
    model_id=model_id_strategy(),
    input_tokens=token_count_strategy,
    output_tokens=token_count_strategy
)
def test_cost_is_non_negative(model_id, input_tokens, output_tokens):
    """Property: Cost is always non-negative.
    
    **Validates: Requirements 1.6**
    
    For any valid inputs, the calculated cost should never be negative.
    """
    calculator = CostCalculator()
    
    cost = calculator.calculate_subtask_cost(
        model_id=model_id,
        input_tokens=input_tokens,
        output_tokens=output_tokens
    )
    
    assert cost >= 0, f"Cost should be non-negative, got {cost}"


@given(
    model_id=model_id_strategy(),
    tokens=token_count_strategy
)
def test_cost_scales_linearly_with_tokens(model_id, tokens):
    """Property: Cost scales linearly with token count.
    
    **Validates: Requirements 1.6**
    
    Doubling the token count should double the cost.
    """
    calculator = CostCalculator()
    
    # Calculate cost for base tokens
    cost_1x = calculator.calculate_subtask_cost(
        model_id=model_id,
        input_tokens=tokens,
        output_tokens=tokens
    )
    
    # Calculate cost for double tokens
    cost_2x = calculator.calculate_subtask_cost(
        model_id=model_id,
        input_tokens=tokens * 2,
        output_tokens=tokens * 2
    )
    
    # Verify 2x tokens = 2x cost (with small epsilon for floating point)
    expected_cost_2x = cost_1x * 2
    assert abs(cost_2x - expected_cost_2x) < 1e-8, (
        f"Cost should scale linearly: cost_1x={cost_1x}, cost_2x={cost_2x}, "
        f"expected_2x={expected_cost_2x}"
    )
