"""Cost calculation service for AI Council requests."""

from typing import Dict, List, Any, Optional
from app.services.cloud_ai.model_registry import MODEL_REGISTRY


class CostCalculator:
    """Calculates costs for AI Council requests based on token usage."""
    
    def calculate_subtask_cost(
        self,
        model_id: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate cost for a single subtask.
        
        Args:
            model_id: The model identifier
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Total cost in USD
            
        Raises:
            KeyError: If model_id is not found in registry
        """
        if model_id not in MODEL_REGISTRY:
            raise KeyError(f"Model {model_id} not found in registry")
        
        model_config = MODEL_REGISTRY[model_id]
        
        input_cost = input_tokens * model_config["cost_per_input_token"]
        output_cost = output_tokens * model_config["cost_per_output_token"]
        
        return input_cost + output_cost
    
    def calculate_total_cost(
        self,
        subtask_costs: List[Dict[str, Any]]
    ) -> float:
        """Calculate total cost across all subtasks.
        
        Args:
            subtask_costs: List of subtask cost dictionaries with keys:
                - model_id: str
                - input_tokens: int
                - output_tokens: int
                - cost: float (optional, will be calculated if not provided)
                
        Returns:
            Total cost in USD
        """
        total = 0.0
        
        for subtask in subtask_costs:
            if "cost" in subtask and subtask["cost"] is not None:
                # Use pre-calculated cost if available
                total += subtask["cost"]
            else:
                # Calculate cost from token usage
                cost = self.calculate_subtask_cost(
                    model_id=subtask["model_id"],
                    input_tokens=subtask["input_tokens"],
                    output_tokens=subtask["output_tokens"]
                )
                total += cost
        
        return total
    
    def create_cost_breakdown(
        self,
        subtask_costs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create detailed cost breakdown for orchestration metadata.
        
        Args:
            subtask_costs: List of subtask cost dictionaries with keys:
                - subtask_id: str
                - model_id: str
                - input_tokens: int
                - output_tokens: int
                - cost: float (optional)
                
        Returns:
            Dictionary with cost breakdown:
                - total_cost: float
                - by_subtask: List[Dict] with per-subtask costs
                - by_model: Dict[str, float] with costs grouped by model
                - total_input_tokens: int
                - total_output_tokens: int
        """
        by_subtask = []
        by_model: Dict[str, float] = {}
        total_input_tokens = 0
        total_output_tokens = 0
        
        for subtask in subtask_costs:
            # Calculate cost if not provided
            if "cost" not in subtask or subtask["cost"] is None:
                cost = self.calculate_subtask_cost(
                    model_id=subtask["model_id"],
                    input_tokens=subtask["input_tokens"],
                    output_tokens=subtask["output_tokens"]
                )
            else:
                cost = subtask["cost"]
            
            # Add to by_subtask breakdown
            by_subtask.append({
                "subtask_id": subtask.get("subtask_id", "unknown"),
                "model_id": subtask["model_id"],
                "input_tokens": subtask["input_tokens"],
                "output_tokens": subtask["output_tokens"],
                "cost": cost
            })
            
            # Aggregate by model
            model_id = subtask["model_id"]
            if model_id not in by_model:
                by_model[model_id] = 0.0
            by_model[model_id] += cost
            
            # Aggregate token counts
            total_input_tokens += subtask["input_tokens"]
            total_output_tokens += subtask["output_tokens"]
        
        total_cost = sum(item["cost"] for item in by_subtask)
        
        return {
            "total_cost": total_cost,
            "by_subtask": by_subtask,
            "by_model": by_model,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens
        }
    
    def get_model_cost_per_token(self, model_id: str) -> Dict[str, float]:
        """Get cost per token for a specific model.
        
        Args:
            model_id: The model identifier
            
        Returns:
            Dictionary with cost_per_input_token and cost_per_output_token
            
        Raises:
            KeyError: If model_id is not found in registry
        """
        if model_id not in MODEL_REGISTRY:
            raise KeyError(f"Model {model_id} not found in registry")
        
        model_config = MODEL_REGISTRY[model_id]
        
        return {
            "cost_per_input_token": model_config["cost_per_input_token"],
            "cost_per_output_token": model_config["cost_per_output_token"]
        }
