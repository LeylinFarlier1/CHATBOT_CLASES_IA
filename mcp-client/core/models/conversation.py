"""
Message and Conversation domain models.

These models represent the core entities for chat interactions:
- Message: A single message in a conversation (user or assistant)
- Conversation: A collection of messages forming a complete dialog
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from uuid import uuid4


@dataclass
class Message:
    """
    Represents a single message in a conversation.

    A message can be from a user or an assistant and can contain
    either text or structured content (like tool calls or results).
    """
    role: str  # "user" or "assistant"
    content: Union[str, List[Dict[str, Any]]]  # Text or structured content
    timestamp: datetime = None  # When the message was created

    def __post_init__(self):
        """Initialize default values after creation."""
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def is_text_only(self) -> bool:
        """Check if message contains only text content."""
        return isinstance(self.content, str)

    def has_tool_calls(self) -> bool:
        """Check if message contains tool calls."""
        if not isinstance(self.content, list):
            return False

        return any(
            isinstance(item, dict) and item.get("type") == "tool_use"
            for item in self.content
        )

    def has_tool_results(self) -> bool:
        """Check if message contains tool results."""
        if not isinstance(self.content, list):
            return False

        return any(
            isinstance(item, dict) and item.get("type") == "tool_result"
            for item in self.content
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format for storage/API."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create a Message from dictionary data."""
        timestamp = None
        if data.get("timestamp"):
            timestamp = (
                data["timestamp"]
                if isinstance(data["timestamp"], datetime)
                else datetime.fromisoformat(data["timestamp"])
            )

        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=timestamp
        )


@dataclass
class Conversation:
    """
    Represents a complete conversation between user and assistant.

    A conversation is a sequence of messages, with methods to
    manipulate and analyze the conversation history.
    """
    messages: List[Message] = field(default_factory=list)
    id: str = None
    created_at: datetime = None
    tools_used: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize default values after creation."""
        if self.id is None:
            self.id = str(uuid4())

        if self.created_at is None:
            self.created_at = datetime.now()

    def add_message(self, message: Message) -> None:
        """Add a new message to the conversation."""
        self.messages.append(message)

        # Track tools if it's a tool result message
        if message.has_tool_results() and isinstance(message.content, list):
            # Extract tool names from tool results
            for item in message.content:
                if isinstance(item, dict) and item.get("type") == "tool_result":
                    tool_name = item.get("name")
                    if tool_name and tool_name not in self.tools_used:
                        self.tools_used.append(tool_name)

    def add_user_message(self, content: str) -> Message:
        """Add a user message to the conversation."""
        message = Message(role="user", content=content)
        self.add_message(message)
        return message

    def add_assistant_message(self, content: Union[str, List[Dict[str, Any]]]) -> Message:
        """Add an assistant message to the conversation."""
        message = Message(role="assistant", content=content)
        self.add_message(message)
        return message

    def get_last_message(self) -> Optional[Message]:
        """Get the most recent message in the conversation."""
        if not self.messages:
            return None
        return self.messages[-1]

    def clear(self) -> None:
        """Clear all messages in the conversation."""
        self.messages.clear()
        self.tools_used.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary format for storage/API."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "messages": [msg.to_dict() for msg in self.messages],
            "tools_used": self.tools_used,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create a Conversation from dictionary data."""
        created_at = None
        if data.get("created_at"):
            created_at = (
                data["created_at"]
                if isinstance(data["created_at"], datetime)
                else datetime.fromisoformat(data["created_at"])
            )

        messages = [
            Message.from_dict(msg_data)
            for msg_data in data.get("messages", [])
        ]

        return cls(
            id=data.get("id"),
            created_at=created_at,
            messages=messages,
            tools_used=data.get("tools_used", []),
            metadata=data.get("metadata", {})
        )

    def to_anthropic_messages(self) -> List[Dict[str, Any]]:
        """
        Convert conversation to Anthropic's message format.

        Returns:
            List of messages in Anthropic API format
        """
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages
        ]

    def __len__(self) -> int:
        """Return the number of messages in the conversation."""
        return len(self.messages)

    def __getitem__(self, index: int) -> Message:
        """Get message by index."""
        return self.messages[index]