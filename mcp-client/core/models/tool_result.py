"""
Tool call and tool result domain models.

These models represent the tool calling functionality:
- ToolCall: A request to execute a tool (from LLM)
- ToolResult: The result of executing a tool
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from uuid import uuid4


@dataclass
class ToolCall:
    """
    Represents a tool call request from an LLM.

    When the LLM decides to use a tool, it generates a ToolCall
    with the tool name, arguments, and a unique ID.
    """
    id: str
    name: str
    arguments: Dict[str, Any]
    timestamp: datetime = None

    def __post_init__(self):
        """Initialize default values after creation."""
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for storage/API."""
        return {
            "type": "tool_use",  # Anthropic format
            "id": self.id,
            "name": self.name,
            "input": self.arguments,  # Anthropic format
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolCall':
        """Create a ToolCall from dictionary data."""
        timestamp = None
        if data.get("timestamp"):
            timestamp = (
                data["timestamp"]
                if isinstance(data["timestamp"], datetime)
                else datetime.fromisoformat(data["timestamp"])
            )

        # Handle different formats (Anthropic vs internal)
        arguments = data.get("input", data.get("arguments", {}))

        return cls(
            id=data["id"],
            name=data["name"],
            arguments=arguments,
            timestamp=timestamp
        )

    @classmethod
    def from_anthropic_tool_use(cls, tool_use: Dict[str, Any]) -> 'ToolCall':
        """Create a ToolCall from Anthropic's tool_use format."""
        return cls(
            id=tool_use["id"],
            name=tool_use["name"],
            arguments=tool_use["input"] if tool_use.get("input") else {}
        )


@dataclass
class ToolResult:
    """
    Represents the result of executing a tool.

    After a tool is executed, a ToolResult is created containing
    the result data, or an error if the execution failed.
    """
    tool_call_id: str
    tool_name: str
    content: Any
    is_error: bool = False
    error_message: Optional[str] = None
    timestamp: datetime = None
    id: str = None

    def __post_init__(self):
        """Initialize default values after creation."""
        if self.timestamp is None:
            self.timestamp = datetime.now()

        if self.id is None:
            self.id = str(uuid4())

        # Set error_message if is_error is True and content contains error info
        if self.is_error and self.error_message is None:
            if isinstance(self.content, str):
                self.error_message = self.content
            elif isinstance(self.content, dict) and "error" in self.content:
                self.error_message = str(self.content["error"])
            elif isinstance(self.content, Exception):
                self.error_message = str(self.content)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for storage/API."""
        result = {
            "type": "tool_result",
            "id": self.id,
            "tool_use_id": self.tool_call_id,  # Link to original call
            "tool_name": self.tool_name,
            "content": self.content,
            "is_error": self.is_error,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

        if self.error_message:
            result["error_message"] = self.error_message

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolResult':
        """Create a ToolResult from dictionary data."""
        timestamp = None
        if data.get("timestamp"):
            timestamp = (
                data["timestamp"]
                if isinstance(data["timestamp"], datetime)
                else datetime.fromisoformat(data["timestamp"])
            )

        return cls(
            id=data.get("id"),
            tool_call_id=data["tool_use_id"],
            tool_name=data["tool_name"],
            content=data["content"],
            is_error=data.get("is_error", False),
            error_message=data.get("error_message"),
            timestamp=timestamp
        )

    @property
    def succeeded(self) -> bool:
        """Check if the tool execution succeeded."""
        return not self.is_error

    @property
    def failed(self) -> bool:
        """Check if the tool execution failed."""
        return self.is_error


@dataclass
class ToolResultBatch:
    """
    Represents a batch of tool results.

    Used to group multiple tool results from a single LLM interaction.
    """
    results: List[ToolResult] = field(default_factory=list)
    timestamp: datetime = None

    def __post_init__(self):
        """Initialize default values after creation."""
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def add_result(self, result: ToolResult) -> None:
        """Add a tool result to the batch."""
        self.results.append(result)

    def to_anthropic_format(self) -> List[Dict[str, Any]]:
        """Convert all results to Anthropic format for followup message."""
        return [result.to_dict() for result in self.results]

    def any_failed(self) -> bool:
        """Check if any tool executions failed."""
        return any(result.failed for result in self.results)

    def all_succeeded(self) -> bool:
        """Check if all tool executions succeeded."""
        return all(result.succeeded for result in self.results)

    def __len__(self) -> int:
        """Return the number of tool results in the batch."""
        return len(self.results)