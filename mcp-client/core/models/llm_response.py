"""
LLM response domain models.

These models represent the responses from LLM providers:
- LLMResponse: A generic response from an LLM
- TextContent: Text content in the response
- ToolCallContent: Tool call content in the response
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from uuid import uuid4

from core.models.tool_result import ToolCall


@dataclass
class TextContent:
    """
    Represents text content from an LLM response.
    """
    text: str
    content_type: str = "text"
    index: Optional[int] = None  # Position in the response

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for storage/API."""
        result = {
            "type": self.content_type,
            "text": self.text
        }

        if self.index is not None:
            result["index"] = self.index

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TextContent':
        """Create a TextContent from dictionary data."""
        return cls(
            text=data["text"],
            content_type=data.get("type", "text"),
            index=data.get("index")
        )


@dataclass
class LLMResponse:
    """
    Represents a complete response from an LLM.

    An LLM response can contain multiple content blocks, including
    text and tool calls. This class provides methods to extract and
    work with those content blocks.
    """
    text_contents: List[TextContent] = field(default_factory=list)
    tool_calls: List[ToolCall] = field(default_factory=list)
    provider: Optional[str] = None  # "claude", "openai", "gemini", etc.
    model: Optional[str] = None     # Specific model ID
    id: str = None
    timestamp: datetime = None
    raw_response: Any = None  # Original provider-specific response

    def __post_init__(self):
        """Initialize default values after creation."""
        if self.id is None:
            self.id = str(uuid4())

        if self.timestamp is None:
            self.timestamp = datetime.now()

    @property
    def text(self) -> str:
        """Get combined text content as a single string."""
        return "\n".join([content.text for content in self.text_contents])

    @property
    def first_text(self) -> Optional[str]:
        """Get the first text block, if any."""
        if not self.text_contents:
            return None
        return self.text_contents[0].text

    @property
    def has_tool_calls(self) -> bool:
        """Check if the response contains any tool calls."""
        return len(self.tool_calls) > 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for storage/API."""
        return {
            "id": self.id,
            "provider": self.provider,
            "model": self.model,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "text_contents": [text.to_dict() for text in self.text_contents],
            "tool_calls": [call.to_dict() for call in self.tool_calls]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMResponse':
        """Create an LLMResponse from dictionary data."""
        timestamp = None
        if data.get("timestamp"):
            timestamp = (
                data["timestamp"]
                if isinstance(data["timestamp"], datetime)
                else datetime.fromisoformat(data["timestamp"])
            )

        text_contents = [
            TextContent.from_dict(content)
            for content in data.get("text_contents", [])
        ]

        tool_calls = [
            ToolCall.from_dict(call)
            for call in data.get("tool_calls", [])
        ]

        return cls(
            id=data.get("id"),
            provider=data.get("provider"),
            model=data.get("model"),
            timestamp=timestamp,
            text_contents=text_contents,
            tool_calls=tool_calls
        )

    @classmethod
    def from_anthropic_response(cls, response, model: str = None) -> 'LLMResponse':
        """Create an LLMResponse from an Anthropic API response."""
        text_contents = []
        tool_calls = []

        # Process each content block
        for i, content in enumerate(response.content):
            if content.type == "text":
                text_contents.append(TextContent(
                    text=content.text,
                    content_type="text",
                    index=i
                ))
            elif content.type == "tool_use":
                tool_calls.append(ToolCall(
                    id=content.id,
                    name=content.name,
                    arguments=content.input or {}
                ))

        return cls(
            provider="claude",
            model=model or "unknown",
            text_contents=text_contents,
            tool_calls=tool_calls,
            raw_response=response
        )

    @classmethod
    def from_openai_response(cls, response, model: str = None) -> 'LLMResponse':
        """Create an LLMResponse from an OpenAI API response."""
        text_contents = []
        tool_calls = []

        # Process message content
        message = response.choices[0].message

        # Handle different content formats
        if isinstance(message.content, str):
            # Simple text response
            text_contents.append(TextContent(
                text=message.content,
                content_type="text"
            ))
        else:
            # Content can be a list of different types
            for i, content in enumerate(message.content):
                if content.type == "text":
                    text_contents.append(TextContent(
                        text=content.text,
                        content_type="text",
                        index=i
                    ))

        # Process tool calls
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                tool_calls.append(ToolCall(
                    id=tool_call.id,
                    name=tool_call.function.name,
                    arguments=tool_call.function.arguments
                ))

        return cls(
            provider="openai",
            model=model or response.model,
            text_contents=text_contents,
            tool_calls=tool_calls,
            raw_response=response
        )

    @classmethod
    def create_text_only(cls, text: str, provider: str = "unknown", model: str = None) -> 'LLMResponse':
        """Create a simple text-only response."""
        return cls(
            text_contents=[TextContent(text=text)],
            tool_calls=[],
            provider=provider,
            model=model
        )

    def add_text_content(self, text: str) -> None:
        """Add a text content block to the response."""
        self.text_contents.append(TextContent(
            text=text,
            index=len(self.text_contents) + len(self.tool_calls)
        ))

    def add_tool_call(self, tool_call: ToolCall) -> None:
        """Add a tool call to the response."""
        self.tool_calls.append(tool_call)