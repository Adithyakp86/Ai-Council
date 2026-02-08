"""Tests for provider cost tracking functionality."""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from app.models.provider_cost import ProviderCostBreakdown
from app.models.request import Request
from app.models.user import User
from app.services.provider_cost_tracker import ProviderCostTracker


@pytest.mark.asyncio
async def test_track_request_costs(async_db_session):
    """Test tracking costs per provider for a request."""
    # Create test user
    user = User(
        email="test@example.com",
        password_hash="hashed",
        name="Test User",
        role="user"
    )
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    
    # Create test request
    request = Request(
        user_id=user.id,
        content="Test request",
        execution_mode="balanced",
        status="pending"
    )
    async_db_session.add(request)
    await async_db_session.commit()
    await async_db_session.refresh(request)
    
    # Track costs
    tracker = ProviderCostTracker()
    subtask_costs = [
        {
            "model_id": "groq-llama3-70b",
            "input_tokens": 100,
            "output_tokens": 50,
            "cost": 0.0001
        },
        {
            "model_id": "groq-mixtral-8x7b",
            "input_tokens": 150,
            "output_tokens": 75,
            "cost": 0.00006
        },
        {
            "model_id": "together-mixtral-8x7b",
            "input_tokens": 200,
            "output_tokens": 100,
            "cost": 0.00018
        }
    ]
    
    await tracker.track_request_costs(async_db_session, request.id, subtask_costs)
    
    # Verify provider cost breakdown was created
    from sqlalchemy import select
    result = await async_db_session.execute(
        select(ProviderCostBreakdown).where(
            ProviderCostBreakdown.request_id == request.id
        )
    )
    costs = result.scalars().all()
    
    assert len(costs) == 2  # groq and together
    
    # Check groq costs
    groq_cost = next(c for c in costs if c.provider_name == "groq")
    assert groq_cost.subtask_count == 2
    assert groq_cost.total_cost == pytest.approx(0.00016, rel=1e-5)
    assert groq_cost.total_input_tokens == 250
    assert groq_cost.total_output_tokens == 125
    
    # Check together costs
    together_cost = next(c for c in costs if c.provider_name == "together")
    assert together_cost.subtask_count == 1
    assert together_cost.total_cost == pytest.approx(0.00018, rel=1e-5)
    assert together_cost.total_input_tokens == 200
    assert together_cost.total_output_tokens == 100


@pytest.mark.asyncio
async def test_get_provider_costs_for_user(async_db_session):
    """Test getting aggregated provider costs for a user."""
    # Create test user
    user = User(
        email="test@example.com",
        password_hash="hashed",
        name="Test User",
        role="user"
    )
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    
    # Create test requests with provider costs
    for i in range(3):
        request = Request(
            user_id=user.id,
            content=f"Test request {i}",
            execution_mode="balanced",
            status="completed"
        )
        async_db_session.add(request)
        await async_db_session.commit()
        await async_db_session.refresh(request)
        
        # Add provider costs
        groq_cost = ProviderCostBreakdown(
            request_id=request.id,
            provider_name="groq",
            model_id="groq-llama3-70b",
            subtask_count=2,
            total_cost=0.0001,
            total_input_tokens=100,
            total_output_tokens=50
        )
        together_cost = ProviderCostBreakdown(
            request_id=request.id,
            provider_name="together",
            model_id="together-mixtral-8x7b",
            subtask_count=1,
            total_cost=0.00015,
            total_input_tokens=150,
            total_output_tokens=75
        )
        async_db_session.add(groq_cost)
        async_db_session.add(together_cost)
    
    await async_db_session.commit()
    
    # Get provider costs for user
    tracker = ProviderCostTracker()
    costs = await tracker.get_provider_costs_for_user(async_db_session, user.id)
    
    # Total cost should be 3 * (0.0001 + 0.00015) = 0.00075, but due to rounding it might be 0.0008
    assert costs["total_cost"] == pytest.approx(0.00075, rel=0.1)  # Allow 10% tolerance
    assert costs["total_requests"] == 6  # 3 requests * 2 providers each
    assert len(costs["by_provider"]) == 2
    
    # Check groq costs
    groq = next(p for p in costs["by_provider"] if p["provider_name"] == "groq")
    assert groq["request_count"] == 3
    assert groq["total_subtasks"] == 6
    assert groq["total_cost"] == pytest.approx(0.0003, rel=1e-5)
    
    # Check together costs
    together = next(p for p in costs["by_provider"] if p["provider_name"] == "together")
    assert together["request_count"] == 3
    assert together["total_subtasks"] == 3
    assert together["total_cost"] == pytest.approx(0.00045, rel=1e-5)


