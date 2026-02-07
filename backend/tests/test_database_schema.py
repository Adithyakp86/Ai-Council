"""Property-based tests for database schema integrity.

**Property: Database Foreign Key Integrity**
**Validates: Requirements 13.4, 13.5**
"""
import pytest
from hypothesis import given, strategies as st
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Request, Response, Subtask


# Hypothesis strategies for generating test data
@st.composite
def user_data(draw):
    """Generate valid user data."""
    return {
        "email": draw(st.emails()),
        "password_hash": draw(st.text(min_size=60, max_size=60)),  # bcrypt hash length
        "name": draw(st.text(min_size=1, max_size=100)),
        "role": draw(st.sampled_from(["user", "admin"])),
        "is_active": draw(st.booleans()),
    }


@st.composite
def request_data(draw):
    """Generate valid request data."""
    return {
        "content": draw(st.text(min_size=1, max_size=5000)),
        "execution_mode": draw(st.sampled_from(["fast", "balanced", "best_quality"])),
        "status": draw(st.sampled_from(["pending", "processing", "completed", "failed"])),
    }


@st.composite
def response_data(draw):
    """Generate valid response data."""
    return {
        "content": draw(st.text(min_size=1, max_size=10000)),
        "confidence": draw(st.floats(min_value=0.0, max_value=1.0)),
        "total_cost": draw(st.floats(min_value=0.0, max_value=100.0)),
        "execution_time": draw(st.floats(min_value=0.1, max_value=300.0)),
        "models_used": {"models": ["test-model"]},
        "orchestration_metadata": {"test": "data"},
    }


@st.composite
def subtask_data(draw):
    """Generate valid subtask data."""
    return {
        "content": draw(st.text(min_size=1, max_size=1000)),
        "task_type": draw(st.sampled_from(["reasoning", "research", "code_generation"])),
        "priority": draw(st.sampled_from(["high", "medium", "low"])),
        "status": draw(st.sampled_from(["pending", "processing", "completed", "failed"])),
    }


@pytest.mark.asyncio
@given(
    user=user_data(),
    req=request_data(),
    resp=response_data(),
)
async def test_cascade_delete_user_deletes_requests_and_responses(
    async_session: AsyncSession,
    user: dict,
    req: dict,
    resp: dict,
):
    """
    Property: Deleting a user cascades to delete all their requests and responses.
    
    This test verifies that the CASCADE delete constraint works correctly:
    - When a user is deleted, all their requests should be automatically deleted
    - When requests are deleted, their responses should also be deleted
    
    **Validates: Requirements 13.4, 13.5**
    """
    # Create user
    db_user = User(**user)
    async_session.add(db_user)
    await async_session.flush()
    
    # Create request for user
    db_request = Request(user_id=db_user.id, **req)
    async_session.add(db_request)
    await async_session.flush()
    
    # Create response for request
    db_response = Response(request_id=db_request.id, **resp)
    async_session.add(db_response)
    await async_session.commit()
    
    # Store IDs for verification
    user_id = db_user.id
    request_id = db_request.id
    response_id = db_response.id
    
    # Verify all records exist
    result = await async_session.execute(select(User).where(User.id == user_id))
    assert result.scalar_one_or_none() is not None
    
    result = await async_session.execute(select(Request).where(Request.id == request_id))
    assert result.scalar_one_or_none() is not None
    
    result = await async_session.execute(select(Response).where(Response.id == response_id))
    assert result.scalar_one_or_none() is not None
    
    # Delete user
    await async_session.delete(db_user)
    await async_session.commit()
    
    # Verify user is deleted
    result = await async_session.execute(select(User).where(User.id == user_id))
    assert result.scalar_one_or_none() is None
    
    # Verify request is cascade deleted
    result = await async_session.execute(select(Request).where(Request.id == request_id))
    assert result.scalar_one_or_none() is None, "Request should be cascade deleted when user is deleted"
    
    # Verify response is cascade deleted
    result = await async_session.execute(select(Response).where(Response.id == response_id))
    assert result.scalar_one_or_none() is None, "Response should be cascade deleted when request is deleted"


