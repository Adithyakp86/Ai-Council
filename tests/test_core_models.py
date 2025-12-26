"""Tests for core data models."""

import pytest
from datetime import datetime
from hypothesis import given, strategies as st
from ai_council.core.models import (
    Task, Subtask, SelfAssessment, AgentResponse, FinalResponse,
    TaskType, ExecutionMode, RiskLevel, Priority, ComplexityLevel,
    TaskIntent, ModelCapabilities, CostProfile, PerformanceMetrics,
    CostBreakdown, ExecutionMetadata
)


class TestTask:
    """Test Task data model."""
    
    def test_task_creation(self):
        """Test basic task creation."""
        task = Task(content="Test task")
        assert task.content == "Test task"
        assert task.execution_mode == ExecutionMode.BALANCED
        assert isinstance(task.created_at, datetime)
        assert task.id  # Should have a UUID
    
    def test_task_validation(self):
        """Test task validation."""
        with pytest.raises(ValueError, match="Task content cannot be empty"):
            Task(content="")
        
        with pytest.raises(ValueError, match="Task content cannot be empty"):
            Task(content="   ")


class TestSubtask:
    """Test Subtask data model."""
    
    def test_subtask_creation(self):
        """Test basic subtask creation."""
        subtask = Subtask(
            content="Test subtask",
            parent_task_id="parent-123",
            task_type=TaskType.REASONING
        )
        assert subtask.content == "Test subtask"
        assert subtask.parent_task_id == "parent-123"
        assert subtask.task_type == TaskType.REASONING
        assert subtask.priority == Priority.MEDIUM
        assert subtask.accuracy_requirement == 0.8
    
    def test_subtask_validation(self):
        """Test subtask validation."""
        with pytest.raises(ValueError, match="Subtask content cannot be empty"):
            Subtask(content="")
        
        with pytest.raises(ValueError, match="Accuracy requirement must be between 0.0 and 1.0"):
            Subtask(content="test", accuracy_requirement=1.5)
        
        with pytest.raises(ValueError, match="Estimated cost cannot be negative"):
            Subtask(content="test", estimated_cost=-1.0)


class TestSelfAssessment:
    """Test SelfAssessment data model."""
    
    def test_self_assessment_creation(self):
        """Test basic self-assessment creation."""
        assessment = SelfAssessment(
            confidence_score=0.85,
            assumptions=["Assumption 1"],
            risk_level=RiskLevel.LOW,
            model_used="gpt-4"
        )
        assert assessment.confidence_score == 0.85
        assert assessment.assumptions == ["Assumption 1"]
        assert assessment.risk_level == RiskLevel.LOW
        assert assessment.model_used == "gpt-4"
    
    def test_self_assessment_validation(self):
        """Test self-assessment validation."""
        with pytest.raises(ValueError, match="Confidence score must be between 0.0 and 1.0"):
            SelfAssessment(confidence_score=1.5)
        
        with pytest.raises(ValueError, match="Estimated cost cannot be negative"):
            SelfAssessment(estimated_cost=-1.0)
        
        with pytest.raises(ValueError, match="Token usage cannot be negative"):
            SelfAssessment(token_usage=-1)


class TestAgentResponse:
    """Test AgentResponse data model."""
    
    def test_agent_response_creation(self):
        """Test basic agent response creation."""
        assessment = SelfAssessment(confidence_score=0.8, model_used="gpt-4")
        response = AgentResponse(
            subtask_id="subtask-123",
            model_used="gpt-4",
            content="Response content",
            self_assessment=assessment
        )
        assert response.subtask_id == "subtask-123"
        assert response.model_used == "gpt-4"
        assert response.content == "Response content"
        assert response.success is True
    
    def test_agent_response_validation(self):
        """Test agent response validation."""
        with pytest.raises(ValueError, match="Subtask ID cannot be empty"):
            AgentResponse(subtask_id="", model_used="gpt-4", content="test")
        
        with pytest.raises(ValueError, match="Model used cannot be empty"):
            AgentResponse(subtask_id="test", model_used="", content="test")
        
        with pytest.raises(ValueError, match="Successful response must have content"):
            AgentResponse(subtask_id="test", model_used="gpt-4", content="", success=True)
        
        with pytest.raises(ValueError, match="Failed response must have error message"):
            AgentResponse(subtask_id="test", model_used="gpt-4", content="", success=False)


