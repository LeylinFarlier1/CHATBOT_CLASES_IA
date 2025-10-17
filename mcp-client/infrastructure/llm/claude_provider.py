"""
Claude (Anthropic) LLM Provider.
Extracted from tui_app.py lines 942-1070.
"""
from anthropic import Anthropic
from typing import List, Dict, Any, Optional
import json

from infrastructure.llm.base_provider import BaseLLMProvider
from core.models.conversation import Message
from core.models.llm_response import LLMResponse
from core.models.tool_result import ToolCall


class ClaudeProvider(BaseLLMProvider):
    """Claude (Anthropic) LLM Provider implementation."""
    
    # Supported Claude models
    SUPPORTED_MODELS = {
        "claude-3-7-sonnet-20250219": "Claude 3.7 Sonnet",
        "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet",
        "claude-3-5-haiku-20241022": "Claude 3.5 Haiku",
        "claude-3-opus-20240229": "Claude 3 Opus",
    }
    
    def __init__(self, api_key: str, model_id: str = "claude-3-7-sonnet-20250219"):
        """
        Initialize Claude provider.
        
        Args:
            api_key: Anthropic API key
            model_id: Claude model identifier
        """
        super().__init__(api_key, model_id)
        self.client = Anthropic(api_key=api_key)
    
    def _validate_model_id(self, model_id: str) -> bool:
        """Validate Claude model ID."""
        return model_id in self.SUPPORTED_MODELS
    
    async def process_messages(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 4096,
        temperature: float = 1.0
    ) -> LLMResponse:
        """
        Process messages with Claude API.
        
        Extracted logic from tui_app.py _process_with_claude method.
        """
        # Convert messages to Anthropic format
        anthropic_messages = self._convert_to_anthropic_format(messages)
        
        # Prepare API call parameters
        api_params = {
            "model": self.model_id,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": anthropic_messages,
        }
        
        # Add tools if provided
        if tools:
            api_params["tools"] = tools
        
        # Call Anthropic API
        response = self.client.messages.create(**api_params)
        
        # Parse response
        return self._parse_anthropic_response(response)
    
    def supports_tools(self) -> bool:
        """Claude supports tool calling."""
        return True
    
    def _convert_to_anthropic_format(
        self, 
        messages: List[Message]
    ) -> List[Dict[str, Any]]:
        """
        Convert internal Message format to Anthropic API format.
        
        Handles both text content and structured content with tool results.
        """
        anthropic_messages = []
        
        for msg in messages:
            if isinstance(msg.content, str):
                # Simple text message
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            elif isinstance(msg.content, list):
                # Structured content (e.g., tool results)
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            else:
                # Fallback: convert to string
                anthropic_messages.append({
                    "role": msg.role,
                    "content": str(msg.content)
                })
        
        return anthropic_messages
    
    def _parse_anthropic_response(self, response) -> LLMResponse:
        """
        Parse Anthropic API response to internal LLMResponse format.
        
        Extracted from tui_app.py lines 963-1020.
        """
        # Extract text content and tool calls
        text_contents = []
        tool_calls = []
        
        for block in response.content:
            if block.type == "text":
                from core.models.llm_response import TextContent
                text_contents.append(TextContent(text=block.text))
            elif block.type == "tool_use":
                # Parse tool call
                tool_call = ToolCall(
                    id=block.id,
                    name=block.name,
                    arguments=block.input
                )
                tool_calls.append(tool_call)
        
        return LLMResponse(
            text_contents=text_contents,
            tool_calls=tool_calls if tool_calls else [],
            provider="claude",
            model=self.model_id
        )
    
    @classmethod
    def list_available_models(cls) -> Dict[str, str]:
        """List all available Claude models."""
        return cls.SUPPORTED_MODELS.copy()
