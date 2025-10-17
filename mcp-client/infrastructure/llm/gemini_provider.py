# infrastructure/llm/gemini_provider.py
"""
Google Gemini LLM Provider.
"""
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import json

from infrastructure.llm.base_provider import BaseLLMProvider
from core.models.conversation import Message
from core.models.llm_response import LLMResponse
from core.models.tool_result import ToolCall


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM Provider implementation."""
    
    # Supported Gemini models
    SUPPORTED_MODELS = {
        "gemini-2.0-flash-exp": "Gemini 2.0 Flash (Experimental)",
        "gemini-1.5-pro": "Gemini 1.5 Pro",
        "gemini-1.5-flash": "Gemini 1.5 Flash",
    }
    
    def __init__(self, api_key: str, model_id: str = "gemini-2.0-flash-exp"):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Google API key
            model_id: Gemini model identifier
        """
        super().__init__(api_key, model_id)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_id)
    
    def _validate_model_id(self, model_id: str) -> bool:
        """Validate Gemini model ID."""
        return model_id in self.SUPPORTED_MODELS
    
    async def process_messages(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 4096,
        temperature: float = 1.0
    ) -> LLMResponse:
        """
        Process messages with Gemini API.
        """
        # Convert messages to Gemini format
        gemini_messages = self._convert_to_gemini_format(messages)
        
        # Prepare generation config
        generation_config = {
            "max_output_tokens": max_tokens,
            "temperature": temperature,
        }
        
        # Start chat session
        chat = self.model.start_chat(history=gemini_messages[:-1])
        
        # Send last message
        last_message = gemini_messages[-1]["parts"][0]
        response = chat.send_message(last_message, generation_config=generation_config)
        
        # Parse response
        return self._parse_gemini_response(response)
    
    def supports_tools(self) -> bool:
        """Gemini supports function calling (limited)."""
        return True
    
    def _convert_to_gemini_format(
        self, 
        messages: List[Message]
    ) -> List[Dict[str, Any]]:
        """
        Convert internal Message format to Gemini API format.
        """
        gemini_messages = []
        
        for msg in messages:
            role = "user" if msg.role == "user" else "model"
            
            if isinstance(msg.content, str):
                gemini_messages.append({
                    "role": role,
                    "parts": [msg.content]
                })
            else:
                gemini_messages.append({
                    "role": role,
                    "parts": [str(msg.content)]
                })
        
        return gemini_messages
    
    def _parse_gemini_response(self, response) -> LLMResponse:
        """
        Parse Gemini API response to internal LLMResponse format.
        """
        text_content = response.text
        
        # Gemini tool calling is more limited, placeholder for now
        tool_calls = None
        
        return LLMResponse(
            text=text_content,
            tool_calls=tool_calls,
            raw_response=response,
            stop_reason="stop",
            usage={
                "input_tokens": 0,  # Gemini doesn't provide this easily
                "output_tokens": 0,
            }
        )
    
    @classmethod
    def list_available_models(cls) -> Dict[str, str]:
        """List all available Gemini models."""
        return cls.SUPPORTED_MODELS.copy()