"""Google AI / Gemini API client."""

import httpx
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for Google AI / Gemini API."""
    
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    
    def __init__(self, api_key: str):
        """Initialize Gemini client.
        
        Args:
            api_key: Google AI API key from https://makersuite.google.com/app/apikey
        """
        self.api_key = api_key
        logger.info("Initialized Gemini client")
    
    def generate(self, prompt: str, model: str, **kwargs) -> str:
        """Generate response from Gemini API.
        
        Args:
            prompt: The input prompt
            model: Model identifier (e.g., 'gemini-pro', 'gemini-pro-vision')
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            str: The generated response text
            
        Raises:
            httpx.HTTPError: If the API request fails
        """
        try:
            # Prepare request payload
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "maxOutputTokens": kwargs.get("max_tokens", 1000),
                    "topP": kwargs.get("top_p", 0.95),
                    "topK": kwargs.get("top_k", 40),
                }
            }
            
            logger.debug(f"Sending request to Gemini: model={model}, prompt_length={len(prompt)}")
            
            # Make synchronous request
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.BASE_URL}/models/{model}:generateContent",
                    params={"key": self.api_key},
                    json=payload,
                )
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                
                # Extract text from response
                if "candidates" in data and len(data["candidates"]) > 0:
                    candidate = data["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        parts = candidate["content"]["parts"]
                        if len(parts) > 0 and "text" in parts[0]:
                            generated_text = parts[0]["text"]
                            logger.debug(f"Received response from Gemini: length={len(generated_text)}")
                            return generated_text
                
                # If we couldn't extract text, raise an error
                raise ValueError(f"Unexpected response format from Gemini: {data}")
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Gemini API error: {e.response.status_code} - {e.response.text}")
            
            if e.response.status_code == 400:
                error_data = e.response.json()
                error_message = error_data.get("error", {}).get("message", "Bad request")
                raise ValueError(f"Gemini API error: {error_message}") from e
            elif e.response.status_code == 403:
                raise ValueError(
                    "Invalid Gemini API key or quota exceeded. "
                    "Get a free API key at https://makersuite.google.com/app/apikey"
                ) from e
            elif e.response.status_code == 429:
                raise ValueError(
                    "Gemini rate limit exceeded (60 requests/minute on free tier). "
                    "Please wait and try again."
                ) from e
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling Gemini: {e}")
            raise
    
    async def generate_async(self, prompt: str, model: str, **kwargs) -> str:
        """Generate response from Gemini API asynchronously.
        
        Args:
            prompt: The input prompt
            model: Model identifier
            **kwargs: Additional parameters
            
        Returns:
            str: The generated response text
        """
        try:
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "maxOutputTokens": kwargs.get("max_tokens", 1000),
                    "topP": kwargs.get("top_p", 0.95),
                    "topK": kwargs.get("top_k", 40),
                }
            }
            
            logger.debug(f"Sending async request to Gemini: model={model}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/models/{model}:generateContent",
                    params={"key": self.api_key},
                    json=payload,
                )
                response.raise_for_status()
                
                data = response.json()
                
                if "candidates" in data and len(data["candidates"]) > 0:
                    candidate = data["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        parts = candidate["content"]["parts"]
                        if len(parts) > 0 and "text" in parts[0]:
                            return parts[0]["text"]
                
                raise ValueError(f"Unexpected response format from Gemini: {data}")
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Gemini API error: {e.response.status_code}")
            
            if e.response.status_code == 403:
                raise ValueError("Invalid Gemini API key or quota exceeded") from e
            elif e.response.status_code == 429:
                raise ValueError("Gemini rate limit exceeded") from e
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling Gemini: {e}")
            raise
    
    def health_check(self) -> Dict[str, any]:
        """Check if Gemini API is accessible and API key is valid.
        
        Returns:
            Dict with health status information
        """
        try:
            # Try a minimal request to check API key validity
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    f"{self.BASE_URL}/models",
                    params={"key": self.api_key},
                )
                response.raise_for_status()
                
                data = response.json()
                models = data.get("models", [])
                
                return {
                    "status": "healthy",
                    "provider": "gemini",
                    "models_available": len(models),
                    "rate_limit": "60 requests/minute (free tier)"
                }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                return {
                    "status": "error",
                    "provider": "gemini",
                    "error": "Invalid API key"
                }
            return {
                "status": "error",
                "provider": "gemini",
                "error": f"HTTP {e.response.status_code}"
            }
        except Exception as e:
            return {
                "status": "error",
                "provider": "gemini",
                "error": str(e)
            }
    
    def get_model_id(self) -> str:
        """Get identifier for this client.
        
        Returns:
            str: Client identifier
        """
        return "gemini"