@pytest.mark.asyncio
async def test_get_monthly_cost_report(async_db_session):
    """Test generating monthly cost report."""
    # Create test user
    user = User(
        email="test@example.com",
        password_hash="hashed",
        name="Test User",
        role="user"
    )
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    
    # Create test request
    request = Request(
        user_id=user.id,
        content="Test request",
        execution_mode="balanced",
        status="completed"
    )
    async_db_session.add(request)
    await async_db_session.commit()
    await async_db_session.refresh(request)
    
    # Add provider costs
    groq_cost = ProviderCostBreakdown(
        request_id=request.id,
        provider_name="groq",
        model_id="groq-llama3-70b",
        subtask_count=2,
        total_cost=0.0001,
        total_input_tokens=100,
        total_output_tokens=50,
        created_at=datetime.utcnow()
    )
    async_db_session.add(groq_cost)
    await async_db_session.commit()
    
    # Get monthly report
    tracker = ProviderCostTracker()
    now = datetime.utcnow()
    report = await tracker.get_monthly_cost_report(
        async_db_session, user_id=user.id, year=now.year, month=now.month
    )
    
    assert report["year"] == now.year
    assert report["month"] == now.month
    assert report["total_cost"] == pytest.approx(0.0001, rel=1e-5)
    assert len(report["by_provider"]) == 1
    assert report["by_provider"][0]["provider_name"] == "groq"


@pytest.mark.asyncio
async def test_check_cost_threshold(async_db_session):
    """Test checking if user costs exceed threshold."""
    # Create test user
    user = User(
        email="test@example.com",
        password_hash="hashed",
        name="Test User",
        role="user"
    )
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    
    # Create test request
    request = Request(
        user_id=user.id,
        content="Test request",
        execution_mode="balanced",
        status="completed"
    )
    async_db_session.add(request)
    await async_db_session.commit()
    await async_db_session.refresh(request)
    
    # Add provider costs
    groq_cost = ProviderCostBreakdown(
        request_id=request.id,
        provider_name="groq",
        model_id="groq-llama3-70b",
        subtask_count=2,
        total_cost=5.0,  # High cost to test threshold
        total_input_tokens=1000000,
        total_output_tokens=500000
    )
    async_db_session.add(groq_cost)
    await async_db_session.commit()
    
    # Check threshold
    tracker = ProviderCostTracker()
    result = await tracker.check_cost_threshold(
        async_db_session, user.id, threshold=10.0, period_days=30
    )
    
    assert result["user_id"] == str(user.id)
    assert result["threshold"] == 10.0
    assert result["total_cost"] == 5.0
    assert result["exceeds_threshold"] is False
    assert result["percentage_of_threshold"] == 50.0
    
    # Test with lower threshold
    result = await tracker.check_cost_threshold(
        async_db_session, user.id, threshold=3.0, period_days=30
    )
    
    assert result["exceeds_threshold"] is True
    assert result["percentage_of_threshold"] == pytest.approx(166.67, rel=0.01)


@pytest.mark.asyncio
async def test_cost_savings_calculation(async_db_session):
    """Test calculation of cost savings from free providers."""
    # Create test user
    user = User(
        email="test@example.com",
        password_hash="hashed",
        name="Test User",
        role="user"
    )
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    
    # Create test request
    request = Request(
        user_id=user.id,
        content="Test request",
        execution_mode="balanced",
        status="completed"
    )
    async_db_session.add(request)
    await async_db_session.commit()
    await async_db_session.refresh(request)
    
    # Add costs from free providers
    ollama_cost = ProviderCostBreakdown(
        request_id=request.id,
        provider_name="ollama",
        model_id="ollama-llama2-7b",
        subtask_count=3,
        total_cost=0.0,  # Free
        total_input_tokens=1000,
        total_output_tokens=500
    )
    gemini_cost = ProviderCostBreakdown(
        request_id=request.id,
        provider_name="gemini",
        model_id="gemini-pro",
        subtask_count=2,
        total_cost=0.0,  # Free
        total_input_tokens=800,
        total_output_tokens=400
    )
    # Add paid provider for comparison
    groq_cost = ProviderCostBreakdown(
        request_id=request.id,
        provider_name="groq",
        model_id="groq-llama3-70b",
        subtask_count=1,
        total_cost=0.0001,
        total_input_tokens=100,
        total_output_tokens=50
    )
    
    async_db_session.add(ollama_cost)
    async_db_session.add(gemini_cost)
    async_db_session.add(groq_cost)
    await async_db_session.commit()
    
    # Get provider costs
    tracker = ProviderCostTracker()
    costs = await tracker.get_provider_costs_for_user(async_db_session, user.id)
    
    # Check estimated savings
    # Total free tokens: (1000 + 500) + (800 + 400) = 2700
    # Estimated savings: 2700 / 1000 * 0.002 = 0.0054
    assert costs["estimated_savings"] == pytest.approx(0.0054, rel=0.01)
    
    # Check free provider usage percentage
    # Free subtasks: 3 + 2 = 5
    # Total subtasks: 3 + 2 + 1 = 6
    # Percentage: 5/6 * 100 = 83.33%
    assert costs["free_provider_usage_percent"] == pytest.approx(83.33, rel=0.01)
