"""OpenRouter adapter for AI Council integration."""

from .adapter import CloudAIAdapter
from .openrouter_client import OpenRouterClient


class OpenRouterAdapter(CloudAIAdapter):
    """Adapter for OpenRouter API that provides access to multiple AI providers.
    
    OpenRouter provides unified access to models from OpenAI, Anthropic, Google, Meta, and more.
    It includes free credits on signup ($1-5) and provides transparent pricing.
    
    Supported models:
    - openai/gpt-3.5-turbo: Fast and cost-effective for most tasks
    - anthropic/claude-instant-1: Quick responses with good reasoning
    - meta-llama/llama-2-70b-chat: Open-source, powerful for research
    - google/palm-2-chat-bison: Google's conversational AI
    
    Features:
    - Unified API across multiple providers
    - Automatic fallback if primary model is unavailable
    - Transparent pricing and usage tracking
    - Free credits on signup for testing
    """
    
    def __init__(self, model_id: str, api_key: str):
        """Initialize OpenRouter adapter.
        
        Args:
            model_id: Model identifier (e.g., 'openai/gpt-3.5-turbo')
            api_key: OpenRouter API key
        """
        super().__init__(
            provider='openrouter',
            model_id=model_id,
            api_key=api_key
        )
    
    def _create_client(self):
        """Create OpenRouter client instance.
        
        Returns:
            OpenRouterClient: Configured client for API calls
        """
        return OpenRouterClient(api_key=self.api_key)
