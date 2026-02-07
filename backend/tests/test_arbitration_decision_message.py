"""Property-based tests for arbitration decision WebSocket messages.

**Property: Arbitration Decision Messages**
**Validates: Requirements 6.6**
Test that arbitration decisions send WebSocket messages with conflicting results
and selected result with reasoning
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
    ExecutionMode, TaskType, Subtask, AgentResponse, 
    SelfAssessment, RiskLevel
)
from ai_council.core.interfaces import ArbitrationResult, Resolution
from datetime import datetime


class TestArbitrationDecisionMessages:
    """Test that arbitration decisions send WebSocket messages with conflict details."""
    
    @pytest.mark.asyncio
    @given(
        num_responses=st.integers(min_value=2, max_value=5),
        num_conflicts=st.integers(min_value=1, max_value=3)
    )
    @settings(max_examples=10, deadline=None)
    async def test_arbitration_sends_decision_with_conflicts(
        self, num_responses, num_conflicts
    ):
        """Property: Arbitration sends decision messages with conflict details.
        
        This test verifies that:
        1. When arbitration resolves conflicts, a WebSocket message is sent
        2. The message type is "arbitration_decision"
        3. The message includes conflicting results
        4. The message includes selected result with reasoning
        5. The message includes confidence scores
        """
        # Create mock WebSocket manager
        ws_manager = Mock(spec=WebSocketManager)
        ws_manager.broadcast_progress = AsyncMock(return_value=True)
        
        # Create bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Create mock responses
        mock_responses = []
        for i in range(num_responses):
            self_assessment = Mock(spec=SelfAssessment)
            self_assessment.confidence_score = 0.6 + (i * 0.1)
            
            response = Mock(spec=AgentResponse)
            response.subtask_id = f"subtask-arb-{i}"
            response.model_used = f"model-{i}"
            response.content = f"Response {i} content"
            response.self_assessment = self_assessment
            response.success = True
            response.error_message = None
            mock_responses.append(response)
        
        # Create mock resolutions
        mock_resolutions = []
        for i in range(num_conflicts):
            resolution = Mock(spec=Resolution)
            resolution.chosen_response_id = f"subtask-arb-{i}_model-{i}"
            resolution.reasoning = f"Selected based on higher confidence score"
            resolution.confidence = 0.8 + (i * 0.05)
            mock_resolutions.append(resolution)
        
        # Create mock arbitration result
        mock_arbitration_result = Mock(spec=ArbitrationResult)
        mock_arbitration_result.validated_responses = mock_responses[:1]  # First response chosen
        mock_arbitration_result.conflicts_resolved = mock_resolutions
        
        # Mock the AI Council creation
        with patch.object(bridge, '_create_ai_council') as mock_create:
            mock_orchestration = Mock()
            
            # Store original method to be replaced by hook
            def mock_arbitrate_with_protection(responses):
                return mock_arbitration_result
            
            mock_orchestration._arbitrate_with_protection = mock_arbitrate_with_protection
            
            # Mock other required components
            mock_orchestration.analysis_engine = Mock()
            mock_orchestration.model_registry = Mock()
            mock_orchestration.cost_optimizer = Mock()
            mock_orchestration.execution_agent = Mock()
            mock_orchestration._execute_parallel_group = Mock(return_value=[])
            
            mock_create.return_value = mock_orchestration
            
            # Initialize AI Council (which will install hooks)
            bridge.ai_council = bridge._create_ai_council()
            bridge._setup_event_hooks("test-request-arb-123")
            
            # Now call arbitration (which should trigger the hook)
            result = bridge.ai_council._arbitrate_with_protection(mock_responses)
            
            # Give async tasks time to complete
            await asyncio.sleep(0.1)
            
            # Verify that broadcast_progress was called
            assert ws_manager.broadcast_progress.called, "WebSocket broadcast should be called"
            
            # Check if any call was for "arbitration_decision"
            calls = ws_manager.broadcast_progress.call_args_list
            arbitration_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "arbitration_decision"
            ]
            
            assert len(arbitration_calls) > 0, "Should have arbitration_decision message"
            
            # Verify the call structure
            first_call = arbitration_calls[0]
            assert first_call[0][0] == "test-request-arb-123", "Request ID should match"
            assert first_call[0][1] == "arbitration_decision", "Event type should be arbitration_decision"
            
            # Verify the data structure
            data = first_call[0][2]
            assert "conflictsDetected" in data, "Should include conflictsDetected"
            assert "decisions" in data, "Should include decisions"
            assert "conflictingResults" in data, "Should include conflictingResults"
            assert "message" in data, "Should include message"
            
            # Verify the values
            assert data["conflictsDetected"] == num_conflicts, "Should match number of conflicts"
            assert len(data["decisions"]) == num_conflicts, "Should have decision for each conflict"
            assert len(data["conflictingResults"]) == num_responses, "Should include all responses"
            
            # Verify decision structure
            for decision in data["decisions"]:
                assert "chosenResponseId" in decision, "Decision should include chosenResponseId"
                assert "reasoning" in decision, "Decision should include reasoning"
                assert "confidence" in decision, "Decision should include confidence"
            
            # Verify conflicting results structure
            for result in data["conflictingResults"]:
                assert "responseId" in result, "Result should include responseId"
                assert "modelId" in result, "Result should include modelId"
                assert "subtaskId" in result, "Result should include subtaskId"
                assert "confidence" in result, "Result should include confidence"
                assert "success" in result, "Result should include success"
    
    @pytest.mark.asyncio
    async def test_arbitration_no_conflicts_sends_message(self):
        """Test that arbitration sends message even when no conflicts detected."""
        # Create mock WebSocket manager
        ws_manager = Mock(spec=WebSocketManager)
        ws_manager.broadcast_progress = AsyncMock(return_value=True)
        
        # Create bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Create mock responses
        mock_responses = []
        for i in range(2):
            self_assessment = Mock(spec=SelfAssessment)
            self_assessment.confidence_score = 0.85
            
            response = Mock(spec=AgentResponse)
            response.subtask_id = f"subtask-no-conflict-{i}"
            response.model_used = f"model-{i}"
            response.content = f"Response {i} content"
            response.self_assessment = self_assessment
            response.success = True
            response.error_message = None
            mock_responses.append(response)
        
        # Create mock arbitration result with NO conflicts
        mock_arbitration_result = Mock(spec=ArbitrationResult)
        mock_arbitration_result.validated_responses = mock_responses
        mock_arbitration_result.conflicts_resolved = []  # No conflicts
        
        # Mock the AI Council creation
        with patch.object(bridge, '_create_ai_council') as mock_create:
            mock_orchestration = Mock()
            
            def mock_arbitrate_with_protection(responses):
                return mock_arbitration_result
            
            mock_orchestration._arbitrate_with_protection = mock_arbitrate_with_protection
            mock_orchestration.analysis_engine = Mock()
            mock_orchestration.model_registry = Mock()
            mock_orchestration.cost_optimizer = Mock()
            mock_orchestration.execution_agent = Mock()
            
            mock_create.return_value = mock_orchestration
            
            # Initialize and setup hooks
            bridge.ai_council = bridge._create_ai_council()
            bridge._setup_event_hooks("test-request-no-conflict-456")
            
            # Call arbitration
            result = bridge.ai_council._arbitrate_with_protection(mock_responses)
            
            # Give async tasks time to complete
            await asyncio.sleep(0.1)
            
            # Verify arbitration_decision was sent
            calls = ws_manager.broadcast_progress.call_args_list
            arbitration_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "arbitration_decision"
            ]
            
            assert len(arbitration_calls) > 0, "Should have arbitration_decision message"
            
            # Verify the data indicates no conflicts
            data = arbitration_calls[0][0][2]
            assert data["conflictsDetected"] == 0, "Should have 0 conflicts"
            assert len(data["decisions"]) == 0, "Should have no decisions"
            assert "No conflicts detected" in data["message"], "Message should indicate no conflicts"
    
    @pytest.mark.asyncio
    async def test_arbitration_decision_includes_reasoning(self):
        """Test that arbitration decision includes detailed reasoning."""
        # Create mock WebSocket manager
        ws_manager = Mock(spec=WebSocketManager)
        ws_manager.broadcast_progress = AsyncMock(return_value=True)
        
        # Create bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Create mock responses with different confidence scores
        mock_responses = []
        for i in range(3):
            self_assessment = Mock(spec=SelfAssessment)
            self_assessment.confidence_score = 0.5 + (i * 0.2)  # 0.5, 0.7, 0.9
            
            response = Mock(spec=AgentResponse)
            response.subtask_id = f"subtask-reasoning-{i}"
            response.model_used = f"model-{i}"
            response.content = f"Response {i} with confidence {0.5 + (i * 0.2)}"
            response.self_assessment = self_assessment
            response.success = True
            response.error_message = None
            mock_responses.append(response)
        
        # Create mock resolution with detailed reasoning
        mock_resolution = Mock(spec=Resolution)
        mock_resolution.chosen_response_id = "subtask-reasoning-2_model-2"
        mock_resolution.reasoning = "Selected response with highest confidence score (0.9) and best quality indicators"
        mock_resolution.confidence = 0.92
        
        # Create mock arbitration result
        mock_arbitration_result = Mock(spec=ArbitrationResult)
        mock_arbitration_result.validated_responses = [mock_responses[2]]  # Highest confidence
        mock_arbitration_result.conflicts_resolved = [mock_resolution]
        
        # Mock the AI Council creation
        with patch.object(bridge, '_create_ai_council') as mock_create:
            mock_orchestration = Mock()
            
            def mock_arbitrate_with_protection(responses):
                return mock_arbitration_result
            
            mock_orchestration._arbitrate_with_protection = mock_arbitrate_with_protection
            mock_orchestration.analysis_engine = Mock()
            mock_orchestration.model_registry = Mock()
            mock_orchestration.cost_optimizer = Mock()
            mock_orchestration.execution_agent = Mock()
            
            mock_create.return_value = mock_orchestration
            
            # Initialize and setup hooks
            bridge.ai_council = bridge._create_ai_council()
            bridge._setup_event_hooks("test-request-reasoning-789")
            
            # Call arbitration
            result = bridge.ai_council._arbitrate_with_protection(mock_responses)
            
            # Give async tasks time to complete
            await asyncio.sleep(0.1)
            
            # Verify arbitration_decision was sent
            calls = ws_manager.broadcast_progress.call_args_list
            arbitration_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "arbitration_decision"
            ]
            
            assert len(arbitration_calls) > 0, "Should have arbitration_decision message"
            
            # Verify the decision includes reasoning
            data = arbitration_calls[0][0][2]
            assert len(data["decisions"]) == 1, "Should have one decision"
            
            decision = data["decisions"][0]
            assert decision["chosenResponseId"] == "subtask-reasoning-2_model-2"
            assert "highest confidence" in decision["reasoning"].lower()
            assert decision["confidence"] == 0.92
    
    @pytest.mark.asyncio
    async def test_arbitration_includes_all_conflicting_responses(self):
        """Test that arbitration message includes all conflicting responses."""
        # Create mock WebSocket manager
        ws_manager = Mock(spec=WebSocketManager)
        ws_manager.broadcast_progress = AsyncMock(return_value=True)
        
        # Create bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Create mock responses with varying attributes
        mock_responses = []
        models = ["groq-llama3-70b", "together-mixtral-8x7b", "openrouter-claude-3"]
        confidences = [0.75, 0.82, 0.68]
        
        for i in range(3):
            self_assessment = Mock(spec=SelfAssessment)
            self_assessment.confidence_score = confidences[i]
            
            response = Mock(spec=AgentResponse)
            response.subtask_id = f"subtask-all-{i}"
            response.model_used = models[i]
            response.content = f"Response from {models[i]}"
            response.self_assessment = self_assessment
            response.success = True
            response.error_message = None
            mock_responses.append(response)
        
        # Create mock resolution
        mock_resolution = Mock(spec=Resolution)
        mock_resolution.chosen_response_id = "subtask-all-1_together-mixtral-8x7b"
        mock_resolution.reasoning = "Selected based on highest confidence"
        mock_resolution.confidence = 0.85
        
        # Create mock arbitration result
        mock_arbitration_result = Mock(spec=ArbitrationResult)
        mock_arbitration_result.validated_responses = [mock_responses[1]]
        mock_arbitration_result.conflicts_resolved = [mock_resolution]
        
        # Mock the AI Council creation
        with patch.object(bridge, '_create_ai_council') as mock_create:
            mock_orchestration = Mock()
            
            def mock_arbitrate_with_protection(responses):
                return mock_arbitration_result
            
            mock_orchestration._arbitrate_with_protection = mock_arbitrate_with_protection
            mock_orchestration.analysis_engine = Mock()
            mock_orchestration.model_registry = Mock()
            mock_orchestration.cost_optimizer = Mock()
            mock_orchestration.execution_agent = Mock()
            
            mock_create.return_value = mock_orchestration
            
            # Initialize and setup hooks
            bridge.ai_council = bridge._create_ai_council()
            bridge._setup_event_hooks("test-request-all-999")
            
            # Call arbitration
            result = bridge.ai_council._arbitrate_with_protection(mock_responses)
            
            # Give async tasks time to complete
            await asyncio.sleep(0.1)
            
            # Verify arbitration_decision was sent
            calls = ws_manager.broadcast_progress.call_args_list
            arbitration_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "arbitration_decision"
            ]
            
            assert len(arbitration_calls) > 0, "Should have arbitration_decision message"
            
            # Verify all conflicting responses are included
            data = arbitration_calls[0][0][2]
            assert len(data["conflictingResults"]) == 3, "Should include all 3 responses"
            
            # Verify each response has correct structure and values
            for i, result in enumerate(data["conflictingResults"]):
                assert result["modelId"] == models[i], f"Model {i} should match"
                assert result["confidence"] == confidences[i], f"Confidence {i} should match"
                assert result["success"] is True, f"Success {i} should be True"
                assert f"subtask-all-{i}" in result["responseId"], f"Response ID {i} should contain subtask ID"
    
    @pytest.mark.asyncio
    @given(
        confidence_values=st.lists(
            st.floats(min_value=0.0, max_value=1.0),
            min_size=2,
            max_size=4
        )
    )
    @settings(max_examples=10, deadline=None)
    async def test_arbitration_preserves_confidence_scores(self, confidence_values):
        """Property: Arbitration message preserves confidence scores from responses.
        
        This test verifies that:
        1. Confidence scores in conflicting results match original responses
        2. Confidence score in decision matches resolution confidence
        """
        # Create mock WebSocket manager
        ws_manager = Mock(spec=WebSocketManager)
        ws_manager.broadcast_progress = AsyncMock(return_value=True)
        
        # Create bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Create mock responses with given confidence values
        mock_responses = []
        for i, confidence in enumerate(confidence_values):
            self_assessment = Mock(spec=SelfAssessment)
            self_assessment.confidence_score = confidence
            
            response = Mock(spec=AgentResponse)
            response.subtask_id = f"subtask-conf-{i}"
            response.model_used = f"model-{i}"
            response.content = f"Response {i}"
            response.self_assessment = self_assessment
            response.success = True
            response.error_message = None
            mock_responses.append(response)
        
        # Create mock resolution with highest confidence
        max_confidence = max(confidence_values)
        mock_resolution = Mock(spec=Resolution)
        mock_resolution.chosen_response_id = f"subtask-conf-0_model-0"
        mock_resolution.reasoning = "Selected based on confidence"
        mock_resolution.confidence = max_confidence
        
        # Create mock arbitration result
        mock_arbitration_result = Mock(spec=ArbitrationResult)
        mock_arbitration_result.validated_responses = [mock_responses[0]]
        mock_arbitration_result.conflicts_resolved = [mock_resolution]
        
        # Mock the AI Council creation
        with patch.object(bridge, '_create_ai_council') as mock_create:
            mock_orchestration = Mock()
            
            def mock_arbitrate_with_protection(responses):
                return mock_arbitration_result
            
            mock_orchestration._arbitrate_with_protection = mock_arbitrate_with_protection
            mock_orchestration.analysis_engine = Mock()
            mock_orchestration.model_registry = Mock()
            mock_orchestration.cost_optimizer = Mock()
            mock_orchestration.execution_agent = Mock()
            
            mock_create.return_value = mock_orchestration
            
            # Initialize and setup hooks
            bridge.ai_council = bridge._create_ai_council()
            bridge._setup_event_hooks("test-request-conf-prop")
            
            # Call arbitration
            result = bridge.ai_council._arbitrate_with_protection(mock_responses)
            
            # Give async tasks time to complete
            await asyncio.sleep(0.1)
            
            # Verify arbitration_decision was sent
            calls = ws_manager.broadcast_progress.call_args_list
            arbitration_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "arbitration_decision"
            ]
            
            assert len(arbitration_calls) > 0, "Should have arbitration_decision message"
            
            # Verify confidence scores are preserved
            data = arbitration_calls[0][0][2]
            
            # Check conflicting results confidence scores
            for i, result in enumerate(data["conflictingResults"]):
                expected_confidence = confidence_values[i]
                actual_confidence = result["confidence"]
                assert abs(actual_confidence - expected_confidence) < 0.01, \
                    f"Confidence {i} should match (expected {expected_confidence}, got {actual_confidence})"
            
            # Check decision confidence
            if data["decisions"]:
                decision_confidence = data["decisions"][0]["confidence"]
                assert abs(decision_confidence - max_confidence) < 0.01, \
                    f"Decision confidence should match max confidence"
