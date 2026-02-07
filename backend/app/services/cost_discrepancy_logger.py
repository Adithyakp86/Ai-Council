"""Cost discrepancy logging service."""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)


class CostDiscrepancyLogger:
    """Logs significant discrepancies between estimated and actual costs."""
    
    # Threshold for logging (50% discrepancy)
    DISCREPANCY_THRESHOLD = 0.5
    
    def __init__(self):
        """Initialize cost discrepancy logger."""
        pass
    
    def calculate_discrepancy_ratio(
        self,
        estimated_cost: float,
        actual_cost: float
    ) -> float:
        """Calculate the discrepancy ratio between estimated and actual cost.
        
        Args:
            estimated_cost: The estimated cost
            actual_cost: The actual cost
            
        Returns:
            Absolute discrepancy ratio: |actual - estimate| / estimate
            Returns 0.0 if estimated_cost is 0
        """
        if estimated_cost == 0:
            # If estimate was 0, any actual cost is infinite discrepancy
            # Return a large value if actual > 0, otherwise 0
            return float('inf') if actual_cost > 0 else 0.0
        
        return abs(actual_cost - estimated_cost) / estimated_cost
    
    def should_log_discrepancy(
        self,
        estimated_cost: float,
        actual_cost: float
    ) -> bool:
        """Check if discrepancy exceeds threshold and should be logged.
        
        Args:
            estimated_cost: The estimated cost
            actual_cost: The actual cost
            
        Returns:
            True if discrepancy exceeds threshold, False otherwise
        """
        discrepancy_ratio = self.calculate_discrepancy_ratio(
            estimated_cost,
            actual_cost
        )
        
        return discrepancy_ratio > self.DISCREPANCY_THRESHOLD
    
    def log_discrepancy(
        self,
        request_id: str,
        execution_mode: str,
        estimated_cost: float,
        actual_cost: float,
        request_length: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a cost discrepancy.
        
        Args:
            request_id: The request identifier
            execution_mode: The execution mode used
            estimated_cost: The estimated cost
            actual_cost: The actual cost
            request_length: Length of the request in characters
            metadata: Optional additional metadata to log
        """
        discrepancy_ratio = self.calculate_discrepancy_ratio(
            estimated_cost,
            actual_cost
        )
        
        if not self.should_log_discrepancy(estimated_cost, actual_cost):
            # Discrepancy is below threshold, don't log
            return
        
        # Calculate percentage and difference
        discrepancy_percentage = discrepancy_ratio * 100
        cost_difference = actual_cost - estimated_cost
        
        # Determine if over or under estimate
        direction = "over" if actual_cost > estimated_cost else "under"
        
        # Build log message
        log_data = {
            "event": "cost_discrepancy",
            "request_id": request_id,
            "execution_mode": execution_mode,
            "estimated_cost": round(estimated_cost, 6),
            "actual_cost": round(actual_cost, 6),
            "cost_difference": round(cost_difference, 6),
            "discrepancy_ratio": round(discrepancy_ratio, 4),
            "discrepancy_percentage": round(discrepancy_percentage, 2),
            "direction": direction,
            "request_length": request_length,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add optional metadata
        if metadata:
            log_data["metadata"] = metadata
        
        # Log as warning since this indicates estimation needs improvement
        logger.warning(
            f"Significant cost discrepancy detected: "
            f"request_id={request_id}, "
            f"mode={execution_mode}, "
            f"estimated=${estimated_cost:.6f}, "
            f"actual=${actual_cost:.6f}, "
            f"discrepancy={discrepancy_percentage:.2f}% ({direction}estimate), "
            f"request_length={request_length}",
            extra=log_data
        )
    
    def check_and_log(
        self,
        request_id: str,
        execution_mode: str,
        estimated_cost: float,
        actual_cost: float,
        request_length: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Check for discrepancy and log if threshold exceeded.
        
        Args:
            request_id: The request identifier
            execution_mode: The execution mode used
            estimated_cost: The estimated cost
            actual_cost: The actual cost
            request_length: Length of the request in characters
            metadata: Optional additional metadata to log
            
        Returns:
            True if discrepancy was logged, False otherwise
        """
        if self.should_log_discrepancy(estimated_cost, actual_cost):
            self.log_discrepancy(
                request_id=request_id,
                execution_mode=execution_mode,
                estimated_cost=estimated_cost,
                actual_cost=actual_cost,
                request_length=request_length,
                metadata=metadata
            )
            return True
        
        return False
    
    def get_discrepancy_summary(
        self,
        estimated_cost: float,
        actual_cost: float
    ) -> Dict[str, Any]:
        """Get a summary of the cost discrepancy.
        
        Args:
            estimated_cost: The estimated cost
            actual_cost: The actual cost
            
        Returns:
            Dictionary with discrepancy summary
        """
        discrepancy_ratio = self.calculate_discrepancy_ratio(
            estimated_cost,
            actual_cost
        )
        
        cost_difference = actual_cost - estimated_cost
        direction = "over" if actual_cost > estimated_cost else "under"
        exceeds_threshold = discrepancy_ratio > self.DISCREPANCY_THRESHOLD
        
        return {
            "estimated_cost": round(estimated_cost, 6),
            "actual_cost": round(actual_cost, 6),
            "cost_difference": round(cost_difference, 6),
            "discrepancy_ratio": round(discrepancy_ratio, 4),
            "discrepancy_percentage": round(discrepancy_ratio * 100, 2),
            "direction": direction,
            "exceeds_threshold": exceeds_threshold,
            "threshold": self.DISCREPANCY_THRESHOLD
        }
