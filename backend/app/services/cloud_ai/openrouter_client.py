"""OpenRouter API client for multi-provider access."""

import httpx
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """Client for OpenRouter API (multi-provider access)."""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self, api_key: str):
        """Initialize OpenRouter client.
        
        Args:
            api_key: OpenRouter API key for authentication
        """
        self.api_key = api_key
    
    def generate(self, prompt: str, model: str, **kwargs) -> str:
        """Generate response from OpenRouter API.
        
        Args:
            prompt: The input prompt
            model: Model identifier (e.g., 'anthropic/claude-3-sonnet', 'openai/gpt-4-turbo')
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            str: The generated response text
            
        Raises:
            httpx.HTTPError: If the API request fails
        """
        # Prepare messages in chat format
        messages = [{"role": "user", "content": prompt}]
        
        # Prepare request payload
        payload = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
        }
        
        # Make synchronous request with required headers
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{self.BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://aicouncil.app",
                    "X-Title": "AI Council",
                },
                json=payload,
            )
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def generate_async(self, prompt: str, model: str, **kwargs) -> str:
        """Generate response from OpenRouter API asynchronously.
        
        Args:
            prompt: The input prompt
            model: Model identifier
            **kwargs: Additional parameters
            
        Returns:
            str: The generated response text
        """
        messages = [{"role": "user", "content": prompt}]
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://aicouncil.app",
                    "X-Title": "AI Council",
                },
                json=payload,
            )
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"]

    def health_check(self) -> Dict[str, any]:
        """Check if OpenRouter API is accessible and API key is valid.
        
        Returns:
            Dict with health status information
        """
        try:
            # Try a minimal request to check API key validity
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    f"{self.BASE_URL}/models",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "HTTP-Referer": "https://aicouncil.app",
                        "X-Title": "AI Council",
                    },
                )
                response.raise_for_status()
                
                data = response.json()
                models = data.get("data", [])
                
                return {
                    "status": "healthy",
                    "provider": "openrouter",
                    "models_available": len(models),
                    "note": "Multi-provider access (free credits on signup)"
                }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return {
                    "status": "error",
                    "provider": "openrouter",
                    "error": "Invalid API key"
                }
            return {
                "status": "error",
                "provider": "openrouter",
                "error": f"HTTP {e.response.status_code}"
            }
        except Exception as e:
            return {
                "status": "error",
                "provider": "openrouter",
                "error": str(e)
            }
    
    def get_model_id(self) -> str:
        """Get identifier for this client.
        
        Returns:
            str: Client identifier
        """
        return "openrouter"
