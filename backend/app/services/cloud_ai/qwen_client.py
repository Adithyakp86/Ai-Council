"""Qwen (Alibaba Cloud) DashScope API client."""

import httpx
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class QwenClient:
    """Client for Qwen (Alibaba Cloud) DashScope API.
    
    Qwen is Alibaba Cloud's large language model series, offering competitive
    performance with free tier availability in some regions.
    
    API Documentation: https://help.aliyun.com/zh/dashscope/
    """
    
    BASE_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    
    def __init__(self, api_key: str):
        """Initialize Qwen client.
        
        Args:
            api_key: Qwen API key from https://dashscope.aliyun.com
        """
        self.api_key = api_key
        logger.info("Initialized Qwen client")
    
    def generate(self, prompt: str, model: str, **kwargs) -> str:
        """Generate response from Qwen API.
        
        Args:
            prompt: The input prompt
            model: Model identifier (e.g., 'qwen-turbo', 'qwen-plus', 'qwen-max')
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            str: The generated response text
            
        Raises:
            httpx.HTTPError: If the API request fails
        """
        try:
            # Prepare request payload
            payload = {
                "model": model,
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                },
                "parameters": {
                    "result_format": "message",
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.8),
                    "top_k": kwargs.get("top_k", 50),
                    "max_tokens": kwargs.get("max_tokens", 1500),
                    "enable_search": kwargs.get("enable_search", False),
                }
            }
            
            logger.debug(f"Sending request to Qwen: model={model}, prompt_length={len(prompt)}")
            
            # Make synchronous request
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    self.BASE_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                
                # Extract text from response
                if "output" in data and "choices" in data["output"]:
                    choices = data["output"]["choices"]
                    if len(choices) > 0 and "message" in choices[0]:
                        message = choices[0]["message"]
                        if "content" in message:
                            generated_text = message["content"]
                            logger.debug(f"Received response from Qwen: length={len(generated_text)}")
                            return generated_text
                
                # If we couldn't extract text, raise an error
                raise ValueError(f"Unexpected response format from Qwen: {data}")
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Qwen API error: {e.response.status_code} - {e.response.text}")
            
            if e.response.status_code == 400:
                error_data = e.response.json()
                error_message = error_data.get("message", "Bad request")
                raise ValueError(f"Qwen API error: {error_message}") from e
            elif e.response.status_code == 401:
                raise ValueError(
                    "Invalid Qwen API key. "
                    "Get a free API key at https://dashscope.aliyun.com"
                ) from e
            elif e.response.status_code == 429:
                raise ValueError(
                    "Qwen rate limit exceeded. "
                    "Please wait and try again."
                ) from e
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling Qwen: {e}")
            raise
    
    async def generate_async(self, prompt: str, model: str, **kwargs) -> str:
        """Generate response from Qwen API asynchronously.
        
        Args:
            prompt: The input prompt
            model: Model identifier
            **kwargs: Additional parameters
            
        Returns:
            str: The generated response text
        """
        try:
            payload = {
                "model": model,
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                },
                "parameters": {
                    "result_format": "message",
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.8),
                    "top_k": kwargs.get("top_k", 50),
                    "max_tokens": kwargs.get("max_tokens", 1500),
                    "enable_search": kwargs.get("enable_search", False),
                }
            }
            
            logger.debug(f"Sending async request to Qwen: model={model}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.BASE_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                
                data = response.json()
                
                if "output" in data and "choices" in data["output"]:
                    choices = data["output"]["choices"]
                    if len(choices) > 0 and "message" in choices[0]:
                        message = choices[0]["message"]
                        if "content" in message:
                            return message["content"]
                
                raise ValueError(f"Unexpected response format from Qwen: {data}")
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Qwen API error: {e.response.status_code}")
            
            if e.response.status_code == 401:
                raise ValueError("Invalid Qwen API key") from e
            elif e.response.status_code == 429:
                raise ValueError("Qwen rate limit exceeded") from e
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling Qwen: {e}")
            raise
    
    def health_check(self) -> Dict[str, any]:
        """Check if Qwen API is accessible and API key is valid.
        
        Returns:
            Dict with health status information
        """
        try:
            # Try a minimal request to check API key validity
            test_payload = {
                "model": "qwen-turbo",
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": "Hello"
                        }
                    ]
                },
                "parameters": {
                    "result_format": "message",
                    "max_tokens": 10,
                }
            }
            
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    self.BASE_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=test_payload,
                )
                response.raise_for_status()
                
                return {
                    "status": "healthy",
                    "provider": "qwen",
                    "models_available": ["qwen-turbo", "qwen-plus", "qwen-max"],
                    "note": "Free tier available in some regions"
                }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return {
                    "status": "error",
                    "provider": "qwen",
                    "error": "Invalid API key"
                }
            return {
                "status": "error",
                "provider": "qwen",
                "error": f"HTTP {e.response.status_code}"
            }
        except Exception as e:
            return {
                "status": "error",
                "provider": "qwen",
                "error": str(e)
            }
    
    def get_model_id(self) -> str:
        """Get identifier for this client.
        
        Returns:
            str: Client identifier
        """
        return "qwen"
