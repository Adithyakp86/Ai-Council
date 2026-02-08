"""OpenAI adapter for AI Council integration."""

from .adapter import CloudAIAdapter
from .openai_client import OpenAIClient


class OpenAIAdapter(CloudAIAdapter):
    """Adapter for OpenAI API that provides access to GPT models.
    
    OpenAI provides industry-leading language models with exceptional quality.
    Requires payment method but includes $5 free trial credits.
    
    Supported models:
    - gpt-3.5-turbo: Fast and cost-effective for most tasks
    - gpt-4: Most capable model with superior reasoning
    - gpt-4-turbo-preview: Latest GPT-4 with improved performance
    
    Features:
    - Industry-leading quality and reasoning capabilities
    - Reliable and well-documented API
    - Fast response times
    - Extensive context windows (up to 128K tokens)
    - Function calling and JSON mode support
    
    Pricing (as of 2024):
    - GPT-3.5-Turbo: $0.50/$1.50 per 1M tokens (input/output)
    - GPT-4: $30/$60 per 1M tokens (input/output)
    - GPT-4-Turbo: $10/$30 per 1M tokens (input/output)
    
    Note: This is an optional integration requiring payment method.
    Free trial includes $5 in credits.
    """
    
    def __init__(self, model_id: str, api_key: str):
        """Initialize OpenAI adapter.
        
        Args:
            model_id: Model identifier (e.g., 'gpt-3.5-turbo', 'gpt-4')
            api_key: OpenAI API key from https://platform.openai.com/api-keys
        """
        super().__init__(
            provider='openai',
            model_id=model_id,
            api_key=api_key
        )
    
    def _create_client(self):
        """Create OpenAI client instance.
        
        Returns:
            OpenAIClient: Configured client for API calls
        """
        return OpenAIClient(api_key=self.api_key)