class TestFinalResponse:
    """Test FinalResponse data model."""
    
    def test_final_response_creation(self):
        """Test basic final response creation."""
        response = FinalResponse(
            content="Final response content",
            overall_confidence=0.9,
            models_used=["gpt-4", "claude-3"]
        )
        assert response.content == "Final response content"
        assert response.overall_confidence == 0.9
        assert response.models_used == ["gpt-4", "claude-3"]
        assert response.success is True
    
    def test_final_response_validation(self):
        """Test final response validation."""
        with pytest.raises(ValueError, match="Overall confidence must be between 0.0 and 1.0"):
            FinalResponse(overall_confidence=1.5)
        
        with pytest.raises(ValueError, match="Successful response must have content"):
            FinalResponse(content="", success=True)
        
        with pytest.raises(ValueError, match="Failed response must have error message"):
            FinalResponse(content="", success=False)


class TestEnumerations:
    """Test enumeration values."""
    
    def test_task_type_enum(self):
        """Test TaskType enumeration."""
        assert TaskType.REASONING.value == "reasoning"
        assert TaskType.CODE_GENERATION.value == "code_generation"
        assert TaskType.RESEARCH.value == "research"
    
    def test_execution_mode_enum(self):
        """Test ExecutionMode enumeration."""
        assert ExecutionMode.FAST.value == "fast"
        assert ExecutionMode.BALANCED.value == "balanced"
        assert ExecutionMode.BEST_QUALITY.value == "best_quality"
    
    def test_risk_level_enum(self):
        """Test RiskLevel enumeration."""
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"


class TestModelCapabilities:
    """Test ModelCapabilities data model."""
    
    def test_model_capabilities_creation(self):
        """Test basic model capabilities creation."""
        capabilities = ModelCapabilities(
            task_types=[TaskType.REASONING, TaskType.CODE_GENERATION],
            cost_per_token=0.00003,
            average_latency=1.5,
            max_context_length=8192,
            reliability_score=0.95,
            strengths=["reasoning", "coding"],
            weaknesses=["image generation"]
        )
        assert len(capabilities.task_types) == 2
        assert capabilities.cost_per_token == 0.00003
        assert capabilities.reliability_score == 0.95
    
    def test_model_capabilities_validation(self):
        """Test model capabilities validation."""
        with pytest.raises(ValueError, match="Cost per token cannot be negative"):
            ModelCapabilities(cost_per_token=-1.0)
        
        with pytest.raises(ValueError, match="Reliability score must be between 0.0 and 1.0"):
            ModelCapabilities(reliability_score=1.5)


class TestCostBreakdown:
    """Test CostBreakdown data model."""
    
    def test_cost_breakdown_creation(self):
        """Test basic cost breakdown creation."""
        breakdown = CostBreakdown(
            total_cost=0.15,
            model_costs={"gpt-4": 0.10, "claude-3": 0.05},
            token_usage={"gpt-4": 1000, "claude-3": 500},
            execution_time=5.2
        )
        assert breakdown.total_cost == 0.15
        assert breakdown.model_costs["gpt-4"] == 0.10
        assert breakdown.execution_time == 5.2
    
    def test_cost_breakdown_validation(self):
        """Test cost breakdown validation."""
        with pytest.raises(ValueError, match="Total cost cannot be negative"):
            CostBreakdown(total_cost=-1.0)
        
        with pytest.raises(ValueError, match="Execution time cannot be negative"):
            CostBreakdown(execution_time=-1.0)


