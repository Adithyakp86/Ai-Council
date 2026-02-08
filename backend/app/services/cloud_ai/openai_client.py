"""OpenAI API client."""

import httpx
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Client for OpenAI API.
    
    OpenAI provides industry-leading language models including GPT-3.5 and GPT-4.
    Requires payment method but includes $5 free trial credits.
    
    Pricing (as of 2024):
    - GPT-3.5-Turbo: $0.50/$1.50 per 1M tokens (input/output)
    - GPT-4: $30/$60 per 1M tokens (input/output)
    - GPT-4-Turbo: $10/$30 per 1M tokens (input/output)
    """
    
    BASE_URL = "https://api.openai.com/v1"
    
    def __init__(self, api_key: str):
        """Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key from https://platform.openai.com
        """
        self.api_key = api_key
        logger.info("Initialized OpenAI client")
    
    def generate(self, prompt: str, model: str, **kwargs) -> str:
        """Generate response from OpenAI API.
        
        Args:
            prompt: The input prompt
            model: Model identifier (e.g., 'gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo-preview')
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            str: The generated response text
            
        Raises:
            httpx.HTTPError: If the API request fails
        """
        try:
            # Prepare messages in chat format
            messages = [{"role": "user", "content": prompt}]
            
            # Prepare request payload
            payload = {
                "model": model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 1000),
                "top_p": kwargs.get("top_p", 1.0),
                "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
                "presence_penalty": kwargs.get("presence_penalty", 0.0),
            }
            
            logger.debug(f"Sending request to OpenAI: model={model}, prompt_length={len(prompt)}")
            
            # Make synchronous request
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                generated_text = data["choices"][0]["message"]["content"]
                
                logger.debug(f"Received response from OpenAI: length={len(generated_text)}")
                return generated_text
                
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenAI API error: {e.response.status_code} - {e.response.text}")
            
            if e.response.status_code == 401:
                raise ValueError(
                    "Invalid OpenAI API key. "
                    "Get your API key at https://platform.openai.com/api-keys"
                ) from e
            elif e.response.status_code == 429:
                error_data = e.response.json()
                error_message = error_data.get("error", {}).get("message", "Rate limit exceeded")
                raise ValueError(f"OpenAI rate limit exceeded: {error_message}") from e
            elif e.response.status_code == 400:
                error_data = e.response.json()
                error_message = error_data.get("error", {}).get("message", "Bad request")
                raise ValueError(f"OpenAI API error: {error_message}") from e
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling OpenAI: {e}")
            raise
    
    async def generate_async(self, prompt: str, model: str, **kwargs) -> str:
        """Generate response from OpenAI API asynchronously.
        
        Args:
            prompt: The input prompt
            model: Model identifier
            **kwargs: Additional parameters
            
        Returns:
            str: The generated response text
        """
        try:
            messages = [{"role": "user", "content": prompt}]
            
            payload = {
                "model": model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 1000),
                "top_p": kwargs.get("top_p", 1.0),
                "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
                "presence_penalty": kwargs.get("presence_penalty", 0.0),
            }
            
            logger.debug(f"Sending async request to OpenAI: model={model}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                
                data = response.json()
                return data["choices"][0]["message"]["content"]
                
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenAI API error: {e.response.status_code}")
            
            if e.response.status_code == 401:
                raise ValueError("Invalid OpenAI API key") from e
            elif e.response.status_code == 429:
                raise ValueError("OpenAI rate limit exceeded") from e
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling OpenAI: {e}")
            raise
    
    def health_check(self) -> Dict[str, any]:
        """Check if OpenAI API is accessible and API key is valid.
        
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
                    },
                )
                response.raise_for_status()
                
                data = response.json()
                models = data.get("data", [])
                
                return {
                    "status": "healthy",
                    "provider": "openai",
                    "models_available": len(models),
                    "note": "Requires payment method ($5 free trial)"
                }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return {
                    "status": "error",
                    "provider": "openai",
                    "error": "Invalid API key"
                }
            return {
                "status": "error",
                "provider": "openai",
                "error": f"HTTP {e.response.status_code}"
            }
        except Exception as e:
            return {
                "status": "error",
                "provider": "openai",
                "error": str(e)
            }
    
    def get_model_id(self) -> str:
        """Get identifier for this client.
        
        Returns:
            str: Client identifier
        """
        return "openai"