@pytest.mark.asyncio
@given(
    user=user_data(),
    req=request_data(),
    subtask1=subtask_data(),
    subtask2=subtask_data(),
)
async def test_cascade_delete_request_deletes_subtasks(
    async_session: AsyncSession,
    user: dict,
    req: dict,
    subtask1: dict,
    subtask2: dict,
):
    """
    Property: Deleting a request cascades to delete all its subtasks.
    
    This test verifies that the CASCADE delete constraint works correctly:
    - When a request is deleted, all its subtasks should be automatically deleted
    
    **Validates: Requirements 13.4, 13.5**
    """
    # Create user
    db_user = User(**user)
    async_session.add(db_user)
    await async_session.flush()
    
    # Create request for user
    db_request = Request(user_id=db_user.id, **req)
    async_session.add(db_request)
    await async_session.flush()
    
    # Create multiple subtasks for request
    db_subtask1 = Subtask(request_id=db_request.id, **subtask1)
    db_subtask2 = Subtask(request_id=db_request.id, **subtask2)
    async_session.add(db_subtask1)
    async_session.add(db_subtask2)
    await async_session.commit()
    
    # Store IDs for verification
    request_id = db_request.id
    subtask1_id = db_subtask1.id
    subtask2_id = db_subtask2.id
    
    # Verify all records exist
    result = await async_session.execute(select(Request).where(Request.id == request_id))
    assert result.scalar_one_or_none() is not None
    
    result = await async_session.execute(select(Subtask).where(Subtask.id == subtask1_id))
    assert result.scalar_one_or_none() is not None
    
    result = await async_session.execute(select(Subtask).where(Subtask.id == subtask2_id))
    assert result.scalar_one_or_none() is not None
    
    # Delete request
    await async_session.delete(db_request)
    await async_session.commit()
    
    # Verify request is deleted
    result = await async_session.execute(select(Request).where(Request.id == request_id))
    assert result.scalar_one_or_none() is None
    
    # Verify all subtasks are cascade deleted
    result = await async_session.execute(select(Subtask).where(Subtask.id == subtask1_id))
    assert result.scalar_one_or_none() is None, "Subtask 1 should be cascade deleted when request is deleted"
    
    result = await async_session.execute(select(Subtask).where(Subtask.id == subtask2_id))
    assert result.scalar_one_or_none() is None, "Subtask 2 should be cascade deleted when request is deleted"


@pytest.mark.asyncio
async def test_cascade_delete_integration(async_session: AsyncSession):
    """
    Integration test: Verify complete cascade delete chain.
    
    User -> Request -> Response + Subtasks
    
    When user is deleted, everything should be cascade deleted.
    
    **Validates: Requirements 13.4, 13.5**
    """
    # Create user
    user = User(
        email="test@example.com",
        password_hash="a" * 60,
        name="Test User",
        role="user",
        is_active=True,
    )
    async_session.add(user)
    await async_session.flush()
    
    # Create request
    request = Request(
        user_id=user.id,
        content="Test query",
        execution_mode="balanced",
        status="completed",
    )
    async_session.add(request)
    await async_session.flush()
    
    # Create response
    response = Response(
        request_id=request.id,
        content="Test response",
        confidence=0.95,
        total_cost=0.05,
        execution_time=5.0,
        models_used={"models": ["test-model"]},
        orchestration_metadata={"test": "data"},
    )
    async_session.add(response)
    
    # Create subtasks
    subtask1 = Subtask(
        request_id=request.id,
        content="Subtask 1",
        task_type="reasoning",
        priority="high",
        status="completed",
    )
    subtask2 = Subtask(
        request_id=request.id,
        content="Subtask 2",
        task_type="research",
        priority="medium",
        status="completed",
    )
    async_session.add(subtask1)
    async_session.add(subtask2)
    await async_session.commit()
    
    # Store IDs
    user_id = user.id
    request_id = request.id
    response_id = response.id
    subtask1_id = subtask1.id
    subtask2_id = subtask2.id
    
    # Verify all exist
    result = await async_session.execute(select(User).where(User.id == user_id))
    assert result.scalar_one_or_none() is not None
    
    result = await async_session.execute(select(Request).where(Request.id == request_id))
    assert result.scalar_one_or_none() is not None
    
    result = await async_session.execute(select(Response).where(Response.id == response_id))
    assert result.scalar_one_or_none() is not None
    
    result = await async_session.execute(select(Subtask).where(Subtask.id == subtask1_id))
    assert result.scalar_one_or_none() is not None
    
    result = await async_session.execute(select(Subtask).where(Subtask.id == subtask2_id))
    assert result.scalar_one_or_none() is not None
    
    # Delete user - should cascade delete everything
    await async_session.delete(user)
    await async_session.commit()
    
    # Verify everything is deleted
    result = await async_session.execute(select(User).where(User.id == user_id))
    assert result.scalar_one_or_none() is None
    
    result = await async_session.execute(select(Request).where(Request.id == request_id))
    assert result.scalar_one_or_none() is None
    
    result = await async_session.execute(select(Response).where(Response.id == response_id))
    assert result.scalar_one_or_none() is None
    
    result = await async_session.execute(select(Subtask).where(Subtask.id == subtask1_id))
    assert result.scalar_one_or_none() is None
    
    result = await async_session.execute(select(Subtask).where(Subtask.id == subtask2_id))
    assert result.scalar_one_or_none() is None
