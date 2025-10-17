"""
Execute Tool Use Case - Orchestrates tool execution workflow.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import logging

from core.services.mcp_service import MCPService
from core.models.tool_result import ToolResult


@dataclass
class ExecuteToolRequest:
    """Request for execute tool use case."""
    tool_name: str
    arguments: Dict[str, Any]


@dataclass
class ExecuteToolResponse:
    """Response from execute tool use case."""
    success: bool
    tool_name: str
    result: Optional[ToolResult] = None
    error: Optional[str] = None


class ExecuteToolUseCase:
    """
    Use case: Execute MCP tool.
    
    This use case orchestrates the complete flow of:
    1. Validate tool exists
    2. Execute tool with arguments
    3. Parse and validate result
    4. Handle errors gracefully
    
    Responsibilities:
    - Validate tool availability
    - Execute tool with proper error handling
    - Parse tool results
    - Log execution details
    """
    
    def __init__(self, mcp_service: MCPService):
        """
        Initialize use case.
        
        Args:
            mcp_service: MCP service for tool operations
        """
        self.mcp_service = mcp_service
        self.logger = logging.getLogger(__name__)
    
    async def execute(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> ExecuteToolResponse:
        """
        Execute use case: execute MCP tool.
        
        Args:
            tool_name: Name of tool to execute
            arguments: Tool arguments
            
        Returns:
            ExecuteToolResponse with result or error
        """
        self.logger.info(f"Executing tool: {tool_name}")
        
        try:
            # Validate tool exists
            if not await self._validate_tool(tool_name):
                error_msg = f"Tool not found: {tool_name}"
                self.logger.error(error_msg)
                return ExecuteToolResponse(
                    success=False,
                    tool_name=tool_name,
                    error=error_msg
                )
            
            # Execute tool
            result = await self.mcp_service.execute_tool(
                tool_name=tool_name,
                arguments=arguments
            )
            
            self.logger.info(f"Tool executed successfully: {tool_name}")
            
            return ExecuteToolResponse(
                success=True,
                tool_name=tool_name,
                result=result
            )
            
        except Exception as e:
            error_msg = f"Failed to execute tool: {str(e)}"
            self.logger.error(error_msg)
            
            return ExecuteToolResponse(
                success=False,
                tool_name=tool_name,
                error=error_msg
            )
    
    async def execute_multiple(
        self,
        tool_calls: List[Dict[str, Any]]
    ) -> List[ExecuteToolResponse]:
        """
        Execute multiple tools sequentially.
        
        Args:
            tool_calls: List of tool calls with name and arguments
            
        Returns:
            List of ExecuteToolResponse
        """
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            arguments = tool_call.get("arguments", {})
            
            response = await self.execute(
                tool_name=tool_name,
                arguments=arguments
            )
            
            results.append(response)
        
        return results
    
    async def _validate_tool(self, tool_name: str) -> bool:
        """
        Validate tool exists.
        
        Args:
            tool_name: Name of tool to validate
            
        Returns:
            True if tool exists
        """
        try:
            tools = await self.mcp_service.list_tools()
            return any(tool.get("name") == tool_name for tool in tools)
        except Exception as e:
            self.logger.error(f"Error validating tool: {e}")
            return False
    
    async def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a tool.
        
        Args:
            tool_name: Name of tool
            
        Returns:
            Tool information dict or None if not found
        """
        try:
            tools = await self.mcp_service.list_tools()
            return next(
                (tool for tool in tools if tool.get("name") == tool_name),
                None
            )
        except Exception as e:
            self.logger.error(f"Error getting tool info: {e}")
            return None
