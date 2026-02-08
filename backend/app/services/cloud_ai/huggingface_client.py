"""HuggingFace Inference API client."""

import httpx
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class HuggingFaceClient:
    """Client for HuggingFace Inference API."""
    
    BASE_URL = "https://api-inference.huggingface.co/models"
    
    def __init__(self, api_key: str):
        """Initialize HuggingFace client.
        
        Args:
            api_key: HuggingFace API key for authentication
        """
        self.api_key = api_key
        logger.info("Initialized HuggingFace client")
    
    def generate(self, prompt: str, model: str, **kwargs) -> str:
        """Generate response from HuggingFace Inference API.
        
        Args:
            prompt: The input prompt
            model: Model identifier (e.g., 'mistralai/Mistral-7B-Instruct-v0.2')
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            str: The generated response text
            
        Raises:
            httpx.HTTPError: If the API request fails
        """
        try:
            # Prepare request payload
            payload = {
                "inputs": prompt,
                "parameters": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_new_tokens": kwargs.get("max_tokens", 1000),
                    "top_p": kwargs.get("top_p", 0.9),
                    "do_sample": True,
                }
            }
            
            logger.debug(f"Sending request to HuggingFace: model={model}, prompt_length={len(prompt)}")
            
            # Make synchronous request
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.BASE_URL}/{model}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                
                # HuggingFace returns array of results
                if isinstance(data, list) and len(data) > 0:
                    generated_text = data[0]["generated_text"]
                    logger.debug(f"Received response from HuggingFace: length={len(generated_text)}")
                    return generated_text
                else:
                    raise ValueError(f"Unexpected response format: {data}")
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"HuggingFace API error: {e.response.status_code} - {e.response.text}")
            
            if e.response.status_code == 401:
                raise ValueError(
                    "Invalid HuggingFace API token. "
                    "Get a free token at https://huggingface.co/settings/tokens"
                ) from e
            elif e.response.status_code == 429:
                raise ValueError(
                    "HuggingFace rate limit exceeded (~1000 requests/day on free tier). "
                    "Please wait and try again."
                ) from e
            elif e.response.status_code == 503:
                # Model is loading
                error_data = e.response.json()
                if "estimated_time" in error_data:
                    wait_time = error_data["estimated_time"]
                    raise ValueError(
                        f"Model is loading. Please wait {wait_time:.1f} seconds and try again."
                    ) from e
                raise ValueError("Model is currently loading. Please try again in a moment.") from e
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling HuggingFace: {e}")
            raise
    
    async def generate_async(self, prompt: str, model: str, **kwargs) -> str:
        """Generate response from HuggingFace Inference API asynchronously.
        
        Args:
            prompt: The input prompt
            model: Model identifier
            **kwargs: Additional parameters
            
        Returns:
            str: The generated response text
        """
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_new_tokens": kwargs.get("max_tokens", 1000),
                    "top_p": kwargs.get("top_p", 0.9),
                    "do_sample": True,
                }
            }
            
            logger.debug(f"Sending async request to HuggingFace: model={model}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/{model}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    return data[0]["generated_text"]
                else:
                    raise ValueError(f"Unexpected response format: {data}")
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"HuggingFace API error: {e.response.status_code}")
            
            if e.response.status_code == 401:
                raise ValueError("Invalid HuggingFace API token") from e
            elif e.response.status_code == 429:
                raise ValueError("HuggingFace rate limit exceeded") from e
            elif e.response.status_code == 503:
                raise ValueError("Model is loading. Please try again in a moment.") from e
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling HuggingFace: {e}")
            raise
    
    def health_check(self) -> Dict[str, any]:
        """Check if HuggingFace API is accessible and API token is valid.
        
        Returns:
            Dict with health status information
        """
        try:
            # Try a minimal request to check API token validity
            # Use a small, fast model for health check
            test_model = "gpt2"
            
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    f"{self.BASE_URL}/{test_model}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "inputs": "test",
                        "parameters": {"max_new_tokens": 5}
                    },
                )
                response.raise_for_status()
                
                return {
                    "status": "healthy",
                    "provider": "huggingface",
                    "rate_limit": "~1000 requests/day (free tier)"
                }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return {
                    "status": "error",
                    "provider": "huggingface",
                    "error": "Invalid API token"
                }
            return {
                "status": "error",
                "provider": "huggingface",
                "error": f"HTTP {e.response.status_code}"
            }
        except Exception as e:
            return {
                "status": "error",
                "provider": "huggingface",
                "error": str(e)
            }
    
    def get_model_id(self) -> str:
        """Get identifier for this client.
        
        Returns:
            str: Client identifier
        """
        return "huggingface"
