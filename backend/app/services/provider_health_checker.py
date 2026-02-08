"""Provider health check service for monitoring cloud AI providers."""

import asyncio
import logging
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import httpx

from app.core.redis import redis_client
from app.services.cloud_ai.circuit_breaker import get_circuit_breaker

logger = logging.getLogger(__name__)


class ProviderHealthStatus:
    """Health status for a cloud AI provider."""
    
    def __init__(
        self,
        status: str,
        last_check: datetime,
        response_time_ms: Optional[float] = None,
        error_message: Optional[str] = None
    ):
        self.status = status  # "healthy", "degraded", or "down"
        self.last_check = last_check
        self.response_time_ms = response_time_ms
        self.error_message = error_message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "status": self.status,
            "last_check": self.last_check.isoformat(),
            "response_time_ms": self.response_time_ms,
            "error_message": self.error_message
        }


class ProviderHealthChecker:
    """Health checker for cloud AI providers with caching."""
    
    CACHE_TTL = 60  # Cache health status for 1 minute
    TIMEOUT = 10.0  # 10 second timeout for health checks
    
    def __init__(self):
        self.circuit_breaker = get_circuit_breaker()
        self._clients_cache = {}
    
    def _get_cache_key(self, provider: str) -> str:
        """Get Redis cache key for provider health status."""
        return f"provider:health:{provider}"
    
    def _get_provider_client(self, provider: str):
        """
        Get or create a client instance for the provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Client instance or None if API key not configured
        """
        # Check cache first
        if provider in self._clients_cache:
            return self._clients_cache[provider]
        
        # Import clients dynamically to avoid circular imports
        from app.services.cloud_ai.groq_client import GroqClient
        from app.services.cloud_ai.together_client import TogetherClient
        from app.services.cloud_ai.openrouter_client import OpenRouterClient
        from app.services.cloud_ai.huggingface_client import HuggingFaceClient
        from app.services.cloud_ai.gemini_adapter import GeminiClient
        from app.services.cloud_ai.openai_client import OpenAIClient
        from app.services.cloud_ai.ollama_client import OllamaClient
        from app.services.cloud_ai.qwen_client import QwenClient
        
        # Map provider names to environment variables and client classes
        provider_config = {
            "groq": ("GROQ_API_KEY", GroqClient),
            "together": ("TOGETHER_API_KEY", TogetherClient),
            "openrouter": ("OPENROUTER_API_KEY", OpenRouterClient),
            "huggingface": ("HUGGINGFACE_TOKEN", HuggingFaceClient),
            "gemini": ("GEMINI_API_KEY", GeminiClient),
            "openai": ("OPENAI_API_KEY", OpenAIClient),
            "qwen": ("QWEN_API_KEY", QwenClient),
            "ollama": ("OLLAMA_ENDPOINT", OllamaClient),
        }
        
        if provider not in provider_config:
            logger.warning(f"Unknown provider: {provider}")
            return None
        
        env_var, client_class = provider_config[provider]
        api_key = os.getenv(env_var, "")
        
        if not api_key:
            logger.debug(f"No API key configured for {provider}")
            return None
        
        try:
            # Special handling for Ollama (uses endpoint instead of API key)
            if provider == "ollama":
                client = client_class(base_url=api_key)
            else:
                client = client_class(api_key=api_key)
            
            self._clients_cache[provider] = client
            return client
        except Exception as e:
            logger.error(f"Error creating client for {provider}: {e}")
            return None
    
    async def _check_provider_with_client(self, provider: str) -> ProviderHealthStatus:
        """
        Check a provider's health using its client's health_check method.
        
        Args:
            provider: Provider name
            
        Returns:
            ProviderHealthStatus object
        """
        start_time = time.time()
        
        try:
            client = self._get_provider_client(provider)
            
            if client is None:
                return ProviderHealthStatus(
                    status="down",
                    last_check=datetime.utcnow(),
                    error_message="API key not configured"
                )
            
            # Call the client's health_check method
            # Run in thread pool to avoid blocking
            import asyncio
            loop = asyncio.get_event_loop()
            health_result = await loop.run_in_executor(None, client.health_check)
            
            response_time_ms = (time.time() - start_time) * 1000
            
            # Parse health result
            status = health_result.get("status", "error")
            error_message = health_result.get("error")
            
            # Map status values
            if status == "healthy":
                final_status = "healthy"
            elif status == "down":
                final_status = "down"
            else:
                final_status = "degraded"
            
            return ProviderHealthStatus(
                status=final_status,
                last_check=datetime.utcnow(),
                response_time_ms=response_time_ms,
                error_message=error_message
            )
            
        except asyncio.TimeoutError:
            response_time_ms = (time.time() - start_time) * 1000
            return ProviderHealthStatus(
                status="down",
                last_check=datetime.utcnow(),
                response_time_ms=response_time_ms,
                error_message="Health check timeout"
            )
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            logger.error(f"Error checking health for {provider}: {e}")
            return ProviderHealthStatus(
                status="down",
                last_check=datetime.utcnow(),
                response_time_ms=response_time_ms,
                error_message=str(e)
            )
    
    async def check_provider_health(self, provider: str) -> ProviderHealthStatus:
        """
        Check health of a single provider with caching.
        
        Args:
            provider: Provider name
            
        Returns:
            ProviderHealthStatus object
        """
        # Try to get from cache first
        try:
            cache_key = self._get_cache_key(provider)
            cached_data = await redis_client.client.get(cache_key)
            
            if cached_data:
                # Parse cached data
                import json
                data = json.loads(cached_data)
                return ProviderHealthStatus(
                    status=data["status"],
                    last_check=datetime.fromisoformat(data["last_check"]),
                    response_time_ms=data.get("response_time_ms"),
                    error_message=data.get("error_message")
                )
        except Exception as e:
            logger.warning(f"Error reading health cache for {provider}: {e}")
        
        # Cache miss or error - perform health check using client
        health_status = await self._check_provider_with_client(provider)
        
        # Also consider circuit breaker state
        circuit_state = self.circuit_breaker.get_state(provider)
        if circuit_state.value == "open":
            # Circuit breaker is open - provider is down
            health_status.status = "down"
            if not health_status.error_message:
                health_status.error_message = "Circuit breaker open"
        elif circuit_state.value == "half_open":
            # Circuit breaker is testing - provider is degraded
            if health_status.status == "healthy":
                health_status.status = "degraded"
                if not health_status.error_message:
                    health_status.error_message = "Circuit breaker testing"
        
        # Cache the result
        try:
            cache_key = self._get_cache_key(provider)
            import json
            cache_data = json.dumps(health_status.to_dict())
            await redis_client.client.setex(
                cache_key,
                self.CACHE_TTL,
                cache_data
            )
        except Exception as e:
            logger.warning(f"Error caching health status for {provider}: {e}")
        
        return health_status
    
    async def check_all_providers(self) -> Dict[str, ProviderHealthStatus]:
        """
        Check health of all configured providers concurrently.
        
        Returns:
            Dictionary mapping provider names to health status
        """
        # List of all supported providers
        providers = ["groq", "together", "openrouter", "huggingface", "gemini", "openai", "ollama", "qwen"]
        
        # Check all providers concurrently
        tasks = [
            self.check_provider_health(provider)
            for provider in providers
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Build result dictionary
        health_statuses = {}
        for provider, result in zip(providers, results):
            if isinstance(result, Exception):
                logger.error(f"Error checking health for {provider}: {result}")
                health_statuses[provider] = ProviderHealthStatus(
                    status="down",
                    last_check=datetime.utcnow(),
                    error_message=str(result)
                )
            else:
                health_statuses[provider] = result
        
        return health_statuses


# Global health checker instance
_health_checker: Optional[ProviderHealthChecker] = None


def get_health_checker() -> ProviderHealthChecker:
    """Get the global health checker instance."""
    global _health_checker
    if _health_checker is None:
        _health_checker = ProviderHealthChecker()
    return _health_checker
