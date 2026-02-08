"""
AI Council Orchestration Bridge for WebSocket integration.

This module bridges the AI Council Core with the FastAPI backend,
hooking into orchestration events to send real-time WebSocket updates.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from ai_council.factory import AICouncilFactory
from ai_council.core.models import ExecutionMode, FinalResponse, Task
from ai_council.core.interfaces import OrchestrationLayer
from ai_council.utils.config import AICouncilConfig

from app.services.websocket_manager import WebSocketManager
from app.services.cloud_ai.model_registry import MODEL_REGISTRY
from app.services.cloud_ai.adapter import CloudAIAdapter
from app.services.execution_mode_config import get_execution_mode_config
from app.core.config import settings
from app.core.provider_config import get_provider_config

logger = logging.getLogger(__name__)


class CouncilOrchestrationBridge:
    """
    Bridges AI Council Core with WebSocket updates for real-time orchestration tracking.
    
    This class:
    - Initializes AI Council with cloud AI adapters
    - Hooks into orchestration events at each layer
    - Sends WebSocket messages for real-time progress updates
    - Manages the complete request processing lifecycle
    """
    
    def __init__(self, websocket_manager: WebSocketManager):
        """
        Initialize the orchestration bridge.
        
        Args:
            websocket_manager: WebSocket manager for sending real-time updates
        """
        self.ws_manager = websocket_manager
        self.ai_council: Optional[OrchestrationLayer] = None
        self.current_request_id: Optional[str] = None
        self._pending_routing_assignments: List[Dict[str, Any]] = []
        self.provider_config = get_provider_config()
        self._available_providers: List[str] = []
        self._provider_selection_log: List[Dict[str, Any]] = []
        
        logger.info("CouncilOrchestrationBridge initialized")
    
    async def process_request(
        self,
        request_id: str,
        user_input: str,
        execution_mode: ExecutionMode
    ) -> FinalResponse:
        """
        Process a request through AI Council with real-time WebSocket updates.
        
        This method:
        1. Initializes AI Council with cloud adapters
        2. Sets up event hooks for WebSocket updates
        3. Processes the request through AI Council
        4. Returns the final response
        
        Args:
            request_id: Unique identifier for the request
            user_input: User's input text to process
            execution_mode: Execution mode (FAST, BALANCED, BEST_QUALITY)
            
        Returns:
            FinalResponse: The final synthesized response from AI Council
        """
        self.current_request_id = request_id
        self._pending_routing_assignments = []
        self._provider_selection_log = []
        
        try:
            logger.info(f"Processing request {request_id} in {execution_mode.value} mode")
            
            # Detect available providers at runtime
            self._available_providers = self._detect_available_providers()
            
            if not self._available_providers:
                logger.error("No AI providers available - cannot process request")
                await self.ws_manager.broadcast_progress(
                    request_id,
                    "error",
                    {
                        "message": "No AI providers configured or available",
                        "error": "Please configure at least one AI provider in .env file"
                    }
                )
                from ai_council.core.models import FinalResponse
                return FinalResponse(
                    content="",
                    overall_confidence=0.0,
                    success=False,
                    error_message="No AI providers configured or available"
                )
            
            logger.info(f"Available providers: {', '.join(self._available_providers)}")
            
            # Initialize AI Council with cloud AI adapters and execution mode config
            self.ai_council = self._create_ai_council(execution_mode)
            
            # Set up event hooks for WebSocket updates
            self._setup_event_hooks(request_id)
            
            # Send initial processing started message
            await self.ws_manager.broadcast_progress(
                request_id,
                "processing_started",
                {
                    "execution_mode": execution_mode.value,
                    "message": "Request processing started"
                }
            )
            
            # Process request through AI Council in a thread pool
            # (AI Council is synchronous, so we run it in a thread)
            response = await asyncio.to_thread(
                self.ai_council.process_request,
                user_input,
                execution_mode
            )
            
            # Send any pending routing assignments that were captured during execution
            if self._pending_routing_assignments:
                await self.ws_manager.broadcast_progress(
                    request_id,
                    "routing_complete",
                    {
                        "assignments": self._pending_routing_assignments,
                        "totalSubtasks": len(self._pending_routing_assignments),
                        "message": f"Routed {len(self._pending_routing_assignments)} subtasks to appropriate models"
                    }
                )
                logger.info(f"Sent routing_complete message with {len(self._pending_routing_assignments)} assignments")
            
            logger.info(f"Request {request_id} processed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error processing request {request_id}: {e}", exc_info=True)
            
            # Send error message via WebSocket
            await self.ws_manager.broadcast_progress(
                request_id,
                "error",
                {
                    "message": "Request processing failed",
                    "error": str(e)
                }
            )
            
            # Return error response
            from ai_council.core.models import FinalResponse
            return FinalResponse(
                content="",
                overall_confidence=0.0,
                success=False,
                error_message=f"Processing failed: {str(e)}"
            )
        finally:
            self.current_request_id = None
            self._pending_routing_assignments = []
            self._provider_selection_log = []
    
    def _detect_available_providers(self) -> List[str]:
        """
        Detect which providers are available at runtime based on API key configuration.
        
        Returns:
            List of available provider names
        """
        available = []
        configured_providers = self.provider_config.get_configured_providers()
        
        logger.info(f"Detecting available providers from {len(configured_providers)} configured providers")
        
        for provider_name in configured_providers:
            # Check if provider has valid API key or endpoint
            api_key = self.provider_config.get_api_key(provider_name)
            
            if provider_name == "ollama":
                # Ollama doesn't need API key, just check if endpoint is configured
                endpoint = self.provider_config.get_endpoint(provider_name)
                if endpoint:
                    available.append(provider_name)
                    logger.info(f"✓ Provider '{provider_name}' available (endpoint: {endpoint})")
            elif api_key:
                available.append(provider_name)
                logger.info(f"✓ Provider '{provider_name}' available (API key configured)")
            else:
                logger.warning(f"✗ Provider '{provider_name}' configured but no API key found")
        
        if not available:
            logger.warning("⚠️  No providers available! Please configure API keys in .env file")
        else:
            logger.info(f"Total available providers: {len(available)}")
        
        return available
    
    def _prioritize_providers_for_subtask(
        self,
        subtask_type: Any,
        available_models: List[str]
    ) -> List[str]:
        """
        Prioritize providers for a subtask based on: availability > cost > latency > capabilities.
        
        Args:
            subtask_type: The task type for the subtask
            available_models: List of model IDs that support this task type
            
        Returns:
            List of model IDs sorted by priority (highest priority first)
        """
        # Filter to only models from available providers
        available_provider_models = [
            model_id for model_id in available_models
            if any(model_id.startswith(f"{provider}-") for provider in self._available_providers)
        ]
        
        if not available_provider_models:
            logger.warning(f"No available provider models for task type: {subtask_type}")
            return []
        
        # Score each model based on priority criteria
        model_scores = []
        
        for model_id in available_provider_models:
            model_config = MODEL_REGISTRY.get(model_id)
            if not model_config:
                continue
            
            provider = model_config["provider"]
            
            # Calculate priority score (higher is better)
            # 1. Availability (already filtered, so all are available)
            availability_score = 100
            
            # 2. Cost (lower cost = higher score)
            avg_cost = (
                model_config["cost_per_input_token"] + 
                model_config["cost_per_output_token"]
            ) / 2
            # Normalize cost to 0-100 scale (assuming max cost of 0.00003)
            cost_score = max(0, 100 - (avg_cost / 0.00003 * 100))
            
            # 3. Latency (lower latency = higher score)
            latency = model_config.get("average_latency", 2.0)
            # Normalize latency to 0-100 scale (assuming max latency of 5s)
            latency_score = max(0, 100 - (latency / 5.0 * 100))
            
            # 4. Capabilities (more capabilities = higher score)
            capabilities_count = len(model_config.get("capabilities", []))
            capabilities_score = min(100, capabilities_count * 20)  # Max 5 capabilities
            
            # 5. Reliability (higher reliability = higher score)
            reliability_score = model_config.get("reliability_score", 0.9) * 100
            
            # Weighted total score
            # Availability: 40%, Cost: 25%, Latency: 15%, Capabilities: 10%, Reliability: 10%
            total_score = (
                availability_score * 0.40 +
                cost_score * 0.25 +
                latency_score * 0.15 +
                capabilities_score * 0.10 +
                reliability_score * 0.10
            )
            
            model_scores.append({
                "model_id": model_id,
                "provider": provider,
                "score": total_score,
                "cost": avg_cost,
                "latency": latency,
                "reliability": model_config.get("reliability_score", 0.9)
            })
        
        # Sort by score (highest first)
        model_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Log prioritization decision
        if model_scores:
            top_model = model_scores[0]
            logger.debug(
                f"Prioritized models for {subtask_type}: "
                f"top={top_model['model_id']} (score={top_model['score']:.1f}, "
                f"cost=${top_model['cost']:.6f}, latency={top_model['latency']:.1f}s)"
            )
        
        return [m["model_id"] for m in model_scores]
    
    def _log_provider_selection(
        self,
        subtask_id: str,
        subtask_type: Any,
        selected_model: str,
        reason: str,
        alternatives: List[str]
    ) -> None:
        """
        Log provider selection decision for a subtask.
        
        Args:
            subtask_id: ID of the subtask
            subtask_type: Type of the subtask
            selected_model: The model that was selected
            reason: Reason for selection
            alternatives: List of alternative models that were considered
        """
        model_config = MODEL_REGISTRY.get(selected_model, {})
        provider = model_config.get("provider", "unknown")
        
        selection_log = {
            "subtask_id": subtask_id,
            "subtask_type": str(subtask_type),
            "selected_model": selected_model,
            "selected_provider": provider,
            "reason": reason,
            "alternatives": alternatives,
            "cost_per_token": (
                model_config.get("cost_per_input_token", 0) +
                model_config.get("cost_per_output_token", 0)
            ) / 2,
            "latency": model_config.get("average_latency", 0),
            "reliability": model_config.get("reliability_score", 0),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self._provider_selection_log.append(selection_log)
        
        logger.info(
            f"Provider selection for subtask {subtask_id}: "
            f"selected={selected_model} (provider={provider}), "
            f"reason={reason}, "
            f"alternatives={len(alternatives)}"
        )
    
    def _create_ai_council(self, execution_mode: ExecutionMode) -> OrchestrationLayer:
        """
        Create AI Council instance with cloud AI adapters for available providers only.
        
        This method:
        1. Creates AI Council configuration with execution mode settings
        2. Initializes the factory
        3. Registers cloud AI models ONLY from available providers
        4. Returns the orchestration layer
        
        Args:
            execution_mode: The execution mode to configure AI Council with
        
        Returns:
            OrchestrationLayer: Configured AI Council orchestration layer
        """
        logger.info(f"Creating AI Council with cloud AI adapters for {execution_mode.value} mode")
        
        # Get execution mode configuration
        mode_config = get_execution_mode_config(execution_mode)
        logger.info(
            f"Execution mode config: parallelism={mode_config.max_parallel_executions}, "
            f"arbitration={mode_config.enable_arbitration}, "
            f"accuracy={mode_config.accuracy_requirement}, "
            f"cost_limit={mode_config.cost_limit}"
        )
        
        # Create AI Council configuration with execution mode settings
        config = AICouncilConfig()
        
        # Apply execution mode configuration to AI Council config
        config.execution.default_mode = execution_mode
        config.execution.max_parallel_executions = mode_config.max_parallel_executions
        config.execution.default_timeout_seconds = mode_config.timeout_seconds
        config.execution.max_retries = mode_config.max_retries
        config.execution.enable_arbitration = mode_config.enable_arbitration
        config.execution.enable_synthesis = mode_config.enable_synthesis
        config.execution.default_accuracy_requirement = mode_config.accuracy_requirement
        
        # Set cost limit if specified
        if mode_config.cost_limit is not None:
            config.cost.max_cost_per_request = mode_config.cost_limit
        
        # Create factory with configured settings
        factory = AICouncilFactory(config)
        
        # Register cloud AI models ONLY from available providers
        registered_count = 0
        skipped_count = 0
        
        for model_id, model_config in MODEL_REGISTRY.items():
            provider = model_config["provider"]
            
            # Skip if provider is not available
            if provider not in self._available_providers:
                logger.debug(f"Skipping model {model_id} - provider '{provider}' not available")
                skipped_count += 1
                continue
            
            try:
                # Get API key for this provider
                api_key = self.provider_config.get_api_key(provider)
                
                # For Ollama, use empty string as API key (not needed)
                if provider == "ollama":
                    api_key = ""
                
                if not api_key and provider != "ollama":
                    logger.warning(f"No API key for provider '{provider}', skipping model {model_id}")
                    skipped_count += 1
                    continue
                
                # Create cloud AI adapter
                adapter = CloudAIAdapter(
                    provider=provider,
                    model_id=model_config["model_name"],
                    api_key=api_key
                )
                
                # Create capabilities for the model
                from ai_council.core.models import ModelCapabilities, TaskType
                
                # Capabilities are already TaskType enums in MODEL_REGISTRY
                task_types = model_config["capabilities"]
                
                capabilities = ModelCapabilities(
                    task_types=task_types,
                    cost_per_token=(
                        model_config["cost_per_input_token"] + 
                        model_config["cost_per_output_token"]
                    ) / 2,
                    average_latency=model_config.get("average_latency", 2.0),
                    max_context_length=model_config.get("max_context", 8192),
                    reliability_score=model_config.get("reliability_score", 0.9),
                    strengths=[str(cap) for cap in model_config["capabilities"][:2]],
                    weaknesses=[]
                )
                
                # Register model with factory's registry
                factory.model_registry.register_model(adapter, capabilities)
                
                logger.info(f"✓ Registered model: {model_id} (provider: {provider})")
                registered_count += 1
                
            except Exception as e:
                logger.error(f"Failed to register model {model_id}: {e}")
                skipped_count += 1
                continue
        
        logger.info(
            f"Model registration complete: {registered_count} registered, "
            f"{skipped_count} skipped"
        )
        
        if registered_count == 0:
            raise RuntimeError(
                "No models could be registered. Please check your provider configuration."
            )
        
        # Create and return orchestration layer
        orchestration_layer = factory.create_orchestration_layer()
        logger.info("AI Council orchestration layer created successfully")
        
        return orchestration_layer
    
    def _get_api_key(self, provider: str) -> str:
        """
        Get API key for a cloud provider using the provider config.
        
        Args:
            provider: Provider name (groq, together, openrouter, huggingface, etc.)
            
        Returns:
            API key string (empty string if not configured)
        """
        api_key = self.provider_config.get_api_key(provider)
        
        if not api_key and provider != "ollama":
            logger.warning(f"No API key configured for provider: {provider}")
            return ""
        
        return api_key or ""
    
    def _setup_event_hooks(self, request_id: str) -> None:
        """
        Set up hooks to capture orchestration events and send WebSocket updates.
        
        This method wraps AI Council layer methods to intercept events and
        send real-time updates via WebSocket.
        
        Args:
            request_id: Unique identifier for the request
        """
        logger.info(f"Settings up event hooks for request {request_id}")
        
        # Hook into analysis layer
        self._hook_analysis_layer(request_id)
        
        # Hook into routing layer
        self._hook_routing_layer(request_id)
        
        # Hook into execution layer
        self._hook_execution_layer(request_id)
        
        # Hook into arbitration layer
        self._hook_arbitration_layer(request_id)
        
        # Hook into synthesis layer
        self._hook_synthesis_layer(request_id)
    
    def _hook_analysis_layer(self, request_id: str) -> None:
        """
        Hook into the analysis layer to send WebSocket updates.
        
        Wraps the analysis engine's methods to intercept analysis completion
        and send real-time updates.
        
        Args:
            request_id: Unique identifier for the request
        """
        analysis_engine = self.ai_council.analysis_engine
        
        # Store original methods
        original_analyze_intent = analysis_engine.analyze_intent
        original_determine_complexity = analysis_engine.determine_complexity
        
        # Track if analysis complete message has been sent
        analysis_complete_sent = {"sent": False}
        
        def hooked_analyze_intent(input_text: str):
            """Wrapped analyze_intent method."""
            result = original_analyze_intent(input_text)
            logger.debug(f"Analysis intent determined: {result.value if result else None}")
            return result
        
        def hooked_determine_complexity(input_text: str):
            """Wrapped determine_complexity method."""
            result = original_determine_complexity(input_text)
            logger.debug(f"Complexity determined: {result.value if result else None}")
            
            # Send analysis complete message after complexity is determined
            # (this is the last step in analysis)
            if not analysis_complete_sent["sent"]:
                analysis_complete_sent["sent"] = True
                
                # Get intent (call original method to avoid recursion)
                intent = original_analyze_intent(input_text)
                
                # Send WebSocket message asynchronously
                asyncio.create_task(
                    self.ws_manager.broadcast_progress(
                        request_id,
                        "analysis_complete",
                        {
                            "intent": intent.value if intent else None,
                            "complexity": result.value if result else None,
                            "message": "Input analysis completed"
                        }
                    )
                )
                logger.info(f"Analysis complete: intent={intent.value if intent else None}, complexity={result.value if result else None}")
            
            return result
        
        # Replace methods with hooked versions
        analysis_engine.analyze_intent = hooked_analyze_intent
        analysis_engine.determine_complexity = hooked_determine_complexity
        
        logger.debug("Analysis layer hooks installed")
    
    def _hook_routing_layer(self, request_id: str) -> None:
        """
        Hook into the routing layer to send WebSocket updates.
        
        Wraps the orchestration layer's _execute_parallel_group method to intercept
        routing decisions and send real-time updates about model assignments.
        Uses intelligent provider prioritization and fallback logic.
        
        Args:
            request_id: Unique identifier for the request
        """
        # Store original method
        original_execute_parallel_group = self.ai_council._execute_parallel_group
        
        # Track if routing complete message has been sent
        routing_complete_sent = {"sent": False}
        
        # Store routing assignments to be sent after thread execution
        self._pending_routing_assignments = []
        
        def hooked_execute_parallel_group(subtasks: List, execution_mode):
            """Wrapped _execute_parallel_group method."""
            
            # Before executing, capture routing decisions with intelligent prioritization
            if not routing_complete_sent["sent"]:
                routing_complete_sent["sent"] = True
                
                # Collect model assignments for each subtask
                assignments = []
                
                for subtask in subtasks:
                    try:
                        # Get available models for this task type
                        available_models = [
                            m.get_model_id() 
                            for m in self.ai_council.model_registry.get_models_for_task_type(subtask.task_type)
                        ]
                        
                        if not available_models:
                            logger.warning(f"No models available for subtask {subtask.id} with task type {subtask.task_type}")
                            continue
                        
                        # Prioritize models based on availability, cost, latency, capabilities
                        prioritized_models = self._prioritize_providers_for_subtask(
                            subtask.task_type,
                            available_models
                        )
                        
                        if not prioritized_models:
                            logger.warning(f"No prioritized models for subtask {subtask.id}")
                            continue
                        
                        # Use cost optimizer to determine which model will be selected
                        # It will pick from the prioritized list
                        optimization = self.ai_council.cost_optimizer.optimize_model_selection(
                            subtask, execution_mode, prioritized_models
                        )
                        
                        selected_model = optimization.recommended_model
                        
                        # Log provider selection decision
                        self._log_provider_selection(
                            subtask_id=subtask.id,
                            subtask_type=subtask.task_type,
                            selected_model=selected_model,
                            reason=optimization.reasoning,
                            alternatives=prioritized_models[1:6]  # Top 5 alternatives
                        )
                        
                        assignments.append({
                            "subtaskId": subtask.id,
                            "subtaskContent": subtask.content[:100],  # First 100 chars
                            "taskType": subtask.task_type.value if subtask.task_type else "unknown",
                            "modelId": selected_model,
                            "provider": MODEL_REGISTRY.get(selected_model, {}).get("provider", "unknown"),
                            "reason": optimization.reasoning,
                            "estimatedCost": optimization.estimated_cost,
                            "estimatedTime": optimization.estimated_time,
                            "alternativesConsidered": len(prioritized_models) - 1
                        })
                        
                        logger.debug(f"Routing subtask {subtask.id} to {selected_model}")
                            
                    except Exception as e:
                        logger.error(f"Error capturing routing decision for subtask {subtask.id}: {e}")
                        # Continue with other subtasks
                        continue
                
                # Store assignments to be sent after thread execution
                if assignments:
                    self._pending_routing_assignments = assignments
                    logger.info(f"Routing complete: {len(assignments)} subtasks routed across {len(set(a['provider'] for a in assignments))} providers")
            
            # Call original method
            return original_execute_parallel_group(subtasks, execution_mode)
        
        # Replace method with hooked version
        self.ai_council._execute_parallel_group = hooked_execute_parallel_group
        
        logger.debug("Routing layer hooks installed with intelligent provider selection")
    
    def _hook_execution_layer(self, request_id: str) -> None:
        """
        Hook into the execution layer to send WebSocket updates for subtask completion.
        
        Wraps the execution agent's execute method to intercept subtask execution
        completion and send real-time progress updates including confidence, cost,
        and execution time. Implements intelligent fallback when primary provider fails.
        
        Args:
            request_id: Unique identifier for the request
        """
        # Get execution agent from AI Council orchestration layer
        if not hasattr(self.ai_council, 'execution_agent'):
            logger.warning("AI Council does not have execution_agent attribute")
            return
        
        execution_agent = self.ai_council.execution_agent
        
        # Store original execute method
        original_execute = execution_agent.execute
        
        def hooked_execute(subtask, model):
            """Wrapped execute method with fallback logic."""
            primary_model = model
            primary_model_id = model.get_model_id()
            
            try:
                # Call original execute method
                response = original_execute(subtask, model)
                
                # If successful, track which provider handled this subtask
                provider = MODEL_REGISTRY.get(primary_model_id, {}).get("provider", "unknown")
                
                # Send WebSocket message with execution progress
                try:
                    # Extract metrics from the response
                    confidence = 0.0
                    cost = 0.0
                    execution_time = 0.0
                    
                    if response.self_assessment:
                        confidence = response.self_assessment.confidence_score
                        cost = response.self_assessment.estimated_cost or 0.0
                        execution_time = response.self_assessment.execution_time or 0.0
                    
                    # Prepare progress data with provider information
                    progress_data = {
                        "subtaskId": subtask.id,
                        "subtaskContent": subtask.content[:100],  # First 100 chars
                        "modelId": response.model_used,
                        "provider": provider,
                        "status": "completed" if response.success else "failed",
                        "confidence": confidence,
                        "cost": cost,
                        "executionTime": execution_time,
                        "success": response.success,
                        "usedFallback": False
                    }
                    
                    # Add error message if failed
                    if not response.success and response.error_message:
                        progress_data["errorMessage"] = response.error_message
                    
                    # Send WebSocket message asynchronously
                    asyncio.create_task(
                        self.ws_manager.broadcast_progress(
                            request_id,
                            "execution_progress",
                            progress_data
                        )
                    )
                    
                    logger.info(
                        f"Execution progress: subtask={subtask.id}, "
                        f"model={response.model_used}, "
                        f"provider={provider}, "
                        f"confidence={confidence:.2f}, "
                        f"cost=${cost:.4f}, "
                        f"time={execution_time:.2f}s"
                    )
                    
                except Exception as e:
                    logger.error(f"Error sending execution progress update: {e}")
                    # Don't fail the execution if WebSocket update fails
                
                return response
                
            except Exception as e:
                # Primary provider failed - attempt fallback
                logger.warning(
                    f"Primary provider failed for subtask {subtask.id}: {e}. "
                    f"Attempting fallback..."
                )
                
                # Get alternative models for this task type
                available_models = [
                    m.get_model_id() 
                    for m in self.ai_council.model_registry.get_models_for_task_type(subtask.task_type)
                ]
                
                # Remove the failed model
                fallback_models = [m for m in available_models if m != primary_model_id]
                
                if not fallback_models:
                    logger.error(f"No fallback models available for subtask {subtask.id}")
                    raise  # Re-raise original exception
                
                # Prioritize fallback models
                prioritized_fallbacks = self._prioritize_providers_for_subtask(
                    subtask.task_type,
                    fallback_models
                )
                
                if not prioritized_fallbacks:
                    logger.error(f"No prioritized fallback models for subtask {subtask.id}")
                    raise  # Re-raise original exception
                
                # Try the top fallback model
                fallback_model_id = prioritized_fallbacks[0]
                fallback_model = None
                
                # Find the model object
                for m in self.ai_council.model_registry.get_models_for_task_type(subtask.task_type):
                    if m.get_model_id() == fallback_model_id:
                        fallback_model = m
                        break
                
                if not fallback_model:
                    logger.error(f"Could not find fallback model object for {fallback_model_id}")
                    raise  # Re-raise original exception
                
                logger.info(
                    f"Using fallback model {fallback_model_id} for subtask {subtask.id} "
                    f"after {primary_model_id} failed"
                )
                
                # Log the fallback decision
                self._log_provider_selection(
                    subtask_id=subtask.id,
                    subtask_type=subtask.task_type,
                    selected_model=fallback_model_id,
                    reason=f"Fallback after {primary_model_id} failed: {str(e)}",
                    alternatives=prioritized_fallbacks[1:6]
                )
                
                try:
                    # Execute with fallback model
                    response = original_execute(subtask, fallback_model)
                    
                    # Track which provider handled this subtask (fallback)
                    fallback_provider = MODEL_REGISTRY.get(fallback_model_id, {}).get("provider", "unknown")
                    
                    # Send WebSocket message with execution progress
                    try:
                        confidence = 0.0
                        cost = 0.0
                        execution_time = 0.0
                        
                        if response.self_assessment:
                            confidence = response.self_assessment.confidence_score
                            cost = response.self_assessment.estimated_cost or 0.0
                            execution_time = response.self_assessment.execution_time or 0.0
                        
                        progress_data = {
                            "subtaskId": subtask.id,
                            "subtaskContent": subtask.content[:100],
                            "modelId": response.model_used,
                            "provider": fallback_provider,
                            "status": "completed" if response.success else "failed",
                            "confidence": confidence,
                            "cost": cost,
                            "executionTime": execution_time,
                            "success": response.success,
                            "usedFallback": True,
                            "primaryModelFailed": primary_model_id,
                            "fallbackReason": str(e)
                        }
                        
                        if not response.success and response.error_message:
                            progress_data["errorMessage"] = response.error_message
                        
                        asyncio.create_task(
                            self.ws_manager.broadcast_progress(
                                request_id,
                                "execution_progress",
                                progress_data
                            )
                        )
                        
                        logger.info(
                            f"Fallback execution success: subtask={subtask.id}, "
                            f"fallback_model={response.model_used}, "
                            f"provider={fallback_provider}, "
                            f"confidence={confidence:.2f}"
                        )
                        
                    except Exception as ws_error:
                        logger.error(f"Error sending fallback execution progress: {ws_error}")
                    
                    return response
                    
                except Exception as fallback_error:
                    logger.error(
                        f"Fallback model {fallback_model_id} also failed for subtask {subtask.id}: "
                        f"{fallback_error}"
                    )
                    raise  # Re-raise fallback exception
        
        # Replace method with hooked version
        execution_agent.execute = hooked_execute
        
        logger.debug("Execution layer hooks installed with intelligent fallback")
    
    def _hook_arbitration_layer(self, request_id: str) -> None:
        """
        Hook into the arbitration layer to send WebSocket updates for conflict resolution.
        
        Wraps the orchestration layer's _arbitrate_with_protection method to intercept
        arbitration decisions and send real-time updates including conflicting results
        and selected result with reasoning.
        
        Args:
            request_id: Unique identifier for the request
        """
        # Store original method
        original_arbitrate_with_protection = self.ai_council._arbitrate_with_protection
        
        def hooked_arbitrate_with_protection(responses):
            """Wrapped _arbitrate_with_protection method."""
            # Call original arbitration method
            arbitration_result = original_arbitrate_with_protection(responses)
            
            # Send WebSocket message with arbitration decisions
            try:
                # Check if there were any conflicts resolved
                if arbitration_result.conflicts_resolved:
                    # Prepare arbitration data
                    arbitration_data = {
                        "conflictsDetected": len(arbitration_result.conflicts_resolved),
                        "decisions": []
                    }
                    
                    # Add details for each conflict resolution
                    for resolution in arbitration_result.conflicts_resolved:
                        decision = {
                            "chosenResponseId": resolution.chosen_response_id,
                            "reasoning": resolution.reasoning,
                            "confidence": resolution.confidence
                        }
                        arbitration_data["decisions"].append(decision)
                    
                    # Add information about conflicting responses
                    # Group responses by subtask to show what was being arbitrated
                    conflicting_responses = []
                    for response in responses:
                        conflicting_responses.append({
                            "responseId": f"{response.subtask_id}_{response.model_used}",
                            "modelId": response.model_used,
                            "subtaskId": response.subtask_id,
                            "confidence": (
                                response.self_assessment.confidence_score 
                                if response.self_assessment else 0.0
                            ),
                            "success": response.success
                        })
                    
                    arbitration_data["conflictingResults"] = conflicting_responses
                    arbitration_data["message"] = (
                        f"Arbitration resolved {len(arbitration_result.conflicts_resolved)} "
                        f"conflicts between {len(responses)} responses"
                    )
                    
                    # Send WebSocket message asynchronously
                    asyncio.create_task(
                        self.ws_manager.broadcast_progress(
                            request_id,
                            "arbitration_decision",
                            arbitration_data
                        )
                    )
                    
                    logger.info(
                        f"Arbitration decision: resolved {len(arbitration_result.conflicts_resolved)} "
                        f"conflicts from {len(responses)} responses"
                    )
                else:
                    # No conflicts detected, but still send a message for transparency
                    arbitration_data = {
                        "conflictsDetected": 0,
                        "decisions": [],
                        "conflictingResults": [],
                        "message": f"No conflicts detected among {len(responses)} responses"
                    }
                    
                    asyncio.create_task(
                        self.ws_manager.broadcast_progress(
                            request_id,
                            "arbitration_decision",
                            arbitration_data
                        )
                    )
                    
                    logger.info(f"Arbitration: no conflicts detected among {len(responses)} responses")
                
            except Exception as e:
                logger.error(f"Error sending arbitration decision update: {e}")
                # Don't fail the arbitration if WebSocket update fails
            
            return arbitration_result
        
        # Replace method with hooked version
        self.ai_council._arbitrate_with_protection = hooked_arbitrate_with_protection
        
        logger.debug("Arbitration layer hooks installed")
    
    def _hook_synthesis_layer(self, request_id: str) -> None:
        """
        Hook into the synthesis layer to send WebSocket updates for synthesis progress.
        
        Wraps the orchestration layer's _synthesize_with_protection method to intercept
        synthesis progress and send real-time updates including synthesis progress and
        final response with all metadata.
        
        Args:
            request_id: Unique identifier for the request
        """
        # Store original method
        original_synthesize_with_protection = self.ai_council._synthesize_with_protection
        
        def hooked_synthesize_with_protection(validated_responses):
            """Wrapped _synthesize_with_protection method."""
            
            # Send synthesis started message
            try:
                asyncio.create_task(
                    self.ws_manager.broadcast_progress(
                        request_id,
                        "synthesis_progress",
                        {
                            "stage": "started",
                            "message": f"Beginning synthesis of {len(validated_responses)} validated responses",
                            "totalResponses": len(validated_responses)
                        }
                    )
                )
                logger.info(f"Synthesis started: processing {len(validated_responses)} validated responses")
            except Exception as e:
                logger.error(f"Error sending synthesis started update: {e}")
            
            # Call original synthesis method
            final_response = original_synthesize_with_protection(validated_responses)
            
            # Send synthesis complete message with final response and all metadata
            try:
                # Prepare comprehensive final response data
                final_response_data = {
                    "stage": "complete",
                    "content": final_response.content,
                    "overallConfidence": final_response.overall_confidence,
                    "success": final_response.success,
                    "modelsUsed": final_response.models_used if final_response.models_used else [],
                    "message": "Synthesis complete - final response generated"
                }
                
                # Add cost breakdown if available
                if final_response.cost_breakdown:
                    final_response_data["costBreakdown"] = {
                        "totalCost": final_response.cost_breakdown.total_cost,
                        "executionTime": final_response.cost_breakdown.execution_time,
                        "modelCosts": final_response.cost_breakdown.model_costs if hasattr(final_response.cost_breakdown, 'model_costs') else {},
                        "tokenUsage": final_response.cost_breakdown.token_usage if hasattr(final_response.cost_breakdown, 'token_usage') else {}
                    }
                
                # Add execution metadata if available
                if hasattr(final_response, 'execution_metadata') and final_response.execution_metadata:
                    metadata = final_response.execution_metadata
                    final_response_data["executionMetadata"] = {
                        "executionPath": metadata.execution_path if hasattr(metadata, 'execution_path') else [],
                        "totalExecutionTime": metadata.total_execution_time if hasattr(metadata, 'total_execution_time') else 0.0,
                        "parallelExecutions": metadata.parallel_executions if hasattr(metadata, 'parallel_executions') else 0
                    }
                
                # Add provider selection log to metadata
                if self._provider_selection_log:
                    final_response_data["providerSelectionLog"] = self._provider_selection_log
                    
                    # Summarize provider usage
                    provider_usage = {}
                    for log_entry in self._provider_selection_log:
                        provider = log_entry["selected_provider"]
                        provider_usage[provider] = provider_usage.get(provider, 0) + 1
                    
                    final_response_data["providerUsageSummary"] = provider_usage
                    
                    logger.info(
                        f"Provider usage summary: "
                        f"{', '.join(f'{p}={c}' for p, c in provider_usage.items())}"
                    )
                
                # Add error message if synthesis failed
                if not final_response.success and final_response.error_message:
                    final_response_data["errorMessage"] = final_response.error_message
                
                # Send synthesis progress update
                asyncio.create_task(
                    self.ws_manager.broadcast_progress(
                        request_id,
                        "synthesis_progress",
                        final_response_data
                    )
                )
                
                # Also send final_response message for backwards compatibility
                asyncio.create_task(
                    self.ws_manager.broadcast_progress(
                        request_id,
                        "final_response",
                        final_response_data
                    )
                )
                
                logger.info(
                    f"Synthesis complete: confidence={final_response.overall_confidence:.2f}, "
                    f"success={final_response.success}, "
                    f"models={len(final_response.models_used) if final_response.models_used else 0}"
                )
                
            except Exception as e:
                logger.error(f"Error sending synthesis complete update: {e}")
                # Don't fail the synthesis if WebSocket update fails
            
            return final_response
        
        # Replace method with hooked version
        self.ai_council._synthesize_with_protection = hooked_synthesize_with_protection
        
        logger.debug("Synthesis layer hooks installed")


# Global instance (will be initialized in main.py)
council_bridge: Optional[CouncilOrchestrationBridge] = None


def get_council_bridge() -> CouncilOrchestrationBridge:
    """
    Get the global CouncilOrchestrationBridge instance.
    
    Returns:
        CouncilOrchestrationBridge: The global bridge instance
    """
    global council_bridge
    if council_bridge is None:
        from app.services.websocket_manager import websocket_manager
        council_bridge = CouncilOrchestrationBridge(websocket_manager)
    return council_bridge

