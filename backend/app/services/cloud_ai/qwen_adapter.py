"""Qwen (Alibaba Cloud) adapter for AI Council integration."""

from .adapter import CloudAIAdapter
from .qwen_client import QwenClient


class QwenAdapter(CloudAIAdapter):
    """Adapter for Qwen (Alibaba Cloud) DashScope API.
    
    Qwen is Alibaba Cloud's large language model series, offering competitive
    performance with multilingual capabilities and strong reasoning abilities.
    
    Supported models:
    - qwen-turbo: Fast and cost-effective for most tasks
    - qwen-plus: Balanced performance and cost
    - qwen-max: Most capable model with superior reasoning
    
    Features:
    - Strong multilingual support (especially Chinese and English)
    - Competitive reasoning and generation capabilities
    - Free tier available in some regions
    - Fast response times
    - Support for web search integration
    
    Pricing (varies by region):
    - Qwen-Turbo: ~$0.002 per 1K tokens
    - Qwen-Plus: ~$0.004 per 1K tokens
    - Qwen-Max: ~$0.012 per 1K tokens
    
    Note: This is an optional integration. Free tier availability varies by region.
    Check https://dashscope.aliyun.com for current pricing and availability.
    """
    
    def __init__(self, model_id: str, api_key: str):
        """Initialize Qwen adapter.
        
        Args:
            model_id: Model identifier (e.g., 'qwen-turbo', 'qwen-plus', 'qwen-max')
            api_key: Qwen API key from https://dashscope.aliyun.com
        """
        super().__init__(
            provider='qwen',
            model_id=model_id,
            api_key=api_key
        )
    
    def _create_client(self):
        """Create Qwen client instance.
        
        Returns:
            QwenClient: Configured client for API calls
        """
        return QwenClient(api_key=self.api_key)