class TestDataModelRoundTripConsistency:
    """Property-based tests for data model round-trip consistency.
    
    **Feature: ai-council, Property 1: Data model round-trip consistency**
    **Validates: Requirements 3.3**
    """
    
    def test_self_assessment_round_trip_consistency_basic(self):
        """
        Property 1: Data model round-trip consistency (Basic version)
        
        For any valid SelfAssessment data, creating a SelfAssessment object
        and then accessing its fields should preserve all the original values
        and maintain validation constraints.
        
        **Validates: Requirements 3.3**
        """
        # Test with multiple valid combinations
        test_cases = [
            {
                'confidence_score': 0.5,
                'assumptions': ['test assumption'],
                'risk_level': RiskLevel.LOW,
                'estimated_cost': 10.0,
                'token_usage': 100,
                'execution_time': 5.0,
                'model_used': 'gpt-4'
            },
            {
                'confidence_score': 1.0,
                'assumptions': [],
                'risk_level': RiskLevel.HIGH,
                'estimated_cost': 0.0,
                'token_usage': 0,
                'execution_time': 0.0,
                'model_used': 'claude'
            },
            {
                'confidence_score': 0.0,
                'assumptions': ['assumption1', 'assumption2'],
                'risk_level': RiskLevel.MEDIUM,
                'estimated_cost': 50.5,
                'token_usage': 1000,
                'execution_time': 15.5,
                'model_used': 'gemini'
            }
        ]
        
        for test_data in test_cases:
            # Create SelfAssessment with test data
            original_assessment = SelfAssessment(**test_data)
            
            # Verify round-trip consistency - all fields should be preserved
            assert original_assessment.confidence_score == test_data['confidence_score']
            assert original_assessment.assumptions == test_data['assumptions']
            assert original_assessment.risk_level == test_data['risk_level']
            assert original_assessment.estimated_cost == test_data['estimated_cost']
            assert original_assessment.token_usage == test_data['token_usage']
            assert original_assessment.execution_time == test_data['execution_time']
            assert original_assessment.model_used == test_data['model_used']
            
            # Verify validation constraints are maintained (Requirements 3.3)
            assert 0.0 <= original_assessment.confidence_score <= 1.0
            assert isinstance(original_assessment.assumptions, list)
            assert isinstance(original_assessment.risk_level, RiskLevel)
            assert original_assessment.estimated_cost >= 0.0
            assert original_assessment.token_usage >= 0
            assert original_assessment.execution_time >= 0.0
            assert isinstance(original_assessment.model_used, str)
            assert len(original_assessment.model_used) > 0
            
            # Verify timestamp is set and is a datetime
            assert isinstance(original_assessment.timestamp, datetime)
    
    @pytest.mark.property
    def test_self_assessment_validation_constraints(self):
        """
        Property 1: Data model validation constraints
        
        Test that SelfAssessment enforces validation constraints as specified
        in Requirements 3.3: confidence score between 0 and 1, assumptions list,
        risk level, and cost estimates.
        
        **Validates: Requirements 3.3**
        """
        # Test confidence score bounds
        with pytest.raises(ValueError, match="Confidence score must be between 0.0 and 1.0"):
            SelfAssessment(confidence_score=1.5, model_used="test")
        
        with pytest.raises(ValueError, match="Confidence score must be between 0.0 and 1.0"):
            SelfAssessment(confidence_score=-0.1, model_used="test")
        
        # Test cost constraints
        with pytest.raises(ValueError, match="Estimated cost cannot be negative"):
            SelfAssessment(estimated_cost=-1.0, model_used="test")
        
        # Test token usage constraints
        with pytest.raises(ValueError, match="Token usage cannot be negative"):
            SelfAssessment(token_usage=-1, model_used="test")
        
        # Test execution time constraints
        with pytest.raises(ValueError, match="Execution time cannot be negative"):
            SelfAssessment(execution_time=-1.0, model_used="test")
        
        # Test valid boundary values
        valid_assessment = SelfAssessment(
            confidence_score=0.0,
            assumptions=[],
            risk_level=RiskLevel.LOW,
            estimated_cost=0.0,
            token_usage=0,
            execution_time=0.0,
            model_used="test"
        )
        assert valid_assessment.confidence_score == 0.0
        
        valid_assessment_max = SelfAssessment(
            confidence_score=1.0,
            assumptions=["test"],
            risk_level=RiskLevel.CRITICAL,
            estimated_cost=1000.0,
            token_usage=10000,
            execution_time=300.0,
            model_used="test"
        )
        assert valid_assessment_max.confidence_score == 1.0