"""Provider cost tracking service."""

import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.provider_cost import ProviderCostBreakdown
from app.models.request import Request
from app.models.response import Response
from app.services.cloud_ai.model_registry import MODEL_REGISTRY

logger = logging.getLogger(__name__)


class ProviderCostTracker:
    """Tracks and analyzes costs per provider."""
    
    async def track_request_costs(
        self,
        db: AsyncSession,
        request_id: UUID,
        subtask_costs: List[Dict[str, Any]]
    ) -> None:
        """Track costs per provider for a request.
        
        Args:
            db: Database session
            request_id: Request ID
            subtask_costs: List of subtask cost dictionaries with keys:
                - model_id: str
                - input_tokens: int
                - output_tokens: int
                - cost: float
        """
        try:
            # Group costs by provider
            provider_data = defaultdict(lambda: {
                "subtask_count": 0,
                "total_cost": 0.0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "models": set()
            })
            
            for subtask in subtask_costs:
                model_id = subtask["model_id"]
                
                # Get provider from model registry
                if model_id not in MODEL_REGISTRY:
                    logger.warning(f"Model {model_id} not found in registry, skipping cost tracking")
                    continue
                
                provider_name = MODEL_REGISTRY[model_id]["provider"]
                
                # Aggregate data
                provider_data[provider_name]["subtask_count"] += 1
                provider_data[provider_name]["total_cost"] += subtask.get("cost", 0.0)
                provider_data[provider_name]["total_input_tokens"] += subtask.get("input_tokens", 0)
                provider_data[provider_name]["total_output_tokens"] += subtask.get("output_tokens", 0)
                provider_data[provider_name]["models"].add(model_id)
            
            # Create provider cost breakdown records
            for provider_name, data in provider_data.items():
                # Use the most frequently used model for this provider
                model_id = list(data["models"])[0] if data["models"] else "unknown"
                
                cost_breakdown = ProviderCostBreakdown(
                    request_id=request_id,
                    provider_name=provider_name,
                    model_id=model_id,
                    subtask_count=data["subtask_count"],
                    total_cost=data["total_cost"],
                    total_input_tokens=data["total_input_tokens"],
                    total_output_tokens=data["total_output_tokens"]
                )
                
                db.add(cost_breakdown)
            
            await db.commit()
            
            logger.info(
                f"Tracked costs for request {request_id}: "
                f"{len(provider_data)} providers, "
                f"total cost: ${sum(d['total_cost'] for d in provider_data.values()):.4f}"
            )
            
        except Exception as e:
            logger.error(f"Error tracking provider costs: {e}", exc_info=True)
            await db.rollback()
    
    async def get_provider_costs_for_request(
        self,
        db: AsyncSession,
        request_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get provider cost breakdown for a specific request.
        
        Args:
            db: Database session
            request_id: Request ID
            
        Returns:
            List of provider cost dictionaries
        """
        result = await db.execute(
            select(ProviderCostBreakdown).where(
                ProviderCostBreakdown.request_id == request_id
            )
        )
        costs = result.scalars().all()
        
        return [
            {
                "provider_name": cost.provider_name,
                "model_id": cost.model_id,
                "subtask_count": cost.subtask_count,
                "total_cost": cost.total_cost,
                "total_input_tokens": cost.total_input_tokens,
                "total_output_tokens": cost.total_output_tokens
            }
            for cost in costs
        ]
    
    async def get_provider_costs_for_user(
        self,
        db: AsyncSession,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get aggregated provider costs for a user.
        
        Args:
            db: Database session
            user_id: User ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary with provider cost breakdown
        """
        # Build query
        query = (
            select(
                ProviderCostBreakdown.provider_name,
                func.count(ProviderCostBreakdown.id).label("request_count"),
                func.sum(ProviderCostBreakdown.subtask_count).label("total_subtasks"),
                func.sum(ProviderCostBreakdown.total_cost).label("total_cost"),
                func.sum(ProviderCostBreakdown.total_input_tokens).label("total_input_tokens"),
                func.sum(ProviderCostBreakdown.total_output_tokens).label("total_output_tokens")
            )
            .join(Request, ProviderCostBreakdown.request_id == Request.id)
            .where(Request.user_id == user_id)
            .group_by(ProviderCostBreakdown.provider_name)
        )
        
        # Apply date filters
        if start_date:
            query = query.where(ProviderCostBreakdown.created_at >= start_date)
        if end_date:
            query = query.where(ProviderCostBreakdown.created_at <= end_date)
        
        result = await db.execute(query)
        rows = result.all()
        
        # Format results
        by_provider = []
        total_cost = 0.0
        total_requests = 0
        
        for row in rows:
            provider_cost = {
                "provider_name": row.provider_name,
                "request_count": row.request_count,
                "total_subtasks": row.total_subtasks or 0,
                "total_cost": float(row.total_cost or 0.0),
                "total_input_tokens": row.total_input_tokens or 0,
                "total_output_tokens": row.total_output_tokens or 0
            }
            by_provider.append(provider_cost)
            total_cost += provider_cost["total_cost"]
            total_requests += provider_cost["request_count"]
        
        # Sort by cost descending
        by_provider.sort(key=lambda x: x["total_cost"], reverse=True)
        
        # Calculate cost savings from free providers
        free_providers = ["ollama", "huggingface", "gemini"]
        free_provider_subtasks = sum(
            p["total_subtasks"] for p in by_provider 
            if p["provider_name"] in free_providers
        )
        
        # Estimate savings (assume average paid provider cost of $0.002 per 1000 tokens)
        total_tokens = sum(
            p["total_input_tokens"] + p["total_output_tokens"] 
            for p in by_provider 
            if p["provider_name"] in free_providers
        )
        estimated_savings = (total_tokens / 1000) * 0.002
        
        return {
            "by_provider": by_provider,
            "total_cost": round(total_cost, 4),
            "total_requests": total_requests,
            "estimated_savings": round(estimated_savings, 4),
            "free_provider_usage_percent": round(
                (free_provider_subtasks / sum(p["total_subtasks"] for p in by_provider) * 100)
                if by_provider else 0.0,
                2
            )
        }
    
    async def get_provider_costs_system_wide(
        self,
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get aggregated provider costs across all users (admin view).
        
        Args:
            db: Database session
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary with system-wide provider cost breakdown
        """
        # Build query
        query = (
            select(
                ProviderCostBreakdown.provider_name,
                func.count(ProviderCostBreakdown.id).label("request_count"),
                func.sum(ProviderCostBreakdown.subtask_count).label("total_subtasks"),
                func.sum(ProviderCostBreakdown.total_cost).label("total_cost"),
                func.sum(ProviderCostBreakdown.total_input_tokens).label("total_input_tokens"),
                func.sum(ProviderCostBreakdown.total_output_tokens).label("total_output_tokens")
            )
            .group_by(ProviderCostBreakdown.provider_name)
        )
        
        # Apply date filters
        if start_date:
            query = query.where(ProviderCostBreakdown.created_at >= start_date)
        if end_date:
            query = query.where(ProviderCostBreakdown.created_at <= end_date)
        
        result = await db.execute(query)
        rows = result.all()
        
        # Format results
        by_provider = []
        total_cost = 0.0
        total_requests = 0
        
        for row in rows:
            provider_cost = {
                "provider_name": row.provider_name,
                "request_count": row.request_count,
                "total_subtasks": row.total_subtasks or 0,
                "total_cost": float(row.total_cost or 0.0),
                "total_input_tokens": row.total_input_tokens or 0,
                "total_output_tokens": row.total_output_tokens or 0
            }
            by_provider.append(provider_cost)
            total_cost += provider_cost["total_cost"]
            total_requests += provider_cost["request_count"]
        
        # Sort by cost descending
        by_provider.sort(key=lambda x: x["total_cost"], reverse=True)
        
        # Calculate cost savings from free providers
        free_providers = ["ollama", "huggingface", "gemini"]
        free_provider_subtasks = sum(
            p["total_subtasks"] for p in by_provider 
            if p["provider_name"] in free_providers
        )
        
        # Estimate savings
        total_tokens = sum(
            p["total_input_tokens"] + p["total_output_tokens"] 
            for p in by_provider 
            if p["provider_name"] in free_providers
        )
        estimated_savings = (total_tokens / 1000) * 0.002
        
        return {
            "by_provider": by_provider,
            "total_cost": round(total_cost, 4),
            "total_requests": total_requests,
            "estimated_savings": round(estimated_savings, 4),
            "free_provider_usage_percent": round(
                (free_provider_subtasks / sum(p["total_subtasks"] for p in by_provider) * 100)
                if by_provider else 0.0,
                2
            )
        }
    
    async def get_monthly_cost_report(
        self,
        db: AsyncSession,
        user_id: Optional[UUID] = None,
        year: int = None,
        month: int = None
    ) -> Dict[str, Any]:
        """Generate monthly cost report by provider.
        
        Args:
            db: Database session
            user_id: Optional user ID (None for system-wide)
            year: Year (defaults to current year)
            month: Month (defaults to current month)
            
        Returns:
            Monthly cost report dictionary
        """
        if year is None or month is None:
            now = datetime.utcnow()
            year = year or now.year
            month = month or now.month
        
        # Calculate date range for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Get costs for the month
        if user_id:
            costs = await self.get_provider_costs_for_user(db, user_id, start_date, end_date)
        else:
            costs = await self.get_provider_costs_system_wide(db, start_date, end_date)
        
        return {
            "year": year,
            "month": month,
            "month_name": start_date.strftime("%B"),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            **costs
        }
    
    async def check_cost_threshold(
        self,
        db: AsyncSession,
        user_id: UUID,
        threshold: float = 10.0,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Check if user's costs exceed threshold in the given period.
        
        Args:
            db: Database session
            user_id: User ID
            threshold: Cost threshold in USD
            period_days: Number of days to check
            
        Returns:
            Dictionary with threshold check results
        """
        start_date = datetime.utcnow() - timedelta(days=period_days)
        
        costs = await self.get_provider_costs_for_user(db, user_id, start_date)
        
        total_cost = costs["total_cost"]
        exceeds_threshold = total_cost >= threshold
        
        return {
            "user_id": str(user_id),
            "period_days": period_days,
            "threshold": threshold,
            "total_cost": total_cost,
            "exceeds_threshold": exceeds_threshold,
            "percentage_of_threshold": round((total_cost / threshold * 100), 2) if threshold > 0 else 0,
            "by_provider": costs["by_provider"]
        }


# Singleton instance
_provider_cost_tracker = None


def get_provider_cost_tracker() -> ProviderCostTracker:
    """Get singleton instance of ProviderCostTracker."""
    global _provider_cost_tracker
    if _provider_cost_tracker is None:
        _provider_cost_tracker = ProviderCostTracker()
    return _provider_cost_tracker
