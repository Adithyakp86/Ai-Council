"""Property-based tests for execution progress WebSocket messages.

**Property 26: Execution Progress Messages**
**Validates: Requirements 6.4, 6.5**
Test that completed subtasks send progress updates
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
from datetime import datetime


class TestExecutionProgressMessages:
    """Test that completed subtasks send progress updates via WebSocket."""
    
    @pytest.mark.asyncio
    @given(
        confidence=st.floats(min_value=0.0, max_value=1.0),
        cost=st.floats(min_value=0.0001, max_value=0.1),
        execution_time=st.floats(min_value=0.1, max_value=10.0),
        success=st.booleans()
    )
    @settings(max_examples=10, deadline=None)
    async def test_execution_sends_progress_with_metrics(
        self, confidence, cost, execution_time, success
    ):
        """Property: Execution sends progress updates with confidence, cost, and time.
        
        This test verifies that:
        1. When a subtask completes execution, a WebSocket message is sent
        2. The message type is "execution_progress"
        3. The message includes confidence, cost, and execution_time
        4. The message includes success status
        """
        # Create mock WebSocket manager
        ws_manager = Mock(spec=WebSocketManager)
        ws_manager.broadcast_progress = AsyncMock(return_value=True)
        
        # Create bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Create mock subtask
        mock_subtask = Mock(spec=Subtask)
        mock_subtask.id = "test-subtask-exec-1"
        mock_subtask.content = "Test subtask for execution"
        mock_subtask.task_type = TaskType.REASONING
        
        # Create mock model
        mock_model = Mock()
        mock_model.get_model_id = Mock(return_value="test-model-exec")
        
        # Create mock self-assessment
        mock_self_assessment = Mock(spec=SelfAssessment)
        mock_self_assessment.confidence_score = confidence
        mock_self_assessment.estimated_cost = cost
        mock_self_assessment.execution_time = execution_time
        
        # Create mock agent response
        mock_response = Mock(spec=AgentResponse)
        mock_response.subtask_id = "test-subtask-exec-1"
        mock_response.model_used = "test-model-exec"
        mock_response.content = "Test response content"
        mock_response.self_assessment = mock_self_assessment
        mock_response.success = success
        mock_response.error_message = None if success else "Test error"
        
        # Mock the AI Council creation
        with patch.object(bridge, '_create_ai_council') as mock_create:
            mock_orchestration = Mock()
            
            # Create mock execution agent
            mock_execution_agent = Mock()
            
            # Store original execute to be replaced by hook
            def mock_execute(subtask, model):
                return mock_response
            
            mock_execution_agent.execute = mock_execute
            
            # Attach execution agent to orchestration
            mock_orchestration.execution_agent = mock_execution_agent
            
            # Mock other required components
            mock_orchestration.analysis_engine = Mock()
            mock_orchestration.model_registry = Mock()
            mock_orchestration.cost_optimizer = Mock()
            mock_orchestration._execute_parallel_group = Mock(return_value=[])
            mock_orchestration.process_request = Mock(return_value=Mock(
                content="Test", overall_confidence=0.8, success=True
            ))
            
            mock_create.return_value = mock_orchestration
            
            # Initialize AI Council (which will install hooks)
            bridge.ai_council = bridge._create_ai_council()
            bridge._setup_event_hooks("test-request-exec-123")
            
            # Now execute the subtask (which should trigger the hook)
            result = bridge.ai_council.execution_agent.execute(mock_subtask, mock_model)
            
            # Give async tasks time to complete
            await asyncio.sleep(0.1)
            
            # Verify that broadcast_progress was called
            assert ws_manager.broadcast_progress.called, "WebSocket broadcast should be called"
            
            # Check if any call was for "execution_progress"
            calls = ws_manager.broadcast_progress.call_args_list
            execution_progress_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "execution_progress"
            ]
            
            assert len(execution_progress_calls) > 0, "Should have execution_progress message"
            
            # Verify the call structure
            first_call = execution_progress_calls[0]
            assert first_call[0][0] == "test-request-exec-123", "Request ID should match"
            assert first_call[0][1] == "execution_progress", "Event type should be execution_progress"
            
            # Verify the data structure
            data = first_call[0][2]
            assert "subtaskId" in data, "Should include subtaskId"
            assert "modelId" in data, "Should include modelId"
            assert "confidence" in data, "Should include confidence"
            assert "cost" in data, "Should include cost"
            assert "executionTime" in data, "Should include executionTime"
            assert "success" in data, "Should include success status"
            
            # Verify the values match
            assert data["subtaskId"] == "test-subtask-exec-1"
            assert data["modelId"] == "test-model-exec"
            assert abs(data["confidence"] - confidence) < 0.01, "Confidence should match"
            assert abs(data["cost"] - cost) < 0.0001, "Cost should match"
            assert abs(data["executionTime"] - execution_time) < 0.1, "Execution time should match"
            assert data["success"] == success, "Success status should match"
    
    @pytest.mark.asyncio
    async def test_execution_progress_includes_error_on_failure(self):
        """Test that execution_progress includes error message on failure."""
        # Create mock WebSocket manager
        ws_manager = Mock(spec=WebSocketManager)
        ws_manager.broadcast_progress = AsyncMock(return_value=True)
        
        # Create bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Create mock subtask
        mock_subtask = Mock(spec=Subtask)
        mock_subtask.id = "test-subtask-fail"
        mock_subtask.content = "Failing subtask"
        mock_subtask.task_type = TaskType.CODE_GENERATION
        
        # Create mock model
        mock_model = Mock()
        mock_model.get_model_id = Mock(return_value="test-model-fail")
        
        # Create mock self-assessment
        mock_self_assessment = Mock(spec=SelfAssessment)
        mock_self_assessment.confidence_score = 0.1
        mock_self_assessment.estimated_cost = 0.005
        mock_self_assessment.execution_time = 2.5
        
        # Create mock agent response (failed)
        mock_response = Mock(spec=AgentResponse)
        mock_response.subtask_id = "test-subtask-fail"
        mock_response.model_used = "test-model-fail"
        mock_response.content = ""
        mock_response.self_assessment = mock_self_assessment
        mock_response.success = False
        mock_response.error_message = "Model execution failed: timeout"
        
        # Mock the AI Council creation
        with patch.object(bridge, '_create_ai_council') as mock_create:
            mock_orchestration = Mock()
            
            # Create mock execution agent
            mock_execution_agent = Mock()
            
            def mock_execute(subtask, model):
                return mock_response
            
            mock_execution_agent.execute = mock_execute
            
            # Attach execution agent
            mock_orchestration.execution_agent = mock_execution_agent
            mock_orchestration.analysis_engine = Mock()
            mock_orchestration.model_registry = Mock()
            mock_orchestration.cost_optimizer = Mock()
            
            mock_create.return_value = mock_orchestration
            
            # Initialize and setup hooks
            bridge.ai_council = bridge._create_ai_council()
            bridge._setup_event_hooks("test-request-fail-456")
            
            # Execute the subtask
            result = bridge.ai_council.execution_agent.execute(mock_subtask, mock_model)
            
            # Give async tasks time to complete
            await asyncio.sleep(0.1)
            
            # Verify execution_progress was sent
            calls = ws_manager.broadcast_progress.call_args_list
            execution_progress_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "execution_progress"
            ]
            
            assert len(execution_progress_calls) > 0, "Should have execution_progress message"
            
            # Verify the data includes error message
            data = execution_progress_calls[0][0][2]
            assert data["success"] is False, "Success should be False"
            assert "errorMessage" in data, "Should include errorMessage on failure"
            assert data["errorMessage"] == "Model execution failed: timeout"
    
    @pytest.mark.asyncio
    @given(
        num_subtasks=st.integers(min_value=2, max_value=5)
    )
    @settings(max_examples=5, deadline=None)
    async def test_execution_progress_sent_for_each_subtask(self, num_subtasks):
        """Property: Execution progress is sent for each completed subtask.
        
        This test verifies that:
        1. Each subtask that completes sends an execution_progress message
        2. The number of messages matches the number of subtasks
        3. Each message has a unique subtaskId
        """
        # Create mock WebSocket manager
        ws_manager = Mock(spec=WebSocketManager)
        ws_manager.broadcast_progress = AsyncMock(return_value=True)
        
        # Create bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Create mock subtasks and responses
        mock_subtasks = []
        mock_responses = []
        
        for i in range(num_subtasks):
            subtask = Mock(spec=Subtask)
            subtask.id = f"subtask-multi-{i}"
            subtask.content = f"Subtask {i} content"
            subtask.task_type = TaskType.REASONING
            mock_subtasks.append(subtask)
            
            # Create response for this subtask
            self_assessment = Mock(spec=SelfAssessment)
            self_assessment.confidence_score = 0.7 + (i * 0.05)
            self_assessment.estimated_cost = 0.001 * (i + 1)
            self_assessment.execution_time = 1.0 + (i * 0.5)
            
            response = Mock(spec=AgentResponse)
            response.subtask_id = f"subtask-multi-{i}"
            response.model_used = f"model-{i}"
            response.content = f"Response {i}"
            response.self_assessment = self_assessment
            response.success = True
            response.error_message = None
            mock_responses.append(response)
        
        # Create mock model
        mock_model = Mock()
        mock_model.get_model_id = Mock(return_value="test-model-multi")
        
        # Mock the AI Council creation
        with patch.object(bridge, '_create_ai_council') as mock_create:
            mock_orchestration = Mock()
            
            # Create mock execution agent
            mock_execution_agent = Mock()
            
            # Track which subtask is being executed
            execution_count = {"count": 0}
            
            def mock_execute(subtask, model):
                idx = execution_count["count"]
                execution_count["count"] += 1
                return mock_responses[idx] if idx < len(mock_responses) else mock_responses[0]
            
            mock_execution_agent.execute = mock_execute
            
            # Attach execution agent
            mock_orchestration.execution_agent = mock_execution_agent
            mock_orchestration.analysis_engine = Mock()
            mock_orchestration.model_registry = Mock()
            mock_orchestration.cost_optimizer = Mock()
            
            mock_create.return_value = mock_orchestration
            
            # Initialize and setup hooks
            bridge.ai_council = bridge._create_ai_council()
            bridge._setup_event_hooks("test-request-multi-789")
            
            # Execute all subtasks
            for subtask in mock_subtasks:
                bridge.ai_council.execution_agent.execute(subtask, mock_model)
            
            # Give async tasks time to complete
            await asyncio.sleep(0.2)
            
            # Verify execution_progress was sent for each subtask
            calls = ws_manager.broadcast_progress.call_args_list
            execution_progress_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "execution_progress"
            ]
            
            assert len(execution_progress_calls) == num_subtasks, \
                f"Should have {num_subtasks} execution_progress messages"
            
            # Verify each message has a unique subtaskId
            subtask_ids = [call[0][2]["subtaskId"] for call in execution_progress_calls]
            assert len(set(subtask_ids)) == num_subtasks, "Each subtask should have unique ID"
            
            # Verify all expected subtask IDs are present
            expected_ids = {f"subtask-multi-{i}" for i in range(num_subtasks)}
            actual_ids = set(subtask_ids)
            assert actual_ids == expected_ids, "All subtask IDs should be present"
    
    @pytest.mark.asyncio
    async def test_execution_progress_message_structure(self):
        """Test that execution_progress message has correct structure."""
        # Create mock WebSocket manager
        ws_manager = Mock(spec=WebSocketManager)
        ws_manager.broadcast_progress = AsyncMock(return_value=True)
        
        # Create bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Create specific mock subtask
        mock_subtask = Mock(spec=Subtask)
        mock_subtask.id = "subtask-structure-test"
        mock_subtask.content = "Analyze the performance metrics of the system"
        mock_subtask.task_type = TaskType.RESEARCH
        
        # Create mock model
        mock_model = Mock()
        mock_model.get_model_id = Mock(return_value="groq-llama3-70b")
        
        # Create detailed self-assessment
        mock_self_assessment = Mock(spec=SelfAssessment)
        mock_self_assessment.confidence_score = 0.87
        mock_self_assessment.estimated_cost = 0.0023
        mock_self_assessment.execution_time = 3.45
        
        # Create detailed agent response
        mock_response = Mock(spec=AgentResponse)
        mock_response.subtask_id = "subtask-structure-test"
        mock_response.model_used = "groq-llama3-70b"
        mock_response.content = "Detailed analysis of system performance..."
        mock_response.self_assessment = mock_self_assessment
        mock_response.success = True
        mock_response.error_message = None
        
        # Mock the AI Council creation
        with patch.object(bridge, '_create_ai_council') as mock_create:
            mock_orchestration = Mock()
            
            # Create mock execution agent
            mock_execution_agent = Mock()
            
            def mock_execute(subtask, model):
                return mock_response
            
            mock_execution_agent.execute = mock_execute
            
            # Attach execution agent
            mock_orchestration.execution_agent = mock_execution_agent
            mock_orchestration.analysis_engine = Mock()
            mock_orchestration.model_registry = Mock()
            mock_orchestration.cost_optimizer = Mock()
            
            mock_create.return_value = mock_orchestration
            
            # Initialize and setup hooks
            bridge.ai_council = bridge._create_ai_council()
            bridge._setup_event_hooks("test-request-structure-999")
            
            # Execute the subtask
            result = bridge.ai_council.execution_agent.execute(mock_subtask, mock_model)
            
            # Give async tasks time to complete
            await asyncio.sleep(0.1)
            
            # Verify execution_progress was sent
            calls = ws_manager.broadcast_progress.call_args_list
            execution_progress_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "execution_progress"
            ]
            
            assert len(execution_progress_calls) > 0, "Should have execution_progress message"
            
            # Verify complete message structure
            call = execution_progress_calls[0]
            assert call[0][0] == "test-request-structure-999"
            assert call[0][1] == "execution_progress"
            
            data = call[0][2]
            
            # Verify all required fields are present
            required_fields = [
                "subtaskId", "subtaskContent", "modelId", "status",
                "confidence", "cost", "executionTime", "success"
            ]
            
            for field in required_fields:
                assert field in data, f"Should include {field} in data"
            
            # Verify field values
            assert data["subtaskId"] == "subtask-structure-test"
            assert data["subtaskContent"] == "Analyze the performance metrics of the system"
            assert data["modelId"] == "groq-llama3-70b"
            assert data["status"] == "completed"
            assert data["confidence"] == 0.87
            assert data["cost"] == 0.0023
            assert data["executionTime"] == 3.45
            assert data["success"] is True
            
            # Verify no error message for successful execution
            assert "errorMessage" not in data or data.get("errorMessage") is None
    
    @pytest.mark.asyncio
    @given(
        task_type=st.sampled_from([
            TaskType.REASONING, TaskType.CODE_GENERATION, 
            TaskType.RESEARCH, TaskType.DEBUGGING
        ])
    )
    @settings(max_examples=5, deadline=None)
    async def test_execution_progress_for_different_task_types(self, task_type):
        """Property: Execution progress is sent for all task types.
        
        This test verifies that:
        1. Execution progress messages are sent regardless of task type
        2. The message structure is consistent across task types
        """
        # Create mock WebSocket manager
        ws_manager = Mock(spec=WebSocketManager)
        ws_manager.broadcast_progress = AsyncMock(return_value=True)
        
        # Create bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Create mock subtask with specific task type
        mock_subtask = Mock(spec=Subtask)
        mock_subtask.id = f"subtask-{task_type.value}"
        mock_subtask.content = f"Task requiring {task_type.value}"
        mock_subtask.task_type = task_type
        
        # Create mock model
        mock_model = Mock()
        mock_model.get_model_id = Mock(return_value=f"model-for-{task_type.value}")
        
        # Create mock self-assessment
        mock_self_assessment = Mock(spec=SelfAssessment)
        mock_self_assessment.confidence_score = 0.75
        mock_self_assessment.estimated_cost = 0.0015
        mock_self_assessment.execution_time = 2.0
        
        # Create mock agent response
        mock_response = Mock(spec=AgentResponse)
        mock_response.subtask_id = f"subtask-{task_type.value}"
        mock_response.model_used = f"model-for-{task_type.value}"
        mock_response.content = f"Response for {task_type.value}"
        mock_response.self_assessment = mock_self_assessment
        mock_response.success = True
        mock_response.error_message = None
        
        # Mock the AI Council creation
        with patch.object(bridge, '_create_ai_council') as mock_create:
            mock_orchestration = Mock()
            
            # Create mock execution agent
            mock_execution_agent = Mock()
            
            def mock_execute(subtask, model):
                return mock_response
            
            mock_execution_agent.execute = mock_execute
            
            # Attach execution agent
            mock_orchestration.execution_agent = mock_execution_agent
            mock_orchestration.analysis_engine = Mock()
            mock_orchestration.model_registry = Mock()
            mock_orchestration.cost_optimizer = Mock()
            
            mock_create.return_value = mock_orchestration
            
            # Initialize and setup hooks
            bridge.ai_council = bridge._create_ai_council()
            bridge._setup_event_hooks(f"test-request-{task_type.value}")
            
            # Execute the subtask
            result = bridge.ai_council.execution_agent.execute(mock_subtask, mock_model)
            
            # Give async tasks time to complete
            await asyncio.sleep(0.1)
            
            # Verify execution_progress was sent
            calls = ws_manager.broadcast_progress.call_args_list
            execution_progress_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "execution_progress"
            ]
            
            assert len(execution_progress_calls) > 0, \
                f"Should have execution_progress message for {task_type.value}"
            
            # Verify the message structure is consistent
            data = execution_progress_calls[0][0][2]
            assert "subtaskId" in data
            assert "modelId" in data
            assert "confidence" in data
            assert "cost" in data
            assert "executionTime" in data
            assert "success" in data
            
            # Verify the subtask ID matches the task type
            assert data["subtaskId"] == f"subtask-{task_type.value}"
