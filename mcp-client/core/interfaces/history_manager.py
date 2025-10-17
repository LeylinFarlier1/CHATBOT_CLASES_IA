"""
History manager interfaces.

This module defines interfaces for managing conversation history,
including storing, retrieving, and searching past interactions.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime


class IHistoryManager(ABC):
    """
    Interface for history managers.

    This interface defines the contract that history managers must implement,
    providing functionality for tracking and analyzing conversation history.
    """

    @abstractmethod
    async def add(
        self,
        query: str,
        response: str,
        conversation_id: Optional[str] = None,
        tools_used: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add an interaction to the history.

        Args:
            query: The user's query
            response: The LLM's response
            conversation_id: Optional ID of the conversation this interaction belongs to
            tools_used: Optional list of tools used in the response
            metadata: Optional additional metadata for the interaction

        Returns:
            The ID of the added history entry
        """
        pass

    @abstractmethod
    async def get_recent(
        self,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get recent interactions from the history.

        Args:
            limit: Maximum number of interactions to return
            offset: Number of interactions to skip

        Returns:
            A list of interaction dictionaries, each containing:
            - id: The interaction ID
            - query: The user's query
            - response: The LLM's response
            - timestamp: When the interaction occurred
            - conversation_id: The ID of the associated conversation
            - tools_used: List of tools used in the response
            - metadata: Additional metadata for the interaction
        """
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search interactions in the history.

        Args:
            query: Search query string
            limit: Maximum number of interactions to return
            offset: Number of interactions to skip

        Returns:
            A list of interaction dictionaries matching the search query
        """
        pass

    @abstractmethod
    async def get_by_conversation(
        self,
        conversation_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get interactions belonging to a specific conversation.

        Args:
            conversation_id: The ID of the conversation
            limit: Maximum number of interactions to return
            offset: Number of interactions to skip

        Returns:
            A list of interaction dictionaries belonging to the conversation
        """
        pass

    @abstractmethod
    async def delete(
        self,
        interaction_id: str
    ) -> bool:
        """
        Delete an interaction from the history.

        Args:
            interaction_id: The ID of the interaction to delete

        Returns:
            True if the interaction was deleted, False otherwise
        """
        pass

    @abstractmethod
    async def clear(
        self,
        before_date: Optional[datetime] = None
    ) -> int:
        """
        Clear the history, optionally up to a specified date.

        Args:
            before_date: Optional date to clear history before

        Returns:
            The number of interactions deleted
        """
        pass

    @abstractmethod
    async def get_stats(
        self
    ) -> Dict[str, Any]:
        """
        Get statistics about the history.

        Returns:
            A dictionary containing statistics:
            - total_interactions: Total number of interactions
            - unique_conversations: Number of unique conversations
            - tools_usage: Dictionary mapping tool names to usage counts
            - provider_usage: Dictionary mapping provider names to usage counts
            - average_tokens: Average number of tokens per interaction
            - time_period: Dictionary with first and last interaction timestamps
        """
        pass