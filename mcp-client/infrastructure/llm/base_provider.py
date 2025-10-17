# infrastructure/llm/base_provider.py
"""
Base LLM Provider - Abstract base class for all LLM providers.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from core.models.conversation import Message
from core.models.llm_response import LLMResponse


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    All concrete providers (Claude, OpenAI, Gemini) must implement this interface.
    """
    
    def __init__(self, api_key: str, model_id: str):
        """
        Initialize provider with API key and model ID.
        
        Args:
            api_key: API key for the provider
            model_id: Model identifier (e.g., "claude-3-7-sonnet-20250219")
        """
        self.api_key = api_key
        self.model_id = model_id
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate provider configuration."""
        if not self.api_key:
            raise ValueError(f"{self.__class__.__name__}: API key is required")
        if not self.model_id:
            raise ValueError(f"{self.__class__.__name__}: Model ID is required")
    
    @abstractmethod
    async def process_messages(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 4096,
        temperature: float = 1.0
    ) -> LLMResponse:
        """
        Process messages and return LLM response.
        
        Args:
            messages: List of conversation messages
            tools: Optional list of available tools (MCP format)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 to 2.0)
            
        Returns:
            LLMResponse with text and optional tool calls
        """
        pass
    
    @abstractmethod
    def supports_tools(self) -> bool:
        """Check if provider supports tool/function calling."""
        pass
    
    def get_model_id(self) -> str:
        """Get current model identifier."""
        return self.model_id
    
    def set_model(self, model_id: str) -> bool:
        """
        Set model identifier.
        
        Args:
            model_id: New model identifier
            
        Returns:
            True if model was set successfully
        """
        if self._validate_model_id(model_id):
            self.model_id = model_id
            return True
        return False
    
    def _validate_model_id(self, model_id: str) -> bool:
        """
        Validate model ID for this provider.
        Override in subclasses for provider-specific validation.
        """
        return bool(model_id)
    
    def _convert_messages_to_provider_format(
        self, 
        messages: List[Message]
    ) -> List[Dict[str, Any]]:
        """
        Convert internal Message format to provider-specific format.
        Override in subclasses for provider-specific conversion.
        """
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
        ]