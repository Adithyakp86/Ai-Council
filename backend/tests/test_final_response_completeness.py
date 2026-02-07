"""Property-based tests for final response message completeness.

**Property 27: Final Response Message Completeness**
**Validates: Requirements 6.8**
Test that final message includes all required fields
"""

import pytest
import asyncio
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add ai_council to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from app.services.council_orchestration_bridge import CouncilOrchestrationBridge
from app.services.websocket_manager import WebSocketManager
from ai_council.core.models import (
    ExecutionMode, AgentResponse, SelfAssessment, RiskLevel,
    FinalResponse, CostBreakdown
)
from datetime import datetime


class TestFinalResponseCompleteness:
    """Test that final response message includes all required fields."""
    
    @pytest.mark.asyncio
    @given(
        content_length=st.integers(min_value=10, max_value=1000),
        overall_confidence=st.floats(min_value=0.0, max_value=1.0),
        total_cost=st.floats(min_value=0.0001, max_value=10.0),
        execution_time=st.floats(min_value=0.1, max_value=120.0),
        num_models=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=20, deadline=None)
    async def test_final_response_includes_all_required_fields(
        self, content_length, overall_confidence, total_cost, execution_time, num_models
    ):
        """Property: Final response message includes all required fields.
        
        This test verifies that when processing completes, the final WebSocket message
        includes all required fields as specified in Requirement 6.8:
        - content: The synthesized final content
        - confidence: Overall confidence score
        - execution_time: Total execution time
        - total_cost: Total cost of processing
        - models_used: List of models that were used
        - orchestration_metadata: Metadata about the orchestration process
        """
        # Create mock WebSocket manager
        ws_manager = Mock(spec=WebSocketManager)
        ws_manager.broadcast_progress = AsyncMock(return_value=True)
        
        # Create bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Generate test content
        content = "A" * content_length
        
        # Create mock models used
        models_used = [f"model-{i}" for i in range(num_models)]
        
        # Create mock cost breakdown
        mock_cost_breakdown = Mock(spec=CostBreakdown)
        mock_cost_breakdown.total_cost = total_cost
        mock_cost_breakdown.execution_time = execution_time
        mock_cost_breakdown.model_costs = {model: total_cost / num_models for model in models_used}
        mock_cost_breakdown.token_usage = {model: 100 * (i + 1) for i, model in enumerate(models_used)}
        
        # Create mock execution metadata
        mock_execution_metadata = Mock()
        mock_execution_metadata.execution_path = ["analysis", "routing", "execution", "synthesis"]
        mock_execution_metadata.total_execution_time = execution_time
        mock_execution_metadata.parallel_executions = num_models
        
        # Create mock final response
        mock_final_response = Mock(spec=FinalResponse)
        mock_final_response.content = content
        mock_final_response.overall_confidence = overall_confidence
        mock_final_response.success = True
        mock_final_response.error_message = None
        mock_final_response.models_used = models_used
        mock_final_response.cost_breakdown = mock_cost_breakdown
        mock_final_response.execution_metadata = mock_execution_metadata
        
        # Mock the AI Council creation
        with patch.object(bridge, '_create_ai_council') as mock_create:
            mock_orchestration = Mock()
            
            def mock_synthesize_with_protection(validated_responses):
                return mock_final_response
            
            mock_orchestration._synthesize_with_protection = mock_synthesize_with_protection
            mock_orchestration.analysis_engine = Mock()
            mock_orchestration.model_registry = Mock()
            mock_orchestration.cost_optimizer = Mock()
            mock_orchestration.execution_agent = Mock()
            
            mock_create.return_value = mock_orchestration
            
            # Initialize AI Council and setup hooks
            bridge.ai_council = bridge._create_ai_council()
            bridge._setup_event_hooks("test-request-completeness-123")
            
            # Call synthesis to trigger the hook
            result = bridge.ai_council._synthesize_with_protection([])
            
            # Give async tasks time to complete
            await asyncio.sleep(0.1)
            
            # Verify that broadcast_progress was called
            assert ws_manager.broadcast_progress.called, "WebSocket broadcast should be called"
            
            # Get all calls
            calls = ws_manager.broadcast_progress.call_args_list
            
            # Find the final_response message
            final_response_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "final_response"
            ]
            
            assert len(final_response_calls) > 0, "Should have at least one final_response message"
            
            # Get the final response data
            final_call = final_response_calls[0]
            assert final_call[0][0] == "test-request-completeness-123", "Request ID should match"
            assert final_call[0][1] == "final_response", "Event type should be final_response"
            
            data = final_call[0][2]
            
            # Verify all required fields are present (Requirement 6.8)
            assert "content" in data, "Final response must include 'content' field"
            assert "overallConfidence" in data, "Final response must include 'overallConfidence' field"
            assert "success" in data, "Final response must include 'success' field"
            assert "modelsUsed" in data, "Final response must include 'modelsUsed' field"
            assert "costBreakdown" in data, "Final response must include 'costBreakdown' field"
            assert "executionMetadata" in data, "Final response must include 'executionMetadata' field"
            
            # Verify field values match expected values
            assert data["content"] == content, "Content should match"
            assert abs(data["overallConfidence"] - overall_confidence) < 0.01, "Confidence should match"
            assert data["success"] is True, "Success should be True"
            assert len(data["modelsUsed"]) == num_models, f"Should include all {num_models} models"
            
            # Verify models_used contains all expected models
            for model in models_used:
                assert model in data["modelsUsed"], f"Should include model {model}"
            
            # Verify cost breakdown structure and values
            cost_breakdown = data["costBreakdown"]
            assert "totalCost" in cost_breakdown, "Cost breakdown must include 'totalCost'"
            assert "executionTime" in cost_breakdown, "Cost breakdown must include 'executionTime'"
            assert "modelCosts" in cost_breakdown, "Cost breakdown must include 'modelCosts'"
            assert "tokenUsage" in cost_breakdown, "Cost breakdown must include 'tokenUsage'"
            
            assert abs(cost_breakdown["totalCost"] - total_cost) < 0.01, "Total cost should match"
            assert abs(cost_breakdown["executionTime"] - execution_time) < 0.1, "Execution time should match"
            
            # Verify execution metadata structure and values
            exec_metadata = data["executionMetadata"]
            assert "executionPath" in exec_metadata, "Execution metadata must include 'executionPath'"
            assert "totalExecutionTime" in exec_metadata, "Execution metadata must include 'totalExecutionTime'"
            assert "parallelExecutions" in exec_metadata, "Execution metadata must include 'parallelExecutions'"
            
            assert isinstance(exec_metadata["executionPath"], list), "Execution path should be a list"
            assert len(exec_metadata["executionPath"]) > 0, "Execution path should not be empty"
            assert abs(exec_metadata["totalExecutionTime"] - execution_time) < 0.1, "Total execution time should match"
            assert exec_metadata["parallelExecutions"] == num_models, "Parallel executions should match"
    
    @pytest.mark.asyncio
    async def test_final_response_completeness_with_minimal_data(self):
        """Test that final response includes all required fields even with minimal data."""
        # Create mock WebSocket manager
        ws_manager = Mock(spec=WebSocketManager)
        ws_manager.broadcast_progress = AsyncMock(return_value=True)
        
        # Create bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Create minimal mock cost breakdown
        mock_cost_breakdown = Mock(spec=CostBreakdown)
        mock_cost_breakdown.total_cost = 0.001
        mock_cost_breakdown.execution_time = 0.5
        mock_cost_breakdown.model_costs = {"minimal-model": 0.001}
        mock_cost_breakdown.token_usage = {"minimal-model": 10}
        
        # Create minimal mock execution metadata
        mock_execution_metadata = Mock()
        mock_execution_metadata.execution_path = ["analysis", "synthesis"]
        mock_execution_metadata.total_execution_time = 0.5
        mock_execution_metadata.parallel_executions = 1
        
        # Create minimal mock final response
        mock_final_response = Mock(spec=FinalResponse)
        mock_final_response.content = "Minimal response"
        mock_final_response.overall_confidence = 0.5
        mock_final_response.success = True
        mock_final_response.error_message = None
        mock_final_response.models_used = ["minimal-model"]
        mock_final_response.cost_breakdown = mock_cost_breakdown
        mock_final_response.execution_metadata = mock_execution_metadata
        
        # Mock the AI Council creation
        with patch.object(bridge, '_create_ai_council') as mock_create:
            mock_orchestration = Mock()
            
            def mock_synthesize_with_protection(validated_responses):
                return mock_final_response
            
            mock_orchestration._synthesize_with_protection = mock_synthesize_with_protection
            mock_orchestration.analysis_engine = Mock()
            mock_orchestration.model_registry = Mock()
            mock_orchestration.cost_optimizer = Mock()
            mock_orchestration.execution_agent = Mock()
            
            mock_create.return_value = mock_orchestration
            
            # Initialize and setup hooks
            bridge.ai_council = bridge._create_ai_council()
            bridge._setup_event_hooks("test-request-minimal-456")
            
            # Call synthesis
            result = bridge.ai_council._synthesize_with_protection([])
            
            # Give async tasks time to complete
            await asyncio.sleep(0.1)
            
            # Get final_response message
            calls = ws_manager.broadcast_progress.call_args_list
            final_response_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "final_response"
            ]
            
            assert len(final_response_calls) > 0, "Should have final_response message"
            
            data = final_response_calls[0][0][2]
            
            # Verify all required fields are present even with minimal data
            required_fields = [
                "content", "overallConfidence", "success", "modelsUsed",
                "costBreakdown", "executionMetadata"
            ]
            
            for field in required_fields:
                assert field in data, f"Final response must include '{field}' field"
            
            # Verify nested required fields in costBreakdown
            cost_required_fields = ["totalCost", "executionTime", "modelCosts", "tokenUsage"]
            for field in cost_required_fields:
                assert field in data["costBreakdown"], f"Cost breakdown must include '{field}' field"
            
            # Verify nested required fields in executionMetadata
            metadata_required_fields = ["executionPath", "totalExecutionTime", "parallelExecutions"]
            for field in metadata_required_fields:
                assert field in data["executionMetadata"], f"Execution metadata must include '{field}' field"
    
    @pytest.mark.asyncio
    async def test_final_response_completeness_on_failure(self):
        """Test that final response includes all required fields even when synthesis fails."""
        # Create mock WebSocket manager
        ws_manager = Mock(spec=WebSocketManager)
        ws_manager.broadcast_progress = AsyncMock(return_value=True)
        
        # Create bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Create mock final response indicating failure
        mock_final_response = Mock(spec=FinalResponse)
        mock_final_response.content = ""
        mock_final_response.overall_confidence = 0.0
        mock_final_response.success = False
        mock_final_response.error_message = "Synthesis failed: test error"
        mock_final_response.models_used = []
        mock_final_response.cost_breakdown = None
        mock_final_response.execution_metadata = None
        
        # Mock the AI Council creation
        with patch.object(bridge, '_create_ai_council') as mock_create:
            mock_orchestration = Mock()
            
            def mock_synthesize_with_protection(validated_responses):
                return mock_final_response
            
            mock_orchestration._synthesize_with_protection = mock_synthesize_with_protection
            mock_orchestration.analysis_engine = Mock()
            mock_orchestration.model_registry = Mock()
            mock_orchestration.cost_optimizer = Mock()
            mock_orchestration.execution_agent = Mock()
            
            mock_create.return_value = mock_orchestration
            
            # Initialize and setup hooks
            bridge.ai_council = bridge._create_ai_council()
            bridge._setup_event_hooks("test-request-failure-789")
            
            # Call synthesis
            result = bridge.ai_council._synthesize_with_protection([])
            
            # Give async tasks time to complete
            await asyncio.sleep(0.1)
            
            # Get final_response message
            calls = ws_manager.broadcast_progress.call_args_list
            final_response_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "final_response"
            ]
            
            assert len(final_response_calls) > 0, "Should have final_response message even on failure"
            
            data = final_response_calls[0][0][2]
            
            # Verify core required fields are present even on failure
            assert "content" in data, "Must include 'content' field"
            assert "overallConfidence" in data, "Must include 'overallConfidence' field"
            assert "success" in data, "Must include 'success' field"
            assert "modelsUsed" in data, "Must include 'modelsUsed' field"
            
            # Verify failure is indicated
            assert data["success"] is False, "Success should be False"
            assert "errorMessage" in data, "Should include 'errorMessage' on failure"
            assert "test error" in data["errorMessage"], "Error message should be included"
            assert data["overallConfidence"] == 0.0, "Confidence should be 0.0 on failure"
            assert data["content"] == "", "Content should be empty on failure"
            assert len(data["modelsUsed"]) == 0, "Models used should be empty on failure"
    
    @pytest.mark.asyncio
    @given(
        num_responses=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=10, deadline=None)
    async def test_final_response_sent_after_synthesis_complete(self, num_responses):
        """Property: Final response message is sent after synthesis completes.
        
        This test verifies that:
        1. The final_response message is sent after synthesis completes
        2. The message includes data from all validated responses
        3. The timing is correct (after synthesis, not before)
        """
        # Create mock WebSocket manager
        ws_manager = Mock(spec=WebSocketManager)
        ws_manager.broadcast_progress = AsyncMock(return_value=True)
        
        # Create bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Create mock validated responses
        mock_responses = []
        for i in range(num_responses):
            self_assessment = Mock(spec=SelfAssessment)
            self_assessment.confidence_score = 0.7 + (i * 0.02)
            self_assessment.estimated_cost = 0.01
            self_assessment.execution_time = 1.0
            self_assessment.token_usage = 100
            self_assessment.risk_level = RiskLevel.LOW
            
            response = Mock(spec=AgentResponse)
            response.subtask_id = f"subtask-timing-{i}"
            response.model_used = f"model-{i % 3}"  # Use 3 different models
            response.content = f"Response {i}"
            response.self_assessment = self_assessment
            response.success = True
            response.error_message = None
            mock_responses.append(response)
        
        # Create mock final response
        models_used = list(set([r.model_used for r in mock_responses]))
        
        mock_cost_breakdown = Mock(spec=CostBreakdown)
        mock_cost_breakdown.total_cost = 0.01 * num_responses
        mock_cost_breakdown.execution_time = 1.0 * num_responses
        mock_cost_breakdown.model_costs = {model: 0.01 for model in models_used}
        mock_cost_breakdown.token_usage = {model: 100 for model in models_used}
        
        mock_execution_metadata = Mock()
        mock_execution_metadata.execution_path = ["analysis", "routing", "execution", "synthesis"]
        mock_execution_metadata.total_execution_time = 1.0 * num_responses
        mock_execution_metadata.parallel_executions = len(models_used)
        
        mock_final_response = Mock(spec=FinalResponse)
        mock_final_response.content = f"Synthesized from {num_responses} responses"
        mock_final_response.overall_confidence = 0.8
        mock_final_response.success = True
        mock_final_response.error_message = None
        mock_final_response.models_used = models_used
        mock_final_response.cost_breakdown = mock_cost_breakdown
        mock_final_response.execution_metadata = mock_execution_metadata
        
        # Mock the AI Council creation
        with patch.object(bridge, '_create_ai_council') as mock_create:
            mock_orchestration = Mock()
            
            def mock_synthesize_with_protection(validated_responses):
                return mock_final_response
            
            mock_orchestration._synthesize_with_protection = mock_synthesize_with_protection
            mock_orchestration.analysis_engine = Mock()
            mock_orchestration.model_registry = Mock()
            mock_orchestration.cost_optimizer = Mock()
            mock_orchestration.execution_agent = Mock()
            
            mock_create.return_value = mock_orchestration
            
            # Initialize and setup hooks
            bridge.ai_council = bridge._create_ai_council()
            bridge._setup_event_hooks("test-request-timing-prop")
            
            # Call synthesis
            result = bridge.ai_council._synthesize_with_protection(mock_responses)
            
            # Give async tasks time to complete
            await asyncio.sleep(0.1)
            
            # Get all calls
            calls = ws_manager.broadcast_progress.call_args_list
            
            # Find synthesis_progress messages
            synthesis_progress_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "synthesis_progress"
            ]
            
            # Find final_response messages
            final_response_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "final_response"
            ]
            
            # Verify both message types were sent
            assert len(synthesis_progress_calls) >= 2, "Should have synthesis_progress messages"
            assert len(final_response_calls) >= 1, "Should have final_response message"
            
            # Verify the final_response message includes all required fields
            final_data = final_response_calls[0][0][2]
            
            required_fields = [
                "content", "overallConfidence", "success", "modelsUsed",
                "costBreakdown", "executionMetadata"
            ]
            
            for field in required_fields:
                assert field in final_data, f"Final response must include '{field}' field"
            
            # Verify the data reflects the synthesis of all responses
            assert f"{num_responses} responses" in final_data["content"], "Content should reference number of responses"
            assert len(final_data["modelsUsed"]) == len(models_used), "Should include all unique models"
    
    @pytest.mark.asyncio
    async def test_final_response_includes_orchestration_metadata(self):
        """Test that final response includes comprehensive orchestration metadata."""
        # Create mock WebSocket manager
        ws_manager = Mock(spec=WebSocketManager)
        ws_manager.broadcast_progress = AsyncMock(return_value=True)
        
        # Create bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Create detailed mock execution metadata
        mock_execution_metadata = Mock()
        mock_execution_metadata.execution_path = [
            "analysis", "decomposition", "routing", "execution", 
            "arbitration", "synthesis"
        ]
        mock_execution_metadata.total_execution_time = 15.5
        mock_execution_metadata.parallel_executions = 4
        
        # Create mock cost breakdown with detailed information
        mock_cost_breakdown = Mock(spec=CostBreakdown)
        mock_cost_breakdown.total_cost = 0.125
        mock_cost_breakdown.execution_time = 15.5
        mock_cost_breakdown.model_costs = {
            "groq-llama3-70b": 0.05,
            "together-mixtral-8x7b": 0.03,
            "openrouter-claude-3-sonnet": 0.045
        }
        mock_cost_breakdown.token_usage = {
            "groq-llama3-70b": 500,
            "together-mixtral-8x7b": 300,
            "openrouter-claude-3-sonnet": 450
        }
        
        # Create mock final response
        mock_final_response = Mock(spec=FinalResponse)
        mock_final_response.content = "Comprehensive synthesized response with detailed metadata"
        mock_final_response.overall_confidence = 0.92
        mock_final_response.success = True
        mock_final_response.error_message = None
        mock_final_response.models_used = [
            "groq-llama3-70b", "together-mixtral-8x7b", "openrouter-claude-3-sonnet"
        ]
        mock_final_response.cost_breakdown = mock_cost_breakdown
        mock_final_response.execution_metadata = mock_execution_metadata
        
        # Mock the AI Council creation
        with patch.object(bridge, '_create_ai_council') as mock_create:
            mock_orchestration = Mock()
            
            def mock_synthesize_with_protection(validated_responses):
                return mock_final_response
            
            mock_orchestration._synthesize_with_protection = mock_synthesize_with_protection
            mock_orchestration.analysis_engine = Mock()
            mock_orchestration.model_registry = Mock()
            mock_orchestration.cost_optimizer = Mock()
            mock_orchestration.execution_agent = Mock()
            
            mock_create.return_value = mock_orchestration
            
            # Initialize and setup hooks
            bridge.ai_council = bridge._create_ai_council()
            bridge._setup_event_hooks("test-request-metadata-999")
            
            # Call synthesis
            result = bridge.ai_council._synthesize_with_protection([])
            
            # Give async tasks time to complete
            await asyncio.sleep(0.1)
            
            # Get final_response message
            calls = ws_manager.broadcast_progress.call_args_list
            final_response_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "final_response"
            ]
            
            assert len(final_response_calls) > 0, "Should have final_response message"
            
            data = final_response_calls[0][0][2]
            
            # Verify orchestration metadata is comprehensive
            assert "executionMetadata" in data, "Must include executionMetadata"
            
            exec_metadata = data["executionMetadata"]
            
            # Verify execution path includes all orchestration stages
            assert "executionPath" in exec_metadata
            execution_path = exec_metadata["executionPath"]
            assert "analysis" in execution_path, "Execution path should include analysis"
            assert "synthesis" in execution_path, "Execution path should include synthesis"
            assert len(execution_path) >= 2, "Execution path should have multiple stages"
            
            # Verify timing information
            assert "totalExecutionTime" in exec_metadata
            assert exec_metadata["totalExecutionTime"] > 0, "Total execution time should be positive"
            
            # Verify parallel execution information
            assert "parallelExecutions" in exec_metadata
            assert exec_metadata["parallelExecutions"] >= 1, "Should have at least one parallel execution"
            
            # Verify cost breakdown includes detailed model information
            assert "costBreakdown" in data
            cost_breakdown = data["costBreakdown"]
            
            assert "modelCosts" in cost_breakdown
            assert len(cost_breakdown["modelCosts"]) == 3, "Should have costs for all 3 models"
            
            assert "tokenUsage" in cost_breakdown
            assert len(cost_breakdown["tokenUsage"]) == 3, "Should have token usage for all 3 models"
            
            # Verify total cost matches sum of model costs
            total_model_costs = sum(cost_breakdown["modelCosts"].values())
            assert abs(total_model_costs - cost_breakdown["totalCost"]) < 0.01, "Total cost should match sum of model costs"
