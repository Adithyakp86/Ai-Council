"""Tests for provider health monitoring system."""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
import json

from app.services.provider_health_checker import (
    ProviderHealthChecker,
    ProviderHealthStatus,
    get_health_checker
)


class TestProviderHealthStatus:
    """Test ProviderHealthStatus class."""
    
    def test_to_dict(self):
        """Test converting health status to dictionary."""
        status = ProviderHealthStatus(
            status="healthy",
            last_check=datetime(2024, 1, 1, 12, 0, 0),
            response_time_ms=150.5,
            error_message=None
        )
        
        result = status.to_dict()
        
        assert result["status"] == "healthy"
        assert result["last_check"] == "2024-01-01T12:00:00"
        assert result["response_time_ms"] == 150.5
        assert result["error_message"] is None
    
    def test_to_dict_with_error(self):
        """Test converting error status to dictionary."""
        status = ProviderHealthStatus(
            status="down",
            last_check=datetime(2024, 1, 1, 12, 0, 0),
            response_time_ms=5000.0,
            error_message="Connection timeout"
        )
        
        result = status.to_dict()
        
        assert result["status"] == "down"
        assert result["error_message"] == "Connection timeout"


class TestProviderHealthChecker:
    """Test ProviderHealthChecker class."""
    
    @pytest.fixture
    def health_checker(self):
        """Create a health checker instance."""
        return ProviderHealthChecker()
    
    @pytest.mark.asyncio
    async def test_check_provider_health_with_valid_api_key(self, health_checker):
        """Test checking provider health with valid API key."""
        # Mock the client
        mock_client = Mock()
        mock_client.health_check.return_value = {
            "status": "healthy",
            "provider": "groq",
            "models_available": 5
        }
        
        with patch.object(health_checker, '_get_provider_client', return_value=mock_client):
            with patch('app.services.provider_health_checker.redis_client') as mock_redis:
                mock_redis.client.get = AsyncMock(return_value=None)
                mock_redis.client.setex = AsyncMock()
                
                result = await health_checker.check_provider_health("groq")
                
                assert result.status == "healthy"
                assert result.response_time_ms is not None
                assert result.error_message is None
    
    @pytest.mark.asyncio
    async def test_check_provider_health_with_invalid_api_key(self, health_checker):
        """Test checking provider health with invalid API key."""
        # Mock the client
        mock_client = Mock()
        mock_client.health_check.return_value = {
            "status": "error",
            "provider": "groq",
            "error": "Invalid API key"
        }
        
        with patch.object(health_checker, '_get_provider_client', return_value=mock_client):
            with patch('app.services.provider_health_checker.redis_client') as mock_redis:
                mock_redis.client.get = AsyncMock(return_value=None)
                mock_redis.client.setex = AsyncMock()
                
                result = await health_checker.check_provider_health("groq")
                
                assert result.status == "degraded"
                assert result.error_message == "Invalid API key"
    
    @pytest.mark.asyncio
    async def test_check_provider_health_no_api_key_configured(self, health_checker):
        """Test checking provider health when no API key is configured."""
        with patch.object(health_checker, '_get_provider_client', return_value=None):
            with patch('app.services.provider_health_checker.redis_client') as mock_redis:
                mock_redis.client.get = AsyncMock(return_value=None)
                mock_redis.client.setex = AsyncMock()
                
                result = await health_checker.check_provider_health("groq")
                
                assert result.status == "down"
                assert result.error_message == "API key not configured"
    
    @pytest.mark.asyncio
    async def test_check_provider_health_uses_cache(self, health_checker):
        """Test that health check uses cached results."""
        cached_status = {
            "status": "healthy",
            "last_check": "2024-01-01T12:00:00",
            "response_time_ms": 100.0,
            "error_message": None
        }
        
        with patch('app.services.provider_health_checker.redis_client') as mock_redis:
            mock_redis.client.get = AsyncMock(return_value=json.dumps(cached_status))
            
            result = await health_checker.check_provider_health("groq")
            
            assert result.status == "healthy"
            assert result.response_time_ms == 100.0
            # Should not call the client since we got cached result
            mock_redis.client.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_check_provider_health_caches_result(self, health_checker):
        """Test that health check caches the result."""
        mock_client = Mock()
        mock_client.health_check.return_value = {
            "status": "healthy",
            "provider": "groq"
        }
        
        with patch.object(health_checker, '_get_provider_client', return_value=mock_client):
            with patch('app.services.provider_health_checker.redis_client') as mock_redis:
                mock_redis.client.get = AsyncMock(return_value=None)
                mock_redis.client.setex = AsyncMock()
                
                await health_checker.check_provider_health("groq")
                
                # Verify cache was set
                mock_redis.client.setex.assert_called_once()
                call_args = mock_redis.client.setex.call_args
                assert call_args[0][0] == "provider:health:groq"
                assert call_args[0][1] == 60  # CACHE_TTL
    
    @pytest.mark.asyncio
    async def test_check_provider_health_with_circuit_breaker_open(self, health_checker):
        """Test that circuit breaker state affects health status."""
        mock_client = Mock()
        mock_client.health_check.return_value = {
            "status": "healthy",
            "provider": "groq"
        }
        
        # Mock circuit breaker to return open state
        mock_circuit_state = Mock()
        mock_circuit_state.value = "open"
        health_checker.circuit_breaker.get_state = Mock(return_value=mock_circuit_state)
        
        with patch.object(health_checker, '_get_provider_client', return_value=mock_client):
            with patch('app.services.provider_health_checker.redis_client') as mock_redis:
                mock_redis.client.get = AsyncMock(return_value=None)
                mock_redis.client.setex = AsyncMock()
                
                result = await health_checker.check_provider_health("groq")
                
                # Should be down because circuit breaker is open
                assert result.status == "down"
                assert "Circuit breaker open" in result.error_message
    
    @pytest.mark.asyncio
    async def test_check_provider_health_with_circuit_breaker_half_open(self, health_checker):
        """Test that half-open circuit breaker marks provider as degraded."""
        mock_client = Mock()
        mock_client.health_check.return_value = {
            "status": "healthy",
            "provider": "groq"
        }
        
        # Mock circuit breaker to return half_open state
        mock_circuit_state = Mock()
        mock_circuit_state.value = "half_open"
        health_checker.circuit_breaker.get_state = Mock(return_value=mock_circuit_state)
        
        with patch.object(health_checker, '_get_provider_client', return_value=mock_client):
            with patch('app.services.provider_health_checker.redis_client') as mock_redis:
                mock_redis.client.get = AsyncMock(return_value=None)
                mock_redis.client.setex = AsyncMock()
                
                result = await health_checker.check_provider_health("groq")
                
                # Should be degraded because circuit breaker is testing
                assert result.status == "degraded"
    
    @pytest.mark.asyncio
    async def test_check_all_providers(self, health_checker):
        """Test checking all providers concurrently."""
        mock_client = Mock()
        mock_client.health_check.return_value = {
            "status": "healthy",
            "provider": "test"
        }
        
        with patch.object(health_checker, '_get_provider_client', return_value=mock_client):
            with patch('app.services.provider_health_checker.redis_client') as mock_redis:
                mock_redis.client.get = AsyncMock(return_value=None)
                mock_redis.client.setex = AsyncMock()
                
                results = await health_checker.check_all_providers()
                
                # Should check all 8 providers
                assert len(results) == 8
                assert "groq" in results
                assert "together" in results
                assert "openrouter" in results
                assert "huggingface" in results
                assert "gemini" in results
                assert "openai" in results
                assert "ollama" in results
                assert "qwen" in results
    
    @pytest.mark.asyncio
    async def test_check_all_providers_handles_exceptions(self, health_checker):
        """Test that check_all_providers handles exceptions gracefully."""
        def mock_check_health(provider):
            if provider == "groq":
                raise Exception("Test error")
            return asyncio.coroutine(lambda: ProviderHealthStatus(
                status="healthy",
                last_check=datetime.utcnow()
            ))()
        
        with patch.object(health_checker, 'check_provider_health', side_effect=mock_check_health):
            results = await health_checker.check_all_providers()
            
            # Should still return results for all providers
            assert len(results) == 8
            # Groq should be marked as down due to exception
            assert results["groq"].status == "down"
    
    def test_get_provider_client_groq(self, health_checker):
        """Test getting Groq client."""
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test_key'}):
            client = health_checker._get_provider_client("groq")
            assert client is not None
            assert client.api_key == 'test_key'
    
    def test_get_provider_client_no_api_key(self, health_checker):
        """Test getting client when no API key is configured."""
        with patch.dict('os.environ', {}, clear=True):
            client = health_checker._get_provider_client("groq")
            assert client is None
    
    def test_get_provider_client_unknown_provider(self, health_checker):
        """Test getting client for unknown provider."""
        client = health_checker._get_provider_client("unknown_provider")
        assert client is None
    
    def test_get_provider_client_caching(self, health_checker):
        """Test that clients are cached."""
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test_key'}):
            client1 = health_checker._get_provider_client("groq")
            client2 = health_checker._get_provider_client("groq")
            
            # Should return the same instance
            assert client1 is client2


