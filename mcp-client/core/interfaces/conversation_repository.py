"""
Conversation repository interfaces.

This module defines interfaces for conversation storage and retrieval,
allowing the application to use different storage backends.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime

from core.models.conversation import Conversation


class IConversationRepository(ABC):
    """
    Interface for conversation repositories.

    This interface defines the contract that conversation repositories must implement,
    allowing the application to use different storage backends (file-based, database, etc.)
    interchangeably.
    """

    @abstractmethod
    async def save(self, conversation: Conversation) -> str:
        """
        Save a conversation to the repository.

        Args:
            conversation: The conversation to save

        Returns:
            The ID of the saved conversation
        """
        pass

    @abstractmethod
    async def get(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a conversation by its ID.

        Args:
            conversation_id: The ID of the conversation to retrieve

        Returns:
            The conversation if found, None otherwise
        """
        pass

    @abstractmethod
    async def list(
        self,
        limit: int = 10,
        offset: int = 0,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        List conversations in the repository.

        Args:
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip
            from_date: Optional start date for filtering
            to_date: Optional end date for filtering

        Returns:
            A list of conversation metadata dictionaries, each containing:
            - id: The conversation ID
            - created_at: When the conversation was created
            - updated_at: When the conversation was last updated
            - summary: Optional summary of the conversation
            - message_count: Number of messages in the conversation
            - metadata: Any additional metadata stored with the conversation
        """
        pass

    @abstractmethod
    async def delete(self, conversation_id: str) -> bool:
        """
        Delete a conversation from the repository.

        Args:
            conversation_id: The ID of the conversation to delete

        Returns:
            True if the conversation was deleted, False otherwise
        """
        pass

    @abstractmethod
    async def update(self, conversation: Conversation) -> bool:
        """
        Update a conversation in the repository.

        Args:
            conversation: The conversation with updated content

        Returns:
            True if the conversation was updated, False otherwise
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
        Search conversations by content.

        Args:
            query: Search query string
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            A list of conversation metadata dictionaries matching the search query
        """
        pass