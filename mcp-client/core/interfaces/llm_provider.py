"""
LLM provider interfaces.

This module defines interfaces for LLM providers, allowing the application to
use different language model backends interchangeably.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

from core.models.conversation import Message
from core.models.llm_response import LLMResponse


class ILLMProvider(ABC):
    """
    Interface for LLM providers (Claude, OpenAI, etc).

    This interface defines the contract that all LLM providers must implement,
    allowing the application to switch between different providers without
    changing the client code.
    """

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from the LLM based on the provided messages.

        Args:
            messages: The conversation history to provide context to the LLM
            tools: Optional list of tools the LLM can use in its response
            model: Optional model identifier to use (defaults to provider's default)
            temperature: Controls randomness in the response (0.0-1.0)
            max_tokens: Optional maximum number of tokens in the response
            **kwargs: Additional provider-specific parameters

        Returns:
            An LLMResponse object containing the model's response
        """
        pass

    @abstractmethod
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get a list of available models from this provider.

        Returns:
            A list of dictionaries containing model information:
            - id: The model identifier used when calling the API
            - name: A human-readable name for the model
            - capabilities: List of capabilities (e.g., ["text", "tools", "vision"])
            - context_window: Maximum context length in tokens
            - additional provider-specific fields may be included
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of this provider.

        Returns:
            Provider name as a string (e.g., "claude", "openai", "gemini")
        """
        pass

    @abstractmethod
    async def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        Count the number of tokens in the given text for a specific model.

        Args:
            text: The text to count tokens for
            model: Optional model identifier (defaults to provider's default)

        Returns:
            The number of tokens in the text
        """
        pass