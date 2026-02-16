#!/usr/bin/env python3
"""
Main application entry point for AI Council.

This module provides the main application class that wires together all
components of the AI Council system and provides a simple interface
for processing user requests.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from .core.models import ExecutionMode, FinalResponse
from .core.interfaces import OrchestrationLayer
from .utils.config import AICouncilConfig, load_config
from .utils.logging import configure_logging, get_logger
from .factory import AICouncilFactory


class AICouncil:
    """
    Main AI Council application class.
    
    This class provides the primary interface for the AI Council system,
    handling configuration loading, component initialization, and request processing.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize AI Council with configuration.
        
        Args:
            config_path: Optional path to configuration file
        """
        # Load configuration
        self.config = load_config(config_path)
        
        # Configure logging
        configure_logging(
            level=self.config.logging.level,
            format_json=self.config.logging.format_json,
            include_timestamp=self.config.logging.include_timestamp,
            include_caller=self.config.logging.include_caller
        )
        
        self.logger = get_logger(__name__)
        self.logger.info("Initializing AI Council application")
        
        # Create factory for dependency injection
        self.factory = AICouncilFactory(self.config)
        
        # Validate configuration
        validation_issues = self.factory.validate_configuration()
        if validation_issues:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"- {issue}" for issue in validation_issues)
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # Initialize orchestration layer
        self.orchestration_layer: OrchestrationLayer = self.factory.create_orchestration_layer()
        
        self.logger.info("AI Council application initialized successfully")
    
    def process_request(
        self, 
        user_input: str, 
        execution_mode: ExecutionMode = ExecutionMode.BALANCED
    ) -> FinalResponse:
        """
        Process a user request through the AI Council system.
        
        Args:
            user_input: The user's request as a string
            execution_mode: The execution mode to use (fast, balanced, best_quality)
            
        Returns:
            FinalResponse: The final processed response
        """
        self.logger.info(f"Processing request in {execution_mode.value} mode")
        self.logger.debug(f"User input: {user_input[:200]}...")
        
        try:
            response = self.orchestration_layer.process_request(user_input, execution_mode)
            
            if response.success:
                self.logger.info("Request processed successfully")
            else:
                self.logger.warning(f"Request processing failed: {response.error_message}")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Unexpected error processing request: {str(e)}")
            return FinalResponse(
                content="",
                overall_confidence=0.0,
                success=False,
                error_message=f"System error: {str(e)}",
                models_used=[]
            )
    
    def estimate_cost(self, user_input: str, execution_mode: ExecutionMode = ExecutionMode.BALANCED) -> Dict[str, Any]:
        """
        Estimate the cost and time for processing a request.
        
        Args:
            user_input: The user's request as a string
            execution_mode: The execution mode to use
            
        Returns:
            Dict containing cost estimate, time estimate, and confidence
        """
        try:
            # Create a task for estimation
            from .core.models import Task
            task = Task(content=user_input, execution_mode=execution_mode)
            
            # Get cost estimate
            estimate = self.orchestration_layer.estimate_cost_and_time(task)
            
            return {
                "estimated_cost": estimate.estimated_cost,
                "estimated_time": estimate.estimated_time,
                "confidence": estimate.confidence,
                "currency": self.config.cost.currency
            }
            
        except Exception as e:
            self.logger.error(f"Cost estimation failed: {str(e)}")
            return {
                "estimated_cost": 0.0,
                "estimated_time": 0.0,
                "confidence": 0.0,
                "error": str(e)
            }
    
    def analyze_tradeoffs(self, user_input: str) -> Dict[str, Any]:
        """
        Analyze cost vs quality trade-offs for different execution modes.
        
        Args:
            user_input: The user's request as a string
            
        Returns:
            Dict containing analysis results and recommendations
        """
        try:
            from .core.models import Task
            task = Task(content=user_input, execution_mode=ExecutionMode.BALANCED)
            
            return self.orchestration_layer.analyze_cost_quality_tradeoffs(task)
            
        except Exception as e:
            self.logger.error(f"Trade-off analysis failed: {str(e)}")
            return {"error": str(e)}
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the current system status and health information.
        
        Returns:
            Dict containing system status information
        """
        try:
            # Get model registry status
            model_registry = self.factory.model_registry
            available_models = []
            
            for task_type in ["reasoning", "research", "code_generation"]:
                from .core.models import TaskType
                task_type_enum = TaskType(task_type)
                models = model_registry.get_models_for_task_type(task_type_enum)
                for model in models:
                    if model.get_model_id() not in [m["id"] for m in available_models]:
                        available_models.append({
                            "id": model.get_model_id(),
                            "capabilities": [task_type]
                        })
                    else:
                        # Add capability to existing model
                        for m in available_models:
                            if m["id"] == model.get_model_id():
                                if task_type not in m["capabilities"]:
                                    m["capabilities"].append(task_type)
            
            # Get resilience manager status
            from .core.failure_handling import resilience_manager
            health_status = resilience_manager.health_check()
            
            return {
                "status": "operational",
                "available_models": available_models,
                "health": health_status,
                "configuration": {
                    "default_execution_mode": self.config.execution.default_mode.value,
                    "max_parallel_executions": self.config.execution.max_parallel_executions,
                    "max_cost_per_request": self.config.cost.max_cost_per_request,
                    "arbitration_enabled": self.config.execution.enable_arbitration,
                    "synthesis_enabled": self.config.execution.enable_synthesis
                }
            }
            
        except Exception as e:
            self.logger.error(f"System status check failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def shutdown(self):
        """Gracefully shutdown the AI Council system."""
        self.logger.info("Shutting down AI Council application")
        
        # Perform any cleanup operations
        try:
            # Close any open resources
            # Note: ResilienceManager doesn't have reset_all_circuit_breakers method
            # Just log successful shutdown
            self.logger.info("AI Council application shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")


def main():
    """
    Main entry point for the AI Council application.
    
    This function provides a simple command-line interface for testing
    the AI Council system.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Council - Multi-Agent Orchestration System")
    parser.add_argument("--config", type=Path, help="Path to configuration file")
    parser.add_argument("--mode", choices=["fast", "balanced", "best_quality"], 
                       default="balanced", help="Execution mode")
    parser.add_argument("--estimate-only", action="store_true", 
                       help="Only estimate cost and time, don't execute")
    parser.add_argument("--analyze-tradeoffs", action="store_true",
                       help="Analyze cost vs quality trade-offs")
    parser.add_argument("--status", action="store_true",
                       help="Show system status and exit")
    parser.add_argument("--interactive", action="store_true",
                       help="Start interactive mode")
    parser.add_argument("request", nargs="?", help="User request to process")
    
    args = parser.parse_args()
    
    try:
        # Initialize AI Council
        ai_council = AICouncil(args.config)
        
        # Handle status request
        if args.status:
            status = ai_council.get_system_status()
            print("\n" + "="*60)
            print("AI COUNCIL SYSTEM STATUS")
            print("="*60)
            print(f"Status: {status.get('status', 'unknown')}")
            
            if 'available_models' in status:
                print(f"\nAvailable Models ({len(status['available_models'])}):")
                for model in status['available_models']:
                    print(f"  - {model['id']}: {', '.join(model['capabilities'])}")
            
            if 'health' in status:
                health = status['health']
                print(f"\nSystem Health: {health.get('overall_health', 'unknown')}")
                if 'circuit_breakers' in health:
                    print(f"Circuit Breakers: {len(health['circuit_breakers'])} active")
            
            if 'configuration' in status:
                config = status['configuration']
                print(f"\nConfiguration:")
                print(f"  Default Mode: {config.get('default_execution_mode', 'unknown')}")
                print(f"  Max Parallel: {config.get('max_parallel_executions', 'unknown')}")
                print(f"  Max Cost: ${config.get('max_cost_per_request', 0)}")
            
            return
        
        # Handle interactive mode
        if args.interactive:
            print("\n" + "="*60)
            print("AI COUNCIL INTERACTIVE MODE")
            print("="*60)
            print("Enter your requests (type 'quit' to exit, 'status' for system status)")
            print("Commands: estimate <request>, analyze <request>, help")
            
            while True:
                try:
                    user_input = input("\n> ").strip()
                    
                    if user_input.lower() in ['quit', 'exit']:
                        break
                    elif user_input.lower() == 'status':
                        status = ai_council.get_system_status()
                        print(f"System Status: {status.get('status', 'unknown')}")
                        continue
                    elif user_input.lower() == 'help':
                        print("Commands:")
                        print("  estimate <request> - Estimate cost and time")
                        print("  analyze <request>  - Analyze trade-offs")
                        print("  status            - Show system status")
                        print("  quit              - Exit interactive mode")
                        print("  <request>         - Process request")
                        continue
                    elif user_input.startswith('estimate '):
                        request = user_input[9:]
                        estimate = ai_council.estimate_cost(request, ExecutionMode(args.mode))
                        print(f"Estimated Cost: ${estimate.get('estimated_cost', 0):.4f}")
                        print(f"Estimated Time: {estimate.get('estimated_time', 0):.1f}s")
                        print(f"Confidence: {estimate.get('confidence', 0):.2f}")
                        continue
                    elif user_input.startswith('analyze '):
                        request = user_input[8:]
                        analysis = ai_council.analyze_tradeoffs(request)
                        if 'error' not in analysis:
                            print("Trade-off Analysis:")
                            for mode, data in analysis.items():
                                if mode != 'recommendations':
                                    print(f"  {mode}: ${data.get('total_cost', 0):.4f}, "
                                          f"{data.get('total_time', 0):.1f}s, "
                                          f"quality: {data.get('average_quality', 0):.2f}")
                        else:
                            print(f"Analysis failed: {analysis['error']}")
                        continue
                    
                    if not user_input:
                        continue
                    
                    # Process the request
                    execution_mode = ExecutionMode(args.mode)
                    response = ai_council.process_request(user_input, execution_mode)
                    
                    print(f"\nResponse (confidence: {response.overall_confidence:.2f}):")
                    print(response.content)
                    
                    if response.execution_metadata:
                        print(f"\nExecution Details:")
                        print(f"  Models Used: {', '.join(response.models_used)}")
                        print(f"  Execution Time: {response.execution_metadata.total_execution_time:.2f}s")
                        if response.cost_breakdown:
                            print(f"  Cost: ${response.cost_breakdown.total_cost:.4f}")
                    
                except KeyboardInterrupt:
                    print("\nExiting...")
                    break
                except Exception as e:
                    print(f"Error: {str(e)}")
            
            return
        
        # Handle single request
        if not args.request:
            parser.print_help()
            return
        
        execution_mode = ExecutionMode(args.mode)
        
        # Handle estimate-only request
        if args.estimate_only:
            estimate = ai_council.estimate_cost(args.request, execution_mode)
            print(f"\nCost Estimate for '{args.request[:50]}...':")
            print(f"  Estimated Cost: ${estimate.get('estimated_cost', 0):.4f}")
            print(f"  Estimated Time: {estimate.get('estimated_time', 0):.1f}s")
            print(f"  Confidence: {estimate.get('confidence', 0):.2f}")
            return
        
        # Handle trade-off analysis
        if args.analyze_tradeoffs:
            analysis = ai_council.analyze_tradeoffs(args.request)
            if 'error' not in analysis:
                print(f"\nTrade-off Analysis for '{args.request[:50]}...':")
                for mode, data in analysis.items():
                    if mode != 'recommendations':
                        print(f"\n{mode.upper()}:")
                        print(f"  Cost: ${data.get('total_cost', 0):.4f}")
                        print(f"  Time: {data.get('total_time', 0):.1f}s")
                        print(f"  Quality: {data.get('average_quality', 0):.2f}")
                
                if 'recommendations' in analysis:
                    print(f"\nRecommendations:")
                    for criterion, recommendation in analysis['recommendations'].items():
                        print(f"  {criterion.replace('_', ' ').title()}: {recommendation}")
            else:
                print(f"Analysis failed: {analysis['error']}")
            return
        
        # Process the request
        print(f"\nProcessing request in {execution_mode.value} mode...")
        response = ai_council.process_request(args.request, execution_mode)
        
        print(f"\n" + "="*60)
        print("AI COUNCIL RESPONSE")
        print("="*60)
        
        if response.success:
            print(f"Content: {response.content}")
            print(f"\nConfidence: {response.overall_confidence:.2f}")
            print(f"Models Used: {', '.join(response.models_used)}")
            
            if response.execution_metadata:
                print(f"Execution Time: {response.execution_metadata.total_execution_time:.2f}s")
                if response.cost_breakdown:
                    print(f"Total Cost: ${response.cost_breakdown.total_cost:.4f}")
        else:
            print(f"Request failed: {response.error_message}")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    finally:
        # Cleanup
        try:
            ai_council.shutdown()
        except:
            pass


if __name__ == "__main__":
    main()