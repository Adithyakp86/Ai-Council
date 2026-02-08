"""Unified provider configuration system for all AI providers.

This module manages API keys, endpoints, and health checks for all AI providers.
It validates configuration on startup and provides a centralized interface for
provider management.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
import httpx
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class ProviderType(Enum):
    """Type of AI provider."""
    FREE = "free"  # No cost, no billing required
    PAID = "paid"  # Requires payment or has paid tiers
    LOCAL = "local"  # Runs locally on user's machine


class ProviderStatus(Enum):
    """Health status of a provider."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    DISABLED = "disabled"
    NOT_CONFIGURED = "not_configured"


@dataclass
class ProviderInfo:
    """Information about an AI provider."""
    name: str
    display_name: str
    provider_type: ProviderType
    env_var: str
    endpoint: Optional[str]
    docs_url: str
    signup_url: str
    description: str
    free_tier_info: Optional[str]
    is_configured: bool = False
    is_available: bool = False
    status: ProviderStatus = ProviderStatus.NOT_CONFIGURED
    last_health_check: Optional[datetime] = None


class ProviderConfig:
    """Unified configuration manager for all AI providers.
    
    This class:
    - Loads API keys from environment variables
    - Validates API keys on startup
    - Provides health check functionality
    - Logs which providers are available
    - Manages provider endpoints and configuration
    """
    
    # Provider definitions with metadata
    PROVIDERS: Dict[str, Dict[str, Any]] = {
        "ollama": {
            "display_name": "Ollama",
            "provider_type": ProviderType.LOCAL,
            "env_var": "OLLAMA_ENDPOINT",
            "endpoint_env": "OLLAMA_ENDPOINT",
            "default_endpoint": "http://localhost:11434",
            "docs_url": "backend/docs/OLLAMA_SETUP.md",
            "signup_url": "https://ollama.ai",
            "description": "Local AI models running on your machine. 100% free, no API keys needed.",
            "free_tier_info": "Completely free - runs locally on your hardware",
        },
        "gemini": {
            "display_name": "Google Gemini",
            "provider_type": ProviderType.FREE,
            "env_var": "GEMINI_API_KEY",
            "endpoint": "https://generativelanguage.googleapis.com",
            "docs_url": "backend/docs/GEMINI_SETUP.md",
            "signup_url": "https://makersuite.google.com/app/apikey",
            "description": "Google's Gemini AI models with generous free tier.",
            "free_tier_info": "Free tier: 60 requests/minute, no billing required",
        },
        "huggingface": {
            "display_name": "HuggingFace",
            "provider_type": ProviderType.FREE,
            "env_var": "HUGGINGFACE_TOKEN",
            "endpoint": "https://api-inference.huggingface.co",
            "docs_url": "backend/docs/HUGGINGFACE_SETUP.md",
            "signup_url": "https://huggingface.co/settings/tokens",
            "description": "Open-source AI models via HuggingFace Inference API.",
            "free_tier_info": "Free tier: ~1000 requests/day",
        },
        "groq": {
            "display_name": "Groq",
            "provider_type": ProviderType.PAID,
            "env_var": "GROQ_API_KEY",
            "endpoint": "https://api.groq.com",
            "docs_url": "backend/docs/GROQ_SETUP.md",
            "signup_url": "https://console.groq.com",
            "description": "Ultra-fast inference with Groq's LPU technology.",
            "free_tier_info": "Free credits available on signup",
        },
        "together": {
            "display_name": "Together AI",
            "provider_type": ProviderType.PAID,
            "env_var": "TOGETHER_API_KEY",
            "endpoint": "https://api.together.xyz",
            "docs_url": "backend/docs/TOGETHER_SETUP.md",
            "signup_url": "https://api.together.xyz",
            "description": "Access to diverse open-source models.",
            "free_tier_info": "$25 free credits on signup",
        },
        "openrouter": {
            "display_name": "OpenRouter",
            "provider_type": ProviderType.PAID,
            "env_var": "OPENROUTER_API_KEY",
            "endpoint": "https://openrouter.ai/api/v1",
            "docs_url": "backend/docs/OPENROUTER_SETUP.md",
            "signup_url": "https://openrouter.ai",
            "description": "Unified access to multiple AI providers.",
            "free_tier_info": "$1-5 free credits on signup",
        },
        "openai": {
            "display_name": "OpenAI",
            "provider_type": ProviderType.PAID,
            "env_var": "OPENAI_API_KEY",
            "endpoint": "https://api.openai.com/v1",
            "docs_url": "backend/docs/OPENAI_SETUP.md",
            "signup_url": "https://platform.openai.com",
            "description": "GPT-3.5, GPT-4, and other OpenAI models.",
            "free_tier_info": "$5 free trial (requires payment method)",
        },
        "qwen": {
            "display_name": "Qwen (Alibaba Cloud)",
            "provider_type": ProviderType.PAID,
            "env_var": "QWEN_API_KEY",
            "endpoint": "https://dashscope.aliyuncs.com/api/v1",
            "docs_url": "backend/docs/QWEN_SETUP.md",
            "signup_url": "https://dashscope.aliyun.com",
            "description": "Alibaba's Qwen AI models.",
            "free_tier_info": "Free tier available in some regions",
        },
    }
    
    def __init__(self):
        """Initialize provider configuration."""
        self.providers: Dict[str, ProviderInfo] = {}
        self._load_configuration()
        self._validate_configuration()
    
    def _load_configuration(self) -> None:
        """Load provider configuration from environment variables."""
        logger.info("Loading AI provider configuration...")
        
        for provider_name, provider_data in self.PROVIDERS.items():
            # Get API key or endpoint from environment
            env_var = provider_data["env_var"]
            
            if provider_name == "ollama":
                # Ollama uses endpoint instead of API key
                endpoint_env = provider_data.get("endpoint_env", "OLLAMA_ENDPOINT")
                config_value = os.getenv(endpoint_env, provider_data.get("default_endpoint"))
                endpoint = config_value
            else:
                config_value = os.getenv(env_var)
                endpoint = provider_data.get("endpoint")
            
            is_configured = bool(config_value)
            
            # Create ProviderInfo object
            provider_info = ProviderInfo(
                name=provider_name,
                display_name=provider_data["display_name"],
                provider_type=provider_data["provider_type"],
                env_var=env_var,
                endpoint=endpoint,
                docs_url=provider_data["docs_url"],
                signup_url=provider_data["signup_url"],
                description=provider_data["description"],
                free_tier_info=provider_data.get("free_tier_info"),
                is_configured=is_configured,
                status=ProviderStatus.NOT_CONFIGURED if not is_configured else ProviderStatus.HEALTHY,
            )
            
            self.providers[provider_name] = provider_info
    
    def _validate_configuration(self) -> None:
        """Validate provider configuration and log status."""
        configured_providers = [p for p in self.providers.values() if p.is_configured]
        
        if not configured_providers:
            logger.warning("⚠️  NO AI PROVIDERS CONFIGURED!")
            logger.warning("   Please configure at least one provider in .env file")
            logger.warning("   See backend/.env.example for available providers")
            return
        
        logger.info(f"✓ Found {len(configured_providers)} configured provider(s)")
        
        # Log configured providers by type
        free_providers = [p for p in configured_providers if p.provider_type == ProviderType.FREE]
        paid_providers = [p for p in configured_providers if p.provider_type == ProviderType.PAID]
        local_providers = [p for p in configured_providers if p.provider_type == ProviderType.LOCAL]
        
        if free_providers:
            logger.info(f"  FREE providers: {', '.join(p.display_name for p in free_providers)}")
        if paid_providers:
            logger.info(f"  PAID providers: {', '.join(p.display_name for p in paid_providers)}")
        if local_providers:
            logger.info(f"  LOCAL providers: {', '.join(p.display_name for p in local_providers)}")
        
        # Log not configured providers
        not_configured = [p for p in self.providers.values() if not p.is_configured]
        if not_configured:
            logger.info(f"  Not configured: {', '.join(p.display_name for p in not_configured)}")
    
    def get_api_key(self, provider_name: str) -> Optional[str]:
        """Get API key for a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            API key if configured, None otherwise
        """
        provider = self.providers.get(provider_name)
        if not provider or not provider.is_configured:
            return None
        
        return os.getenv(provider.env_var)
    
    def get_endpoint(self, provider_name: str) -> Optional[str]:
        """Get endpoint URL for a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Endpoint URL if available, None otherwise
        """
        provider = self.providers.get(provider_name)
        if not provider:
            return None
        
        return provider.endpoint
    
    def is_provider_configured(self, provider_name: str) -> bool:
        """Check if a provider is configured.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            True if provider is configured, False otherwise
        """
        provider = self.providers.get(provider_name)
        return provider.is_configured if provider else False
    
    def get_configured_providers(self) -> List[str]:
        """Get list of configured provider names.
        
        Returns:
            List of provider names that are configured
        """
        return [name for name, info in self.providers.items() if info.is_configured]
    
    def get_available_providers(self) -> List[str]:
        """Get list of available (configured and healthy) provider names.
        
        Returns:
            List of provider names that are available
        """
        return [
            name for name, info in self.providers.items()
            if info.is_configured and info.status == ProviderStatus.HEALTHY
        ]
    
    def get_provider_info(self, provider_name: str) -> Optional[ProviderInfo]:
        """Get detailed information about a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            ProviderInfo object if provider exists, None otherwise
        """
        return self.providers.get(provider_name)
    
    def get_all_providers_info(self) -> Dict[str, ProviderInfo]:
        """Get information about all providers.
        
        Returns:
            Dictionary mapping provider names to ProviderInfo objects
        """
        return self.providers.copy()
    
    async def check_provider_health(self, provider_name: str) -> ProviderStatus:
        """Check health status of a specific provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            ProviderStatus enum value
        """
        provider = self.providers.get(provider_name)
        if not provider:
            return ProviderStatus.NOT_CONFIGURED
        
        if not provider.is_configured:
            return ProviderStatus.NOT_CONFIGURED
        
        try:
            # Perform lightweight health check
            if provider_name == "ollama":
                status = await self._check_ollama_health(provider)
            elif provider_name == "gemini":
                status = await self._check_gemini_health(provider)
            elif provider_name == "huggingface":
                status = await self._check_huggingface_health(provider)
            elif provider_name in ["groq", "together", "openrouter", "openai", "qwen"]:
                status = await self._check_generic_api_health(provider)
            else:
                status = ProviderStatus.HEALTHY  # Assume healthy if no specific check
            
            # Update provider status
            provider.status = status
            provider.last_health_check = datetime.utcnow()
            
            return status
            
        except Exception as e:
            logger.error(f"Health check failed for {provider_name}: {e}")
            provider.status = ProviderStatus.DOWN
            provider.last_health_check = datetime.utcnow()
            return ProviderStatus.DOWN
    
    async def _check_ollama_health(self, provider: ProviderInfo) -> ProviderStatus:
        """Check Ollama health by pinging the API."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{provider.endpoint}/api/tags")
                if response.status_code == 200:
                    return ProviderStatus.HEALTHY
                else:
                    return ProviderStatus.DEGRADED
        except Exception:
            return ProviderStatus.DOWN
    
    async def _check_gemini_health(self, provider: ProviderInfo) -> ProviderStatus:
        """Check Gemini health by validating API key format."""
        api_key = self.get_api_key(provider.name)
        if api_key and len(api_key) > 10:
            # Basic validation - actual health check would require a test request
            return ProviderStatus.HEALTHY
        return ProviderStatus.DOWN
    
    async def _check_huggingface_health(self, provider: ProviderInfo) -> ProviderStatus:
        """Check HuggingFace health by validating token format."""
        token = self.get_api_key(provider.name)
        if token and len(token) > 10:
            # Basic validation - actual health check would require a test request
            return ProviderStatus.HEALTHY
        return ProviderStatus.DOWN
    
    async def _check_generic_api_health(self, provider: ProviderInfo) -> ProviderStatus:
        """Generic health check for API-based providers."""
        api_key = self.get_api_key(provider.name)
        if api_key and len(api_key) > 10:
            # Basic validation - actual health check would require a test request
            return ProviderStatus.HEALTHY
        return ProviderStatus.DOWN
    
    async def check_all_providers_health(self) -> Dict[str, ProviderStatus]:
        """Check health status of all configured providers.
        
        Returns:
            Dictionary mapping provider names to their health status
        """
        health_status = {}
        
        for provider_name in self.get_configured_providers():
            status = await self.check_provider_health(provider_name)
            health_status[provider_name] = status
        
        return health_status
    
    def log_provider_summary(self) -> None:
        """Log a summary of all providers and their status."""
        logger.info("=" * 80)
        logger.info("AI PROVIDER CONFIGURATION SUMMARY")
        logger.info("=" * 80)
        
        for provider_name, provider in self.providers.items():
            status_icon = "✓" if provider.is_configured else "✗"
            type_label = f"[{provider.provider_type.value.upper()}]"
            
            logger.info(f"{status_icon} {provider.display_name} {type_label}")
            
            if provider.is_configured:
                logger.info(f"   Status: {provider.status.value}")
                if provider.last_health_check:
                    logger.info(f"   Last check: {provider.last_health_check.isoformat()}")
            else:
                logger.info(f"   Not configured - Set {provider.env_var} in .env")
                logger.info(f"   Get API key: {provider.signup_url}")
                if provider.free_tier_info:
                    logger.info(f"   {provider.free_tier_info}")
        
        logger.info("=" * 80)


# Global provider configuration instance
_provider_config: Optional[ProviderConfig] = None


def get_provider_config() -> ProviderConfig:
    """Get the global provider configuration instance.
    
    Returns:
        ProviderConfig singleton instance
    """
    global _provider_config
    if _provider_config is None:
        _provider_config = ProviderConfig()
    return _provider_config


def initialize_provider_config() -> ProviderConfig:
    """Initialize and return the provider configuration.
    
    This should be called on application startup.
    
    Returns:
        ProviderConfig instance
    """
    config = get_provider_config()
    config.log_provider_summary()
    return config
