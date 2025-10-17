"""
MCP client interfaces.

This module defines interfaces for MCP (Model Context Protocol) clients,
allowing the application to interact with different MCP server implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

from core.models.tool_result import ToolCall, ToolResult


class IMCPClient(ABC):
    """
    Interface for MCP (Model Context Protocol) client.

    This interface defines the contract that MCP clients must implement,
    allowing the application to interact with different MCP server implementations
    while maintaining a consistent API.
    """

    @abstractmethod
    async def list_tools(self) -> Dict[str, Any]:
        """
        Get a list of all available tools from the MCP server.

        Returns:
            A dictionary containing:
            - tools: List of tool definitions (each with name, description, parameters)
            - additional server metadata
        """
        pass

    @abstractmethod
    async def call_tool(self, tool_name: str, tool_params: Dict[str, Any]) -> ToolResult:
        """
        Call a specific MCP tool with the given parameters.

        Args:
            tool_name: The name of the tool to call
            tool_params: A dictionary of parameters to pass to the tool

        Returns:
            A ToolResult object containing the result of the tool execution
        """
        pass

    @abstractmethod
    async def call_tools_batch(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        """
        Call multiple MCP tools in batch.

        Args:
            tool_calls: A list of ToolCall objects representing the tools to call

        Returns:
            A list of ToolResult objects containing the results of the tool executions
        """
        pass

    @abstractmethod
    async def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the schema for a specific tool.

        Args:
            tool_name: The name of the tool to get the schema for

        Returns:
            A dictionary containing the tool schema, or None if not found
        """
        pass

    @abstractmethod
    async def read_resource(self, resource_path: str) -> Dict[str, Any]:
        """
        Read an MCP resource from the server.

        Args:
            resource_path: The path to the resource to read

        Returns:
            A dictionary containing the resource data
        """
        pass

    @abstractmethod
    def get_server_url(self) -> str:
        """
        Get the URL of the MCP server.

        Returns:
            The server URL as a string
        """
        pass