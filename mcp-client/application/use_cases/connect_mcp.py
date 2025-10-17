"""
Connect MCP Use Case - Orchestrates MCP server connection.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import logging

from core.services.mcp_service import MCPService


@dataclass
class ConnectMCPRequest:
    """Request for connect MCP use case."""
    server_path: str
    server_args: List[str]
    env: Optional[Dict[str, str]] = None


@dataclass
class ConnectMCPResponse:
    """Response from connect MCP use case."""
    success: bool
    tools_count: int
    resources_count: int
    error: Optional[str] = None


class ConnectMCPUseCase:
    """
    Use case: Connect to MCP server.
    
    This use case orchestrates the complete flow of:
    1. Connect to MCP server
    2. List available tools
    3. List available resources
    4. Return connection status
    
    Responsibilities:
    - Coordinate MCP connection
    - Validate connection status
    - Handle connection errors
    """
    
    def __init__(self, mcp_service: MCPService):
        """
        Initialize use case.
        
        Args:
            mcp_service: MCP service for server operations
        """
        self.mcp_service = mcp_service
        self.logger = logging.getLogger(__name__)
    
    async def execute(
        self,
        server_path: str,
        server_args: List[str],
        env: Optional[Dict[str, str]] = None
    ) -> ConnectMCPResponse:
        """
        Execute use case: connect to MCP server.
        
        Args:
            server_path: Path to MCP server script
            server_args: Arguments for server startup
            env: Optional environment variables
            
        Returns:
            ConnectMCPResponse with connection status
        """
        self.logger.info(f"Connecting to MCP server: {server_path}")
        
        try:
            # Connect to server
            await self.mcp_service.connect(
                server_path=server_path,
                server_args=server_args,
                env=env
            )
            
            # List tools and resources
            tools = await self.mcp_service.list_tools()
            resources = await self.mcp_service.list_resources()
            
            tools_count = len(tools)
            resources_count = len(resources)
            
            self.logger.info(
                f"Connected successfully: {tools_count} tools, {resources_count} resources"
            )
            
            return ConnectMCPResponse(
                success=True,
                tools_count=tools_count,
                resources_count=resources_count
            )
            
        except Exception as e:
            error_msg = f"Failed to connect: {str(e)}"
            self.logger.error(error_msg)
            
            return ConnectMCPResponse(
                success=False,
                tools_count=0,
                resources_count=0,
                error=error_msg
            )
    
    async def disconnect(self) -> bool:
        """
        Disconnect from MCP server.
        
        Returns:
            True if disconnected successfully
        """
        try:
            await self.mcp_service.disconnect()
            self.logger.info("Disconnected from MCP server")
            return True
        except Exception as e:
            self.logger.error(f"Error disconnecting: {e}")
            return False
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get current connection status.
        
        Returns:
            Dict with connection info
        """
        is_connected = self.mcp_service.is_connected()
        
        return {
            "connected": is_connected,
            "tools_count": self.mcp_service.get_tools_count() if is_connected else 0,
            "resources_count": self.mcp_service.get_resources_count() if is_connected else 0
        }
