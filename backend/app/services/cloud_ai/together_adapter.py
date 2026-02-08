"""Together AI adapter for AI Council integration."""

from .adapter import CloudAIAdapter
from .together_client import TogetherClient


class TogetherAdapter(CloudAIAdapter):
    """Adapter for Together AI API that provides access to open-source models.
    
    Together AI offers high-performance inference for open-source models with generous
    free credits ($25 on signup) and competitive pricing for production use.
    
    Supported models:
    - togethercomputer/llama-2-70b-chat: Meta's powerful 70B parameter model
    - mistralai/Mixtral-8x7B-Instruct-v0.1: Mixtral's efficient mixture-of-experts model
    - NousResearch/Nous-Hermes-2-Yi-34B: High-quality 34B parameter instruction-tuned model
    
    Features:
    - Fast inference with optimized infrastructure
    - Generous free credits for prototyping ($25 on signup)
    - Support for latest open-source models
    - Competitive pricing for production workloads
    - Simple REST API with streaming support
    
    Pricing (as of 2024):
    - Llama-2-70B: ~$0.90 per 1M tokens
    - Mixtral-8x7B: ~$0.60 per 1M tokens
    - Nous-Hermes-2-Yi-34B: ~$0.80 per 1M tokens
    """
    
    def __init__(self, model_id: str, api_key: str):
        """Initialize Together AI adapter.
        
        Args:
            model_id: Model identifier (e.g., 'mistralai/Mixtral-8x7B-Instruct-v0.1')
            api_key: Together AI API key from https://api.together.xyz
        """
        super().__init__(
            provider='together',
            model_id=model_id,
            api_key=api_key
        )
    
    def _create_client(self):
        """Create Together AI client instance.
        
        Returns:
            TogetherClient: Configured client for API calls
        """
        return TogetherClient(api_key=self.api_key)
