"""Property-based tests for synthesis progress WebSocket messages.

**Property: Synthesis Progress Messages**
**Validates: Requirements 6.7, 6.8**
Test that synthesis layer sends WebSocket messages with synthesis progress
and final response with all metadata
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


class TestSynthesisProgressMessages:
    """Test that synthesis layer sends WebSocket messages with progress and final response."""
    
    @pytest.mark.asyncio
    @given(
        num_responses=st.integers(min_value=1, max_value=5),
        overall_confidence=st.floats(min_value=0.0, max_value=1.0),
        total_cost=st.floats(min_value=0.0001, max_value=1.0),
        execution_time=st.floats(min_value=0.1, max_value=60.0)
    )
    @settings(max_examples=10, deadline=None)
    async def test_synthesis_sends_progress_and_final_response(
        self, num_responses, overall_confidence, total_cost, execution_time
    ):
        """Property: Synthesis sends progress messages and final response with metadata.
        
        This test verifies that:
        1. When synthesis starts, a WebSocket message with type "synthesis_progress" is sent
        2. When synthesis completes, messages with final response data are sent
        3. The final response includes all required metadata
        4. Both "synthesis_progress" and "final_response" messages are sent
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
            self_assessment.confidence_score = 0.7 + (i * 0.05)
            self_assessment.estimated_cost = total_cost / num_responses
            self_assessment.execution_time = execution_time / num_responses
            self_assessment.token_usage = 100 + (i * 50)
            self_assessment.risk_level = RiskLevel.LOW
            
            response = Mock(spec=AgentResponse)
            response.subtask_id = f"subtask-synth-{i}"
            response.model_used = f"model-{i}"
            response.content = f"Response {i} content for synthesis"
            response.self_assessment = self_assessment
            response.success = True
            response.error_message = None
            mock_responses.append(response)
        
        # Create mock final response
        mock_cost_breakdown = Mock(spec=CostBreakdown)
        mock_cost_breakdown.total_cost = total_cost
        mock_cost_breakdown.execution_time = execution_time
        mock_cost_breakdown.model_costs = {f"model-{i}": total_cost / num_responses for i in range(num_responses)}
        mock_cost_breakdown.token_usage = {f"model-{i}": 100 + (i * 50) for i in range(num_responses)}
        
        mock_final_response = Mock(spec=FinalResponse)
        mock_final_response.content = "Synthesized final response combining all agent outputs"
        mock_final_response.overall_confidence = overall_confidence
        mock_final_response.success = True
        mock_final_response.error_message = None
        mock_final_response.models_used = [f"model-{i}" for i in range(num_responses)]
        mock_final_response.cost_breakdown = mock_cost_breakdown
        
        # Mock the AI Council creation
        with patch.object(bridge, '_create_ai_council') as mock_create:
            mock_orchestration = Mock()
            
            # Store original method to be replaced by hook
            def mock_synthesize_with_protection(validated_responses):
                return mock_final_response
            
            mock_orchestration._synthesize_with_protection = mock_synthesize_with_protection
            
            # Mock other required components
            mock_orchestration.analysis_engine = Mock()
            mock_orchestration.model_registry = Mock()
            mock_orchestration.cost_optimizer = Mock()
            mock_orchestration.execution_agent = Mock()
            mock_orchestration._execute_parallel_group = Mock(return_value=[])
            mock_orchestration._arbitrate_with_protection = Mock()
            
            mock_create.return_value = mock_orchestration
            
            # Initialize AI Council (which will install hooks)
            bridge.ai_council = bridge._create_ai_council()
            bridge._setup_event_hooks("test-request-synth-123")
            
            # Now call synthesis (which should trigger the hook)
            result = bridge.ai_council._synthesize_with_protection(mock_responses)
            
            # Give async tasks time to complete
            await asyncio.sleep(0.1)
            
            # Verify that broadcast_progress was called
            assert ws_manager.broadcast_progress.called, "WebSocket broadcast should be called"
            
            # Check for synthesis_progress messages
            calls = ws_manager.broadcast_progress.call_args_list
            synthesis_progress_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "synthesis_progress"
            ]
            
            assert len(synthesis_progress_calls) >= 2, "Should have at least 2 synthesis_progress messages (started and complete)"
            
            # Verify the started message
            started_call = synthesis_progress_calls[0]
            assert started_call[0][0] == "test-request-synth-123", "Request ID should match"
            assert started_call[0][1] == "synthesis_progress", "Event type should be synthesis_progress"
            
            started_data = started_call[0][2]
            assert started_data["stage"] == "started", "First message should be 'started' stage"
            assert "totalResponses" in started_data, "Should include totalResponses"
            assert started_data["totalResponses"] == num_responses, "Should match number of responses"
            
            # Verify the complete message
            complete_call = synthesis_progress_calls[-1]
            complete_data = complete_call[0][2]
            
            assert complete_data["stage"] == "complete", "Last message should be 'complete' stage"
            assert "content" in complete_data, "Should include content"
            assert "overallConfidence" in complete_data, "Should include overallConfidence"
            assert "success" in complete_data, "Should include success"
            assert "modelsUsed" in complete_data, "Should include modelsUsed"
            assert "costBreakdown" in complete_data, "Should include costBreakdown"
            
            # Verify the values
            assert complete_data["success"] is True, "Success should be True"
            assert abs(complete_data["overallConfidence"] - overall_confidence) < 0.01, "Confidence should match"
            assert len(complete_data["modelsUsed"]) == num_responses, "Should include all models"
            
            # Verify cost breakdown structure
            cost_breakdown = complete_data["costBreakdown"]
            assert "totalCost" in cost_breakdown, "Cost breakdown should include totalCost"
            assert "executionTime" in cost_breakdown, "Cost breakdown should include executionTime"
            assert abs(cost_breakdown["totalCost"] - total_cost) < 0.01, "Total cost should match"
            assert abs(cost_breakdown["executionTime"] - execution_time) < 0.1, "Execution time should match"
            
            # Check for final_response message (backwards compatibility)
            final_response_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "final_response"
            ]
            
            assert len(final_response_calls) > 0, "Should have final_response message for backwards compatibility"
    
    @pytest.mark.asyncio
    async def test_synthesis_includes_all_metadata(self):
        """Test that synthesis complete message includes all required metadata."""
        # Create mock WebSocket manager
        ws_manager = Mock(spec=WebSocketManager)
        ws_manager.broadcast_progress = AsyncMock(return_value=True)
        
        # Create bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Create mock validated responses
        mock_responses = []
        for i in range(3):
            self_assessment = Mock(spec=SelfAssessment)
            self_assessment.confidence_score = 0.8
            self_assessment.estimated_cost = 0.01
            self_assessment.execution_time = 2.5
            self_assessment.token_usage = 150
            self_assessment.risk_level = RiskLevel.LOW
            
            response = Mock(spec=AgentResponse)
            response.subtask_id = f"subtask-meta-{i}"
            response.model_used = f"groq-llama3-70b"
            response.content = f"Response {i}"
            response.self_assessment = self_assessment
            response.success = True
            response.error_message = None
            mock_responses.append(response)
        
        # Create mock final response with execution metadata
        mock_cost_breakdown = Mock(spec=CostBreakdown)
        mock_cost_breakdown.total_cost = 0.03
        mock_cost_breakdown.execution_time = 7.5
        mock_cost_breakdown.model_costs = {"groq-llama3-70b": 0.03}
        mock_cost_breakdown.token_usage = {"groq-llama3-70b": 450}
        
        mock_execution_metadata = Mock()
        mock_execution_metadata.execution_path = ["analysis", "routing", "execution", "arbitration", "synthesis"]
        mock_execution_metadata.total_execution_time = 8.2
        mock_execution_metadata.parallel_executions = 3
        
        mock_final_response = Mock(spec=FinalResponse)
        mock_final_response.content = "Complete synthesized response"
        mock_final_response.overall_confidence = 0.85
        mock_final_response.success = True
        mock_final_response.error_message = None
        mock_final_response.models_used = ["groq-llama3-70b"]
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
            bridge._setup_event_hooks("test-request-meta-456")
            
            # Call synthesis
            result = bridge.ai_council._synthesize_with_protection(mock_responses)
            
            # Give async tasks time to complete
            await asyncio.sleep(0.1)
            
            # Verify synthesis_progress complete message
            calls = ws_manager.broadcast_progress.call_args_list
            synthesis_progress_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "synthesis_progress"
            ]
            
            # Get the complete message
            complete_call = [c for c in synthesis_progress_calls if c[0][2].get("stage") == "complete"][0]
            data = complete_call[0][2]
            
            # Verify all metadata fields are present
            assert "content" in data
            assert "overallConfidence" in data
            assert "success" in data
            assert "modelsUsed" in data
            assert "costBreakdown" in data
            assert "executionMetadata" in data
            
            # Verify execution metadata structure
            exec_meta = data["executionMetadata"]
            assert "executionPath" in exec_meta
            assert "totalExecutionTime" in exec_meta
            assert "parallelExecutions" in exec_meta
            
            # Verify execution metadata values
            assert exec_meta["executionPath"] == ["analysis", "routing", "execution", "arbitration", "synthesis"]
            assert abs(exec_meta["totalExecutionTime"] - 8.2) < 0.1
            assert exec_meta["parallelExecutions"] == 3
            
            # Verify cost breakdown details
            cost_breakdown = data["costBreakdown"]
            assert "modelCosts" in cost_breakdown
            assert "tokenUsage" in cost_breakdown
            assert cost_breakdown["modelCosts"]["groq-llama3-70b"] == 0.03
            assert cost_breakdown["tokenUsage"]["groq-llama3-70b"] == 450
    
    @pytest.mark.asyncio
    async def test_synthesis_handles_failure(self):
        """Test that synthesis sends appropriate message when synthesis fails."""
        # Create mock WebSocket manager
        ws_manager = Mock(spec=WebSocketManager)
        ws_manager.broadcast_progress = AsyncMock(return_value=True)
        
        # Create bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Create mock validated responses
        mock_responses = []
        for i in range(2):
            response = Mock(spec=AgentResponse)
            response.subtask_id = f"subtask-fail-{i}"
            response.model_used = f"model-{i}"
            response.content = f"Response {i}"
            response.self_assessment = None
            response.success = True
            response.error_message = None
            mock_responses.append(response)
        
        # Create mock final response indicating failure
        mock_final_response = Mock(spec=FinalResponse)
        mock_final_response.content = ""
        mock_final_response.overall_confidence = 0.0
        mock_final_response.success = False
        mock_final_response.error_message = "Synthesis failed: insufficient data"
        mock_final_response.models_used = []
        mock_final_response.cost_breakdown = None
        
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
            bridge._setup_event_hooks("test-request-fail-789")
            
            # Call synthesis
            result = bridge.ai_council._synthesize_with_protection(mock_responses)
            
            # Give async tasks time to complete
            await asyncio.sleep(0.1)
            
            # Verify synthesis_progress message was sent
            calls = ws_manager.broadcast_progress.call_args_list
            synthesis_progress_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "synthesis_progress"
            ]
            
            assert len(synthesis_progress_calls) >= 2, "Should have synthesis_progress messages"
            
            # Get the complete message
            complete_call = [c for c in synthesis_progress_calls if c[0][2].get("stage") == "complete"][0]
            data = complete_call[0][2]
            
            # Verify failure is indicated
            assert data["success"] is False, "Success should be False"
            assert "errorMessage" in data, "Should include errorMessage"
            assert "insufficient data" in data["errorMessage"], "Error message should be included"
            assert data["overallConfidence"] == 0.0, "Confidence should be 0.0 on failure"
    
    @pytest.mark.asyncio
    @given(
        num_models=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=10, deadline=None)
    async def test_synthesis_includes_all_models_used(self, num_models):
        """Property: Synthesis message includes all models that were used.
        
        This test verifies that:
        1. The modelsUsed field includes all unique models
        2. The number of models matches the expected count
        """
        # Create mock WebSocket manager
        ws_manager = Mock(spec=WebSocketManager)
        ws_manager.broadcast_progress = AsyncMock(return_value=True)
        
        # Create bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Create mock validated responses with different models
        model_names = [f"model-{i}" for i in range(num_models)]
        mock_responses = []
        
        for i, model_name in enumerate(model_names):
            self_assessment = Mock(spec=SelfAssessment)
            self_assessment.confidence_score = 0.8
            self_assessment.estimated_cost = 0.01
            self_assessment.execution_time = 2.0
            self_assessment.token_usage = 100
            self_assessment.risk_level = RiskLevel.LOW
            
            response = Mock(spec=AgentResponse)
            response.subtask_id = f"subtask-models-{i}"
            response.model_used = model_name
            response.content = f"Response from {model_name}"
            response.self_assessment = self_assessment
            response.success = True
            response.error_message = None
            mock_responses.append(response)
        
        # Create mock final response
        mock_cost_breakdown = Mock(spec=CostBreakdown)
        mock_cost_breakdown.total_cost = 0.01 * num_models
        mock_cost_breakdown.execution_time = 2.0 * num_models
        mock_cost_breakdown.model_costs = {name: 0.01 for name in model_names}
        mock_cost_breakdown.token_usage = {name: 100 for name in model_names}
        
        mock_final_response = Mock(spec=FinalResponse)
        mock_final_response.content = "Synthesized response"
        mock_final_response.overall_confidence = 0.85
        mock_final_response.success = True
        mock_final_response.error_message = None
        mock_final_response.models_used = model_names
        mock_final_response.cost_breakdown = mock_cost_breakdown
        
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
            bridge._setup_event_hooks("test-request-models-prop")
            
            # Call synthesis
            result = bridge.ai_council._synthesize_with_protection(mock_responses)
            
            # Give async tasks time to complete
            await asyncio.sleep(0.1)
            
            # Verify synthesis_progress complete message
            calls = ws_manager.broadcast_progress.call_args_list
            synthesis_progress_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "synthesis_progress"
            ]
            
            # Get the complete message
            complete_call = [c for c in synthesis_progress_calls if c[0][2].get("stage") == "complete"][0]
            data = complete_call[0][2]
            
            # Verify all models are included
            assert "modelsUsed" in data
            assert len(data["modelsUsed"]) == num_models, f"Should include all {num_models} models"
            
            # Verify all model names are present
            for model_name in model_names:
                assert model_name in data["modelsUsed"], f"Should include {model_name}"
    
    @pytest.mark.asyncio
    async def test_synthesis_sends_both_message_types(self):
        """Test that synthesis sends both synthesis_progress and final_response messages."""
        # Create mock WebSocket manager
        ws_manager = Mock(spec=WebSocketManager)
        ws_manager.broadcast_progress = AsyncMock(return_value=True)
        
        # Create bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Create mock validated responses
        mock_responses = []
        self_assessment = Mock(spec=SelfAssessment)
        self_assessment.confidence_score = 0.9
        self_assessment.estimated_cost = 0.02
        self_assessment.execution_time = 3.0
        self_assessment.token_usage = 200
        self_assessment.risk_level = RiskLevel.LOW
        
        response = Mock(spec=AgentResponse)
        response.subtask_id = "subtask-both-1"
        response.model_used = "test-model"
        response.content = "Test response"
        response.self_assessment = self_assessment
        response.success = True
        response.error_message = None
        mock_responses.append(response)
        
        # Create mock final response
        mock_cost_breakdown = Mock(spec=CostBreakdown)
        mock_cost_breakdown.total_cost = 0.02
        mock_cost_breakdown.execution_time = 3.0
        
        mock_final_response = Mock(spec=FinalResponse)
        mock_final_response.content = "Final synthesized response"
        mock_final_response.overall_confidence = 0.9
        mock_final_response.success = True
        mock_final_response.error_message = None
        mock_final_response.models_used = ["test-model"]
        mock_final_response.cost_breakdown = mock_cost_breakdown
        
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
            bridge._setup_event_hooks("test-request-both-999")
            
            # Call synthesis
            result = bridge.ai_council._synthesize_with_protection(mock_responses)
            
            # Give async tasks time to complete
            await asyncio.sleep(0.1)
            
            # Verify both message types were sent
            calls = ws_manager.broadcast_progress.call_args_list
            
            synthesis_progress_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "synthesis_progress"
            ]
            
            final_response_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "final_response"
            ]
            
            assert len(synthesis_progress_calls) >= 2, "Should have synthesis_progress messages"
            assert len(final_response_calls) >= 1, "Should have final_response message"
            
            # Verify both messages have the same complete data
            synthesis_complete = [c for c in synthesis_progress_calls if c[0][2].get("stage") == "complete"][0]
            final_response = final_response_calls[0]
            
            synthesis_data = synthesis_complete[0][2]
            final_data = final_response[0][2]
            
            # Both should have the same core fields
            assert synthesis_data["content"] == final_data["content"]
            assert synthesis_data["overallConfidence"] == final_data["overallConfidence"]
            assert synthesis_data["success"] == final_data["success"]
            assert synthesis_data["modelsUsed"] == final_data["modelsUsed"]
