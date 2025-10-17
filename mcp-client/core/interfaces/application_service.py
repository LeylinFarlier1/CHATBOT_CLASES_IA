"""
Application service interfaces.

This module defines interfaces for application services, which orchestrate
the flow of data between the user interface and the domain model.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple

from core.models.conversation import Conversation, Message
from core.models.llm_response import LLMResponse
from core.models.tool_result import ToolCall, ToolResult


class IApplicationService(ABC):
    """
    Interface for the main application service.

    This interface defines the high-level operations of the application,
    orchestrating the flow between the user interface, LLM providers,
    and MCP clients.
    """

    @abstractmethod
    async def send_message(
        self,
        text: str,
        conversation_id: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> Tuple[LLMResponse, Conversation]:
        """
        Send a user message and get an LLM response.

        Args:
            text: The user message text
            conversation_id: Optional ID of an existing conversation to continue
            model: Optional model to use for this specific request
            provider: Optional provider to use for this specific request
            system_prompt: Optional system prompt to override the default
            stream: Whether to stream the response

        Returns:
            A tuple containing:
            - The LLM response
            - The updated conversation
        """
        pass

    @abstractmethod
    async def execute_tool_call(
        self,
        tool_call: ToolCall,
        conversation_id: Optional[str] = None
    ) -> Tuple[ToolResult, Conversation]:
        """
        Execute a tool call and update the conversation history.

        Args:
            tool_call: The tool call to execute
            conversation_id: Optional ID of an existing conversation to update

        Returns:
            A tuple containing:
            - The tool result
            - The updated conversation
        """
        pass

    @abstractmethod
    async def execute_tool_calls_batch(
        self,
        tool_calls: List[ToolCall],
        conversation_id: Optional[str] = None
    ) -> Tuple[List[ToolResult], Conversation]:
        """
        Execute multiple tool calls in batch and update the conversation history.

        Args:
            tool_calls: The tool calls to execute
            conversation_id: Optional ID of an existing conversation to update

        Returns:
            A tuple containing:
            - The list of tool results
            - The updated conversation
        """
        pass

    @abstractmethod
    async def get_conversation(
        self,
        conversation_id: str
    ) -> Optional[Conversation]:
        """
        Get a conversation by its ID.

        Args:
            conversation_id: The ID of the conversation to retrieve

        Returns:
            The conversation if found, None otherwise
        """
        pass

    @abstractmethod
    async def list_conversations(
        self,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List available conversations.

        Args:
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip

        Returns:
            A list of conversation metadata dictionaries
        """
        pass

    @abstractmethod
    async def delete_conversation(
        self,
        conversation_id: str
    ) -> bool:
        """
        Delete a conversation.

        Args:
            conversation_id: The ID of the conversation to delete

        Returns:
            True if the conversation was deleted, False otherwise
        """
        pass

    @abstractmethod
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get a list of available MCP tools.

        Returns:
            A list of tool definitions
        """
        pass

    @abstractmethod
    async def get_available_models(
        self,
        provider: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get a list of available LLM models.

        Args:
            provider: Optional provider to filter models by

        Returns:
            A list of model definitions
        """
        pass

    @abstractmethod
    async def set_default_model(
        self,
        model_id: str,
        provider: Optional[str] = None
    ) -> bool:
        """
        Set the default model to use for responses.

        Args:
            model_id: The ID of the model to use as default
            provider: Optional provider of the model

        Returns:
            True if the default model was set, False otherwise
        """
        pass

    @abstractmethod
    async def set_default_provider(
        self,
        provider: str
    ) -> bool:
        """
        Set the default provider to use for responses.

        Args:
            provider: The provider to use as default

        Returns:
            True if the default provider was set, False otherwise
        """
        pass

    @abstractmethod
    async def create_new_conversation(self) -> Conversation:
        """
        Create a new empty conversation.

        Returns:
            The newly created conversation
        """
        pass