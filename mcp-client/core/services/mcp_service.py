"""
MCP Service - Handles all MCP operations (tools, resources, execution).
Extracted from tui_app.py and client.py.
"""
from typing import List, Dict, Any, Optional, TYPE_CHECKING
import logging
from contextlib import AsyncExitStack

from core.models.tool_result import ToolCall, ToolResult

# Lazy imports to avoid circular dependencies and allow testing without MCP installed
if TYPE_CHECKING:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client


class MCPService:
    """
    Service for MCP operations (tools, resources, execution).
    
    Centralizes all MCP-related logic extracted from:
    - tui_app.py lines 654-704 (connect_to_mcp)
    - tui_app.py lines 976-999 (tool execution)
    - client.py lines 47-105 (connect)
    """
    
    def __init__(self):
        """Initialize MCP service."""
        self.session: Optional[Any] = None  # Type: Optional[ClientSession]
        self.stdio = None
        self.write = None
        self.exit_stack = AsyncExitStack()
        
        self._tools_cache: Optional[List] = None
        self._resources_cache: Optional[List] = None
        
        self.logger = logging.getLogger(__name__)
    
    async def connect(
        self,
        server_path: str,
        server_args: List[str],
        env: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Connect to MCP server.
        
        Args:
            server_path: Path to server script (e.g., "server_mcp.py")
            server_args: Arguments for server startup
            env: Optional environment variables
            
        Raises:
            Exception: If connection fails
        """
        # Import MCP modules only when needed
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
        self.logger.info(f"Connecting to MCP server: {server_path}")
        
        try:
            # Configure server parameters
            server_params = StdioServerParameters(
                command="uv",
                args=server_args,
                env=env,
            )
            
            # Create transport and session
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            self.stdio, self.write = stdio_transport
            
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(self.stdio, self.write)
            )
            
            # Initialize session
            await self.session.initialize()
            
            self.logger.info("MCP server connected successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MCP server: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from MCP server."""
        await self.exit_stack.aclose()
        self.session = None
        self._tools_cache = None
        self._resources_cache = None
        self.logger.info("Disconnected from MCP server")
    
    def is_connected(self) -> bool:
        """Check if connected to MCP server."""
        return self.session is not None
    
    async def list_tools(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        List available MCP tools.
        
        Args:
            use_cache: Whether to use cached tools list
            
        Returns:
            List of tool dictionaries with name, description, input_schema
        """
        if not self.is_connected():
            raise RuntimeError("Not connected to MCP server")
        
        if use_cache and self._tools_cache is not None:
            return self._tools_cache
        
        response = await self.session.list_tools()
        
        self._tools_cache = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
            }
            for tool in response.tools
        ]
        
        self.logger.info(f"Listed {len(self._tools_cache)} tools from MCP server")
        return self._tools_cache
    
    async def list_resources(self, use_cache: bool = True) -> List:
        """
        List available MCP resources.
        
        Args:
            use_cache: Whether to use cached resources list
            
        Returns:
            List of available resources
        """
        if not self.is_connected():
            raise RuntimeError("Not connected to MCP server")
        
        if use_cache and self._resources_cache is not None:
            return self._resources_cache
        
        try:
            response = await self.session.list_resources()
            self._resources_cache = response.resources
            self.logger.info(f"Listed {len(self._resources_cache)} resources from MCP server")
            return self._resources_cache
        except Exception as e:
            self.logger.warning(f"Failed to list resources: {e}")
            return []
    
    async def execute_tool(self, tool_call: ToolCall) -> ToolResult:
        """
        Execute MCP tool and return result.
        
        Extracted from tui_app.py lines 976-999.
        
        Args:
            tool_call: ToolCall with id, name, and arguments
            
        Returns:
            ToolResult with execution result or error
        """
        if not self.is_connected():
            raise RuntimeError("Not connected to MCP server")
        
        tool_name = tool_call.name
        tool_args = tool_call.arguments
        
        self.logger.debug(f"Executing tool: {tool_name} with args: {tool_args}")
        
        try:
            # Suppress logging during tool call to prevent terminal corruption
            old_level = logging.root.level
            logging.root.setLevel(logging.CRITICAL + 1)
            
            try:
                # Call tool
                tool_result = await self.session.call_tool(tool_name, tool_args)
                
                # Extract result text
                result_text = (
                    tool_result.content[0].text
                    if tool_result.content and hasattr(tool_result.content[0], "text")
                    else str(tool_result.content)
                )
            finally:
                # Restore logging level
                logging.root.setLevel(old_level)
            
            self.logger.debug(f"Tool {tool_name} executed successfully")
            
            return ToolResult(
                tool_call_id=tool_call.id,
                tool_name=tool_name,
                content=result_text,
                is_error=False
            )
            
        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {e}")
            
            return ToolResult(
                tool_call_id=tool_call.id,
                tool_name=tool_name,
                content=None,
                error_message=str(e),
                is_error=True
            )
    
    async def read_resource(self, uri: str) -> str:
        """
        Read MCP resource by URI.
        
        Args:
            uri: Resource URI
            
        Returns:
            Resource content as string
        """
        if not self.is_connected():
            raise RuntimeError("Not connected to MCP server")
        
        result = await self.session.read_resource(uri)
        return result.contents[0].text if result.contents else ""
    
    def get_tools_count(self) -> int:
        """Get count of available tools."""
        return len(self._tools_cache) if self._tools_cache else 0
    
    def get_resources_count(self) -> int:
        """Get count of available resources."""
        return len(self._resources_cache) if self._resources_cache else 0