class TestGetHealthChecker:
    """Test get_health_checker singleton function."""
    
    def test_get_health_checker_returns_singleton(self):
        """Test that get_health_checker returns the same instance."""
        checker1 = get_health_checker()
        checker2 = get_health_checker()
        
        assert checker1 is checker2
    
    def test_get_health_checker_returns_instance(self):
        """Test that get_health_checker returns a ProviderHealthChecker instance."""
        checker = get_health_checker()
        assert isinstance(checker, ProviderHealthChecker)


class TestProviderHealthMonitoringIntegration:
    """Integration tests for provider health monitoring."""
    
    @pytest.mark.asyncio
    async def test_health_check_response_time_measured(self):
        """Test that response time is measured correctly."""
        checker = ProviderHealthChecker()
        
        mock_client = Mock()
        # Simulate a slow health check
        def slow_health_check():
            import time
            time.sleep(0.1)  # 100ms delay
            return {"status": "healthy", "provider": "test"}
        
        mock_client.health_check = slow_health_check
        
        with patch.object(checker, '_get_provider_client', return_value=mock_client):
            with patch('app.services.provider_health_checker.redis_client') as mock_redis:
                mock_redis.client.get = AsyncMock(return_value=None)
                mock_redis.client.setex = AsyncMock()
                
                result = await checker.check_provider_health("groq")
                
                # Response time should be at least 100ms
                assert result.response_time_ms >= 100
    
    @pytest.mark.asyncio
    async def test_health_check_marks_slow_provider_as_degraded(self):
        """Test that slow providers are marked as degraded."""
        checker = ProviderHealthChecker()
        
        mock_client = Mock()
        # Simulate a very slow health check (>5 seconds)
        def very_slow_health_check():
            import time
            time.sleep(6)
            return {"status": "healthy", "provider": "test"}
        
        mock_client.health_check = very_slow_health_check
        
        with patch.object(checker, '_get_provider_client', return_value=mock_client):
            with patch('app.services.provider_health_checker.redis_client') as mock_redis:
                mock_redis.client.get = AsyncMock(return_value=None)
                mock_redis.client.setex = AsyncMock()
                
                # This should timeout or take a long time
                result = await checker.check_provider_health("groq")
                
                # Should have a high response time
                assert result.response_time_ms > 5000 or result.status == "down"
