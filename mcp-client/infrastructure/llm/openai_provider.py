# infrastructure/llm/openai_provider.py
"""
OpenAI LLM Provider (GPT-4, GPT-4o, etc.).
Extracted from tui_app.py lines 1072-1204.
"""
from openai import OpenAI
from typing import List, Dict, Any, Optional
import json

from infrastructure.llm.base_provider import BaseLLMProvider
from core.models.conversation import Message
from core.models.llm_response import LLMResponse
from core.models.tool_result import ToolCall


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM Provider implementation."""
    
    # Supported OpenAI models
    SUPPORTED_MODELS = {
        "gpt-4o": "GPT-4o (Omni)",
        "gpt-4o-mini": "GPT-4o Mini",
        "gpt-4-turbo": "GPT-4 Turbo",
        "gpt-4": "GPT-4",
        "gpt-3.5-turbo": "GPT-3.5 Turbo",
    }
    
    def __init__(self, api_key: str, model_id: str = "gpt-4o"):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            model_id: OpenAI model identifier
        """
        super().__init__(api_key, model_id)
        self.client = OpenAI(api_key=api_key)
    
    def _validate_model_id(self, model_id: str) -> bool:
        """Validate OpenAI model ID."""
        return model_id in self.SUPPORTED_MODELS
    
    async def process_messages(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 4096,
        temperature: float = 1.0
    ) -> LLMResponse:
        """
        Process messages with OpenAI API.
        
        Extracted logic from tui_app.py _process_with_openai method.
        """
        # Convert messages to OpenAI format
        openai_messages = self._convert_to_openai_format(messages)
        
        # Prepare API call parameters
        api_params = {
            "model": self.model_id,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": openai_messages,
        }
        
        # Add tools if provided (convert to OpenAI function format)
        if tools:
            api_params["tools"] = self._convert_tools_to_openai_format(tools)
        
        # Call OpenAI API
        response = self.client.chat.completions.create(**api_params)
        
        # Parse response
        return self._parse_openai_response(response)
    
    def supports_tools(self) -> bool:
        """OpenAI supports function calling."""
        return True
    
    def _convert_to_openai_format(
        self, 
        messages: List[Message]
    ) -> List[Dict[str, Any]]:
        """
        Convert internal Message format to OpenAI API format.
        """
        openai_messages = []
        
        for msg in messages:
            if isinstance(msg.content, str):
                openai_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            elif isinstance(msg.content, list):
                # Handle structured content (tool results)
                # OpenAI expects specific format for tool results
                openai_messages.append({
                    "role": msg.role,
                    "content": self._format_structured_content(msg.content)
                })
            else:
                openai_messages.append({
                    "role": msg.role,
                    "content": str(msg.content)
                })
        
        return openai_messages
    
    def _format_structured_content(self, content: List[Dict]) -> str:
        """Format structured content for OpenAI."""
        # Simple implementation: concatenate text from all blocks
        text_parts = []
        for block in content:
            if isinstance(block, dict):
                if "text" in block:
                    text_parts.append(block["text"])
                elif "tool_result" in block:
                    text_parts.append(str(block["tool_result"]))
        return "\n".join(text_parts)
    
    def _convert_tools_to_openai_format(
        self, 
        tools: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Convert MCP tools format to OpenAI functions format.
        
        MCP format: {name, description, input_schema}
        OpenAI format: {type: "function", function: {name, description, parameters}}
        """
        openai_tools = []
        
        for tool in tools:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("input_schema", {})
                }
            }
            openai_tools.append(openai_tool)
        
        return openai_tools
    
    def _parse_openai_response(self, response) -> LLMResponse:
        """
        Parse OpenAI API response to internal LLMResponse format.
        """
        message = response.choices[0].message
        
        # Extract text content
        text_content = message.content or ""
        
        # Extract tool calls if present
        tool_calls = []
        if message.tool_calls:
            for tc in message.tool_calls:
                tool_call = ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments)
                )
                tool_calls.append(tool_call)
        
        return LLMResponse(
            text=text_content,
            tool_calls=tool_calls if tool_calls else None,
            raw_response=response,
            stop_reason=response.choices[0].finish_reason,
            usage={
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        )
    
    @classmethod
    def list_available_models(cls) -> Dict[str, str]:
        """List all available OpenAI models."""
        return cls.SUPPORTED_MODELS.copy()