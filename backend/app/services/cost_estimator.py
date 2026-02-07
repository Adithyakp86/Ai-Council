"""Cost estimation service for AI Council requests."""

import hashlib
import json
from typing import Dict, Optional
from redis.asyncio import Redis

from app.services.cloud_ai.model_registry import MODEL_REGISTRY
from app.services.execution_mode_config import EXECUTION_MODE_CONFIGS


class CostEstimator:
    """Estimates costs for AI Council requests based on execution mode and request length."""
    
    # Historical data for estimation (tokens per character ratios)
    # These are approximate ratios based on typical tokenization
    TOKENS_PER_CHAR_INPUT = 0.25  # ~4 chars per token
    TOKENS_PER_CHAR_OUTPUT = 0.25  # Similar for output
    
    # Subtask multipliers by execution mode
    # These represent how many subtasks are typically created
    SUBTASK_MULTIPLIERS = {
        "fast": 1.5,  # Minimal decomposition
        "balanced": 3.0,  # Moderate decomposition
        "best_quality": 5.0  # Maximum decomposition
    }
    
    # Output length multipliers (output is typically longer than input)
    OUTPUT_MULTIPLIERS = {
        "fast": 1.5,  # Shorter responses
        "balanced": 2.0,  # Standard responses
        "best_quality": 3.0  # Comprehensive responses
    }
    
    def __init__(self, redis_client: Optional[Redis] = None):
        """Initialize cost estimator.
        
        Args:
            redis_client: Optional Redis client for caching
        """
        self.redis_client = redis_client
        self.cache_ttl = 3600  # 1 hour in seconds
    
    def _estimate_token_count(self, text_length: int) -> int:
        """Estimate token count from text length.
        
        Args:
            text_length: Length of text in characters
            
        Returns:
            Estimated token count
        """
        return int(text_length * self.TOKENS_PER_CHAR_INPUT)
    
    def _get_average_model_cost(self, execution_mode: str) -> float:
        """Get average cost per token for models used in execution mode.
        
        Args:
            execution_mode: Execution mode (fast, balanced, best_quality)
            
        Returns:
            Average cost per token (input + output averaged)
        """
        config = EXECUTION_MODE_CONFIGS.get(execution_mode)
        if not config:
            raise ValueError(f"Unknown execution mode: {execution_mode}")
        
        # Get preferred models for this mode
        preferred_models = config.preferred_model_types
        
        # Calculate average cost across preferred models
        total_cost = 0.0
        count = 0
        
        for model_id in preferred_models:
            if model_id in MODEL_REGISTRY:
                model_config = MODEL_REGISTRY[model_id]
                # Average of input and output cost
                avg_cost = (
                    model_config["cost_per_input_token"] +
                    model_config["cost_per_output_token"]
                ) / 2
                total_cost += avg_cost
                count += 1
        
        if count == 0:
            # Fallback to a reasonable default
            return 0.000001  # $0.000001 per token
        
        return total_cost / count
    
    def estimate_cost_for_mode(
        self,
        request_length: int,
        execution_mode: str
    ) -> float:
        """Estimate cost for a request in a specific execution mode.
        
        Args:
            request_length: Length of request in characters
            execution_mode: Execution mode (fast, balanced, best_quality)
            
        Returns:
            Estimated cost in USD
        """
        # Estimate input tokens
        input_tokens = self._estimate_token_count(request_length)
        
        # Estimate output tokens based on mode
        output_multiplier = self.OUTPUT_MULTIPLIERS.get(execution_mode, 2.0)
        output_tokens = int(input_tokens * output_multiplier)
        
        # Get subtask multiplier
        subtask_multiplier = self.SUBTASK_MULTIPLIERS.get(execution_mode, 3.0)
        
        # Total tokens across all subtasks
        total_input_tokens = int(input_tokens * subtask_multiplier)
        total_output_tokens = int(output_tokens * subtask_multiplier)
        
        # Get average model cost for this mode
        avg_cost_per_token = self._get_average_model_cost(execution_mode)
        
        # Calculate total cost
        estimated_cost = (total_input_tokens + total_output_tokens) * avg_cost_per_token
        
        return round(estimated_cost, 6)  # Round to 6 decimal places
    
    def estimate_all_modes(self, request_length: int) -> Dict[str, float]:
        """Estimate costs for all execution modes.
        
        Args:
            request_length: Length of request in characters
            
        Returns:
            Dictionary with mode names as keys and estimated costs as values
        """
        return {
            "fast": self.estimate_cost_for_mode(request_length, "fast"),
            "balanced": self.estimate_cost_for_mode(request_length, "balanced"),
            "best_quality": self.estimate_cost_for_mode(request_length, "best_quality")
        }
    
    def _get_cache_key(self, request_length: int) -> str:
        """Generate cache key for cost estimates.
        
        Args:
            request_length: Length of request in characters
            
        Returns:
            Cache key string
        """
        # Use length as the key (simple but effective)
        # Round to nearest 10 to increase cache hit rate
        rounded_length = (request_length // 10) * 10
        return f"cost:estimate:length:{rounded_length}"
    
    async def estimate_all_modes_cached(
        self,
        request_length: int
    ) -> Dict[str, float]:
        """Estimate costs for all modes with Redis caching.
        
        Args:
            request_length: Length of request in characters
            
        Returns:
            Dictionary with mode names as keys and estimated costs as values
        """
        if not self.redis_client:
            # No caching available, calculate directly
            return self.estimate_all_modes(request_length)
        
        cache_key = self._get_cache_key(request_length)
        
        try:
            # Try to get from cache
            cached_value = await self.redis_client.get(cache_key)
            if cached_value:
                return json.loads(cached_value)
        except Exception as e:
            # Cache read failed, continue without cache
            print(f"Cache read failed: {e}")
        
        # Calculate estimates
        estimates = self.estimate_all_modes(request_length)
        
        try:
            # Store in cache
            await self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(estimates)
            )
        except Exception as e:
            # Cache write failed, continue without cache
            print(f"Cache write failed: {e}")
        
        return estimates
    
    def estimate_with_time(
        self,
        request_length: int,
        execution_mode: str
    ) -> Dict[str, any]:
        """Estimate cost and time for a request.
        
        Args:
            request_length: Length of request in characters
            execution_mode: Execution mode (fast, balanced, best_quality)
            
        Returns:
            Dictionary with estimated_cost and estimated_time_seconds
        """
        cost = self.estimate_cost_for_mode(request_length, execution_mode)
        
        # Estimate time based on mode configuration
        config = EXECUTION_MODE_CONFIGS.get(execution_mode)
        if not config:
            raise ValueError(f"Unknown execution mode: {execution_mode}")
        
        # Base time estimation (rough approximation)
        # Longer requests take more time
        base_time = min(request_length / 100, 30)  # Cap at 30 seconds base
        
        # Adjust by mode
        time_multipliers = {
            "fast": 1.0,  # Fastest
            "balanced": 2.0,  # Moderate
            "best_quality": 4.0  # Slowest (more decomposition, arbitration)
        }
        
        multiplier = time_multipliers.get(execution_mode, 2.0)
        estimated_time = base_time * multiplier
        
        return {
            "estimated_cost": cost,
            "estimated_time_seconds": round(estimated_time, 1)
        }
    
    def estimate_all_modes_with_time(
        self,
        request_length: int
    ) -> Dict[str, Dict[str, any]]:
        """Estimate costs and times for all execution modes.
        
        Args:
            request_length: Length of request in characters
            
        Returns:
            Dictionary with mode names as keys and estimate dicts as values
        """
        return {
            "fast": self.estimate_with_time(request_length, "fast"),
            "balanced": self.estimate_with_time(request_length, "balanced"),
            "best_quality": self.estimate_with_time(request_length, "best_quality")
        }
