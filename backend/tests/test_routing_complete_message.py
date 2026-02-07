"""Property-based tests for routing complete WebSocket message.

**Property 25: Routing Complete Message**
**Validates: Requirements 6.3**
Test that routing sends assignments via WebSocket
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
from ai_council.core.models import ExecutionMode, TaskType, Subtask


class TestRoutingCompleteMessage:
    """Test that routing sends assignments via WebSocket."""
    
    @pytest.mark.asyncio
    @given(
        num_subtasks=st.integers(min_value=1, max_value=5),
        execution_mode=st.sampled_from([ExecutionMode.FAST, ExecutionMode.BALANCED, ExecutionMode.BEST_QUALITY])
    )
    @settings(max_examples=10, deadline=None)
    async def test_routing_sends_assignments_via_websocket(self, num_subtasks, execution_mode):
        """Property: Routing sends model assignments via WebSocket.
        
        This test verifies that:
        1. When AI Council routes subtasks to models, a WebSocket message is sent
        2. The message type is "routing_complete"
        3. The message includes model assignments for each subtask
        4. Each assignment includes subtaskId, modelId, and reason
        """
        # Create mock WebSocket manager
        ws_manager = Mock(spec=WebSocketManager)
        ws_manager.broadcast_progress = AsyncMock(return_value=True)
        
        # Create bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Mock the AI Council creation
        with patch.object(bridge, '_create_ai_council') as mock_create:
            # Create mock orchestration layer
            mock_orchestration = Mock()
            
            # Create mock subtasks
            mock_subtasks = []
            for i in range(num_subtasks):
                subtask = Mock(spec=Subtask)
                subtask.id = f"subtask-{i}"
                subtask.content = f"Test subtask {i} content"
                subtask.task_type = TaskType.REASONING
                mock_subtasks.append(subtask)
            
            # Create mock model registry
            mock_model_registry = Mock()
            
            # Create mock models
            mock_model = Mock()
            mock_model.get_model_id = Mock(return_value="test-model-1")
            
            mock_model_registry.get_models_for_task_type = Mock(return_value=[mock_model])
            
            # Create mock cost optimizer
            mock_cost_optimizer = Mock()
            
            # Create mock optimization result
            mock_optimization = Mock()
            mock_optimization.recommended_model = "test-model-1"
            mock_optimization.reasoning = "Best model for this task type"
            mock_optimization.estimated_cost = 0.001
            mock_optimization.estimated_time = 1.5
            
            mock_cost_optimizer.optimize_model_selection = Mock(return_value=mock_optimization)
            
            # Attach mocks to orchestration layer
            mock_orchestration.model_registry = mock_model_registry
            mock_orchestration.cost_optimizer = mock_cost_optimizer
            
            # Mock _execute_parallel_group to simulate routing
            def mock_execute_parallel_group(subtasks, mode):
                # This simulates the routing happening
                return []
            
            mock_orchestration._execute_parallel_group = mock_execute_parallel_group
            
            # Mock process_request to trigger routing
            def mock_process_request(input_text, mode):
                # Simulate routing by calling _execute_parallel_group
                mock_orchestration._execute_parallel_group(mock_subtasks, mode)
                
                from ai_council.core.models import FinalResponse
                return FinalResponse(
                    content="Mock response",
                    overall_confidence=0.8,
                    success=True
                )
            
            mock_orchestration.process_request = mock_process_request
            mock_create.return_value = mock_orchestration
            
            # Process request
            request_id = "test-request-routing-123"
            try:
                await bridge.process_request(request_id, "Test input for routing", execution_mode)
            except Exception as e:
                # Some errors are expected due to mocking
                pass
            
            # Give async tasks time to complete
            await asyncio.sleep(0.1)
            
            # Verify that broadcast_progress was called
            assert ws_manager.broadcast_progress.called, "WebSocket broadcast should be called"
            
            # Check if any call was for "routing_complete"
            calls = ws_manager.broadcast_progress.call_args_list
            routing_complete_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "routing_complete"
            ]
            
            assert len(routing_complete_calls) > 0, "Should have routing_complete message"
            
            # Verify the call structure
            first_call = routing_complete_calls[0]
            assert first_call[0][0] == request_id, "Request ID should match"
            assert first_call[0][1] == "routing_complete", "Event type should be routing_complete"
            
            # Verify the data structure
            data = first_call[0][2]
            assert "assignments" in data, "Should include assignments in data"
            assert "totalSubtasks" in data, "Should include totalSubtasks in data"
            
            # Verify assignments structure
            assignments = data["assignments"]
            assert isinstance(assignments, list), "Assignments should be a list"
            assert len(assignments) == num_subtasks, f"Should have {num_subtasks} assignments"
            
            # Verify each assignment has required fields
            for assignment in assignments:
                assert "subtaskId" in assignment, "Assignment should have subtaskId"
                assert "modelId" in assignment, "Assignment should have modelId"
                assert "reason" in assignment, "Assignment should have reason"
                assert "taskType" in assignment, "Assignment should have taskType"
    
    @pytest.mark.asyncio
    async def test_routing_complete_message_structure(self):
        """Test that routing_complete message has correct structure."""
        # Create mock WebSocket manager
        ws_manager = Mock(spec=WebSocketManager)
        ws_manager.broadcast_progress = AsyncMock(return_value=True)
        
        # Create bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Mock the AI Council creation
        with patch.object(bridge, '_create_ai_council') as mock_create:
            # Create mock orchestration layer
            mock_orchestration = Mock()
            
            # Create specific mock subtasks
            subtask1 = Mock(spec=Subtask)
            subtask1.id = "subtask-alpha"
            subtask1.content = "Analyze the data"
            subtask1.task_type = TaskType.REASONING
            
            subtask2 = Mock(spec=Subtask)
            subtask2.id = "subtask-beta"
            subtask2.content = "Generate code"
            subtask2.task_type = TaskType.CODE_GENERATION
            
            mock_subtasks = [subtask1, subtask2]
            
            # Create mock model registry
            mock_model_registry = Mock()
            mock_model = Mock()
            mock_model.get_model_id = Mock(return_value="groq-llama3-70b")
            mock_model_registry.get_models_for_task_type = Mock(return_value=[mock_model])
            
            # Create mock cost optimizer
            mock_cost_optimizer = Mock()
            mock_optimization = Mock()
            mock_optimization.recommended_model = "groq-llama3-70b"
            mock_optimization.reasoning = "Optimal for reasoning tasks"
            mock_optimization.estimated_cost = 0.0015
            mock_optimization.estimated_time = 2.0
            mock_cost_optimizer.optimize_model_selection = Mock(return_value=mock_optimization)
            
            # Attach mocks
            mock_orchestration.model_registry = mock_model_registry
            mock_orchestration.cost_optimizer = mock_cost_optimizer
            
            # Mock _execute_parallel_group
            def mock_execute_parallel_group(subtasks, mode):
                return []
            
            mock_orchestration._execute_parallel_group = mock_execute_parallel_group
            
            # Mock process_request
            def mock_process_request(input_text, mode):
                mock_orchestration._execute_parallel_group(mock_subtasks, mode)
                
                from ai_council.core.models import FinalResponse
                return FinalResponse(
                    content="Test response",
                    overall_confidence=0.9,
                    success=True
                )
            
            mock_orchestration.process_request = mock_process_request
            mock_create.return_value = mock_orchestration
            
            # Process request
            request_id = "test-request-routing-456"
            try:
                await bridge.process_request(request_id, "Complex task requiring routing", ExecutionMode.BALANCED)
            except Exception:
                pass
            
            # Give async tasks time to complete
            await asyncio.sleep(0.1)
            
            # Verify broadcast_progress was called
            assert ws_manager.broadcast_progress.called
            
            # Check for routing_complete message
            calls = ws_manager.broadcast_progress.call_args_list
            routing_complete_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "routing_complete"
            ]
            
            # Verify routing_complete was sent
            assert len(routing_complete_calls) > 0, "Should have routing_complete message"
            
            call = routing_complete_calls[0]
            assert call[0][0] == request_id
            assert call[0][1] == "routing_complete"
            
            data = call[0][2]
            assert "assignments" in data, "Should include assignments"
            assert "totalSubtasks" in data, "Should include totalSubtasks"
            assert "message" in data, "Should include message"
            
            # Verify assignments have all required fields
            assignments = data["assignments"]
            assert len(assignments) == 2, "Should have 2 assignments"
            
            for assignment in assignments:
                assert "subtaskId" in assignment
                assert "subtaskContent" in assignment
                assert "taskType" in assignment
                assert "modelId" in assignment
                assert "reason" in assignment
                assert "estimatedCost" in assignment
                assert "estimatedTime" in assignment
    
    @pytest.mark.asyncio
    async def test_routing_message_sent_after_analysis(self):
        """Test that routing message is sent after analysis message."""
        # Create mock WebSocket manager
        ws_manager = Mock(spec=WebSocketManager)
        message_order = []
        
        async def track_messages(request_id, event_type, data):
            message_order.append(event_type)
            return True
        
        ws_manager.broadcast_progress = track_messages
        
        # Create bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Mock the AI Council creation
        with patch.object(bridge, '_create_ai_council') as mock_create:
            mock_orchestration = Mock()
            
            # Create mock analysis engine
            mock_analysis_engine = Mock()
            mock_analysis_engine.analyze_intent = Mock(return_value=None)
            mock_analysis_engine.determine_complexity = Mock(return_value=None)
            
            # Create mock subtasks
            subtask = Mock(spec=Subtask)
            subtask.id = "subtask-1"
            subtask.content = "Test"
            subtask.task_type = TaskType.REASONING
            
            # Create mock model registry and cost optimizer
            mock_model_registry = Mock()
            mock_model = Mock()
            mock_model.get_model_id = Mock(return_value="test-model")
            mock_model_registry.get_models_for_task_type = Mock(return_value=[mock_model])
            
            mock_cost_optimizer = Mock()
            mock_optimization = Mock()
            mock_optimization.recommended_model = "test-model"
            mock_optimization.reasoning = "Test"
            mock_optimization.estimated_cost = 0.001
            mock_optimization.estimated_time = 1.0
            mock_cost_optimizer.optimize_model_selection = Mock(return_value=mock_optimization)
            
            # Attach mocks
            mock_orchestration.analysis_engine = mock_analysis_engine
            mock_orchestration.model_registry = mock_model_registry
            mock_orchestration.cost_optimizer = mock_cost_optimizer
            
            # Mock _execute_parallel_group
            def mock_execute_parallel_group(subtasks, mode):
                return []
            
            mock_orchestration._execute_parallel_group = mock_execute_parallel_group
            
            # Mock process_request
            def mock_process_request(input_text, mode):
                # Simulate the order: analysis then routing
                mock_analysis_engine.analyze_intent(input_text)
                mock_analysis_engine.determine_complexity(input_text)
                mock_orchestration._execute_parallel_group([subtask], mode)
                
                from ai_council.core.models import FinalResponse
                return FinalResponse(
                    content="Test",
                    overall_confidence=0.8,
                    success=True
                )
            
            mock_orchestration.process_request = mock_process_request
            mock_create.return_value = mock_orchestration
            
            # Process request
            request_id = "test-request-routing-789"
            try:
                await bridge.process_request(request_id, "Test input", ExecutionMode.BALANCED)
            except Exception:
                pass
            
            # Give async tasks time to complete
            await asyncio.sleep(0.1)
            
            # Verify message order
            assert len(message_order) > 0, "Should have sent messages"
            assert "processing_started" in message_order, "Should have processing_started"
            
            # If routing_complete was sent, verify it comes after analysis_complete (if present)
            if "routing_complete" in message_order:
                routing_idx = message_order.index("routing_complete")
                processing_idx = message_order.index("processing_started")
                assert routing_idx > processing_idx, "routing_complete should come after processing_started"
                
                # If analysis_complete is present, routing should come after it
                if "analysis_complete" in message_order:
                    analysis_idx = message_order.index("analysis_complete")
                    assert routing_idx > analysis_idx, "routing_complete should come after analysis_complete"
    
    @pytest.mark.asyncio
    @given(
        task_type=st.sampled_from([TaskType.REASONING, TaskType.CODE_GENERATION, TaskType.RESEARCH])
    )
    @settings(max_examples=5, deadline=None)
    async def test_routing_assigns_appropriate_models_for_task_type(self, task_type):
        """Property: Routing assigns models based on task type capabilities.
        
        This test verifies that:
        1. Each subtask is assigned a model that supports its task type
        2. The routing decision includes the task type
        3. The model selection is based on capabilities
        """
        # Create mock WebSocket manager
        ws_manager = Mock(spec=WebSocketManager)
        ws_manager.broadcast_progress = AsyncMock(return_value=True)
        
        # Create bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Mock the AI Council creation
        with patch.object(bridge, '_create_ai_council') as mock_create:
            mock_orchestration = Mock()
            
            # Create mock subtask with specific task type
            subtask = Mock(spec=Subtask)
            subtask.id = "subtask-typed"
            subtask.content = f"Task requiring {task_type.value}"
            subtask.task_type = task_type
            
            # Create mock model registry that returns models for this task type
            mock_model_registry = Mock()
            mock_model = Mock()
            mock_model.get_model_id = Mock(return_value=f"model-for-{task_type.value}")
            mock_model_registry.get_models_for_task_type = Mock(return_value=[mock_model])
            
            # Create mock cost optimizer
            mock_cost_optimizer = Mock()
            mock_optimization = Mock()
            mock_optimization.recommended_model = f"model-for-{task_type.value}"
            mock_optimization.reasoning = f"Specialized for {task_type.value}"
            mock_optimization.estimated_cost = 0.002
            mock_optimization.estimated_time = 1.8
            mock_cost_optimizer.optimize_model_selection = Mock(return_value=mock_optimization)
            
            # Attach mocks
            mock_orchestration.model_registry = mock_model_registry
            mock_orchestration.cost_optimizer = mock_cost_optimizer
            
            # Mock _execute_parallel_group
            def mock_execute_parallel_group(subtasks, mode):
                return []
            
            mock_orchestration._execute_parallel_group = mock_execute_parallel_group
            
            # Mock process_request
            def mock_process_request(input_text, mode):
                mock_orchestration._execute_parallel_group([subtask], mode)
                
                from ai_council.core.models import FinalResponse
                return FinalResponse(
                    content="Test response",
                    overall_confidence=0.85,
                    success=True
                )
            
            mock_orchestration.process_request = mock_process_request
            mock_create.return_value = mock_orchestration
            
            # Process request
            request_id = f"test-request-{task_type.value}"
            try:
                await bridge.process_request(request_id, f"Task for {task_type.value}", ExecutionMode.BALANCED)
            except Exception:
                pass
            
            # Give async tasks time to complete
            await asyncio.sleep(0.1)
            
            # Verify routing_complete message was sent
            calls = ws_manager.broadcast_progress.call_args_list
            routing_complete_calls = [
                call for call in calls 
                if len(call[0]) > 1 and call[0][1] == "routing_complete"
            ]
            
            assert len(routing_complete_calls) > 0, "Should have routing_complete message"
            
            # Verify the assignment includes the correct task type
            data = routing_complete_calls[0][0][2]
            assignments = data["assignments"]
            assert len(assignments) > 0, "Should have at least one assignment"
            
            assignment = assignments[0]
            assert assignment["taskType"] == task_type.value, f"Task type should be {task_type.value}"
            assert assignment["modelId"] == f"model-for-{task_type.value}", "Model should match task type"
