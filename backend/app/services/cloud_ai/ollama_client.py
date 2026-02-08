"""Ollama client for local development and testing."""

import httpx
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for Ollama local inference (for development/testing)."""
    
    def __init__(self, base_url: str = "http://localhost:11434", api_key: str = ""):
        """Initialize Ollama client.
        
        Args:
            base_url: Ollama server URL (default: http://localhost:11434)
            api_key: Not used for Ollama, kept for interface compatibility
        """
        self.base_url = base_url
        logger.info(f"Initialized Ollama client with base_url: {base_url}")
    
    def generate(self, prompt: str, model: str, **kwargs) -> str:
        """Generate response from Ollama API.
        
        Args:
            prompt: The input prompt
            model: Model identifier (e.g., 'llama2', 'mistral', 'codellama')
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            str: The generated response text
            
        Raises:
            httpx.HTTPError: If the API request fails
            ConnectionError: If Ollama server is not reachable
        """
        try:
            # Prepare request payload
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "num_predict": kwargs.get("max_tokens", 1000),
                }
            }
            
            logger.debug(f"Sending request to Ollama: model={model}, prompt_length={len(prompt)}")
            
            # Make synchronous request
            with httpx.Client(timeout=120.0) as client:
                response = client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                generated_text = data["response"]
                
                logger.debug(f"Received response from Ollama: length={len(generated_text)}")
                return generated_text
                
        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to Ollama at {self.base_url}: {e}")
            raise ConnectionError(
                f"Ollama server is not reachable at {self.base_url}. "
                "Please ensure Ollama is running. See backend/docs/OLLAMA_SETUP.md"
            ) from e
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama API error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 404:
                raise ValueError(
                    f"Model '{model}' not found. Please pull it first: ollama pull {model}"
                ) from e
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling Ollama: {e}")
            raise
    
    async def generate_async(self, prompt: str, model: str, **kwargs) -> str:
        """Generate response from Ollama API asynchronously.
        
        Args:
            prompt: The input prompt
            model: Model identifier
            **kwargs: Additional parameters
            
        Returns:
            str: The generated response text
            
        Raises:
            httpx.HTTPError: If the API request fails
            ConnectionError: If Ollama server is not reachable
        """
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "num_predict": kwargs.get("max_tokens", 1000),
                }
            }
            
            logger.debug(f"Sending async request to Ollama: model={model}")
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                
                data = response.json()
                return data["response"]
                
        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to Ollama at {self.base_url}: {e}")
            raise ConnectionError(
                f"Ollama server is not reachable at {self.base_url}. "
                "Please ensure Ollama is running."
            ) from e
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama API error: {e.response.status_code}")
            if e.response.status_code == 404:
                raise ValueError(f"Model '{model}' not found. Please pull it first.") from e
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling Ollama: {e}")
            raise
    
    def health_check(self) -> Dict[str, any]:
        """Check if Ollama server is healthy and responsive.
        
        Returns:
            Dict with health status information
        """
        try:
            with httpx.Client(timeout=5.0) as client:
                # Try to list models as a health check
                response = client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                
                data = response.json()
                models = data.get("models", [])
                
                return {
                    "status": "healthy",
                    "endpoint": self.base_url,
                    "models_available": len(models),
                    "model_names": [m.get("name") for m in models]
                }
        except httpx.ConnectError:
            return {
                "status": "down",
                "endpoint": self.base_url,
                "error": "Cannot connect to Ollama server"
            }
        except Exception as e:
            return {
                "status": "error",
                "endpoint": self.base_url,
                "error": str(e)
            }
    
    def list_models(self) -> List[str]:
        """List all available models in Ollama.
        
        Returns:
            List of model names
        """
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                
                data = response.json()
                models = data.get("models", [])
                return [m.get("name") for m in models]
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []
    
    def get_model_id(self) -> str:
        """Get identifier for this client.
        
        Returns:
            str: Client identifier
        """
        return "ollama"
