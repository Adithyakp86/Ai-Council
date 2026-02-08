"""User endpoints."""
import logging
from collections import defaultdict
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.middleware import get_current_user
from app.models.user import User
from app.models.request import Request
from app.models.response import Response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user", tags=["user"])


class UserStatsResponse(BaseModel):
    """Schema for user statistics response."""
    total_requests: int
    total_cost: float
    average_confidence: float
    requests_by_mode: dict[str, int]
    requests_over_time: list[dict]
    top_models: list[dict]
    average_response_time: float
    provider_cost_breakdown: dict[str, Any]


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's usage statistics.
    
    This endpoint calculates:
    1. Total requests from Request_History
    2. Total cost from Response records
    3. Average confidence score
    4. Group requests by execution_mode
    5. Generate time series data for requests over time
    6. Identify most frequently used models
    7. Calculate average response time
    
    Statistics are cached in Redis for 5 minutes to improve performance.
    Cache is invalidated when new requests complete.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        UserStatsResponse with comprehensive usage statistics
    """
    try:
        from sqlalchemy import select
        from app.core.redis import redis_client
        import json
        
        logger.info(f"Calculating statistics for user {current_user.id}")
        
        # Check cache first
        cache_key = redis_client.get_user_stats_key(str(current_user.id))
        try:
            cached_stats = await redis_client.client.get(cache_key)
            if cached_stats:
                logger.info(f"Returning cached statistics for user {current_user.id}")
                stats_dict = json.loads(cached_stats)
                return UserStatsResponse(**stats_dict)
        except Exception as cache_error:
            logger.warning(f"Cache read error: {cache_error}, proceeding with calculation")
        
        # Get all user's requests
        result = await db.execute(
            select(Request).where(Request.user_id == current_user.id)
        )
        requests = result.scalars().all()
        
        # Calculate total requests
        total_requests = len(requests)
        
        if total_requests == 0:
            # Return empty stats for users with no requests
            empty_stats = UserStatsResponse(
                total_requests=0,
                total_cost=0.0,
                average_confidence=0.0,
                requests_by_mode={},
                requests_over_time=[],
                top_models=[],
                average_response_time=0.0,
                provider_cost_breakdown={
                    "by_provider": [],
                    "total_cost": 0.0,
                    "total_requests": 0,
                    "estimated_savings": 0.0,
                    "free_provider_usage_percent": 0.0
                }
            )
            
            # Cache empty stats for 5 minutes
            try:
                await redis_client.client.setex(
                    cache_key,
                    300,  # 5 minutes
                    json.dumps(empty_stats.model_dump())
                )
            except Exception as cache_error:
                logger.warning(f"Cache write error: {cache_error}")
            
            return empty_stats
        
        # Get all responses for user's requests
        request_ids = [req.id for req in requests]
        result = await db.execute(
            select(Response).where(Response.request_id.in_(request_ids))
        )
        responses = result.scalars().all()
        
        # Calculate total cost
        total_cost = sum(resp.total_cost for resp in responses)
        
        # Calculate average confidence
        if responses:
            average_confidence = sum(resp.confidence for resp in responses) / len(responses)
        else:
            average_confidence = 0.0
        
        # Group requests by execution_mode
        requests_by_mode = defaultdict(int)
        for req in requests:
            requests_by_mode[req.execution_mode] += 1
        
        # Generate time series data for requests over time
        # Group by day for the last 30 days
        requests_over_time = []
        if requests:
            # Create daily buckets
            date_counts = defaultdict(int)
            for req in requests:
                date_key = req.created_at.date().isoformat()
                date_counts[date_key] += 1
            
            # Convert to list of dicts sorted by date
            requests_over_time = [
                {"date": date, "count": count}
                for date, count in sorted(date_counts.items())
            ]
        
        # Identify most frequently used models
        model_counts = defaultdict(int)
        model_costs = defaultdict(float)
        
        for resp in responses:
            models = resp.models_used.get("models", [])
            for model in models:
                if isinstance(model, str):
                    model_counts[model] += 1
                    # Distribute cost evenly across models (simplified)
                    model_costs[model] += resp.total_cost / len(models) if models else 0
                elif isinstance(model, dict):
                    model_id = model.get("model_id", "unknown")
                    model_counts[model_id] += 1
                    model_costs[model_id] += resp.total_cost / len(models) if models else 0
        
        # Sort by usage count and get top models
        top_models = [
            {
                "model_id": model_id,
                "usage_count": count,
                "total_cost": round(model_costs[model_id], 4)
            }
            for model_id, count in sorted(
                model_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]  # Top 10 models
        ]
        
        # Calculate average response time
        if responses:
            average_response_time = sum(resp.execution_time for resp in responses) / len(responses)
        else:
            average_response_time = 0.0
        
        # Get provider cost breakdown
        from app.services.provider_cost_tracker import get_provider_cost_tracker
        provider_cost_tracker = get_provider_cost_tracker()
        provider_cost_breakdown = await provider_cost_tracker.get_provider_costs_for_user(
            db, current_user.id
        )
        
        logger.info(
            f"Statistics calculated for user {current_user.id}: "
            f"total_requests={total_requests}, "
            f"total_cost={total_cost:.4f}, "
            f"avg_confidence={average_confidence:.2f}"
        )
        
        stats = UserStatsResponse(
            total_requests=total_requests,
            total_cost=round(total_cost, 4),
            average_confidence=round(average_confidence, 4),
            requests_by_mode=dict(requests_by_mode),
            requests_over_time=requests_over_time,
            top_models=top_models,
            average_response_time=round(average_response_time, 2),
            provider_cost_breakdown=provider_cost_breakdown
        )
        
        # Cache statistics for 5 minutes
        try:
            await redis_client.client.setex(
                cache_key,
                300,  # 5 minutes
                json.dumps(stats.model_dump())
            )
            logger.info(f"Cached statistics for user {current_user.id}")
        except Exception as cache_error:
            logger.warning(f"Cache write error: {cache_error}")
        
        return stats
        
    except Exception as e:
        logger.error(f"Error calculating user statistics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate user statistics"
        )
