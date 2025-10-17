"""
TUI App Adapter - Bridge between legacy tui_app.py and new architecture.

This adapter allows the old MacroMCPApp to gradually adopt the new services
without breaking existing functionality. It acts as a translation layer.

Phase 7.1 of the modularization plan.
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from core.services.mcp_service import MCPService
from core.services.llm_service import LLMService
from core.services.conversation_service import ConversationService
from core.models.conversation import Conversation, Message
from core.models.llm_response import LLMResponse
from infrastructure.llm.provider_factory import LLMProviderFactory


class TUIAppAdapter:
    """
    Adapter that allows legacy tui_app.py to use new services.
    
    This class bridges the gap between the old monolithic implementation
    and the new clean architecture, enabling gradual migration.
    """
    
    def __init__(
        self,
        provider_name: str = "claude",
        model_key: str = "sonnet-3.7",
        conversation_service: Optional[ConversationService] = None
    ):
        """
        Initialize the adapter.
        
        Args:
            provider_name: LLM provider name ("claude", "openai", "gemini")
            model_key: Model key from provider configuration
            conversation_service: Optional conversation service instance
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize services
        self.mcp_service = MCPService()
        
        # Create LLM provider using factory
        self.llm_provider = LLMProviderFactory.create_provider(provider_name)
        self.llm_service = LLMService(self.llm_provider, self.mcp_service)
        
        # Conversation service
        self.conversation_service = conversation_service or ConversationService()
        
        # Current state
        self.current_provider = provider_name
        self.current_model_key = model_key
        self.is_connected = False
        
        self.logger.info(f"TUIAppAdapter initialized with {provider_name}/{model_key}")
    
    async def connect_to_mcp(
        self,
        server_path: str,
        server_args: List[str],
        env: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Connect to MCP server.
        
        Args:
            server_path: Path to MCP server script
            server_args: Arguments for server startup
            env: Optional environment variables
            
        Returns:
            True if connection successful
        """
        try:
            await self.mcp_service.connect(
                server_path=server_path,
                server_args=server_args,
                env=env
            )
            
            self.is_connected = True
            self.logger.info("✅ Connected to MCP server")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to MCP: {e}")
            self.is_connected = False
            return False
    
    async def disconnect_from_mcp(self) -> None:
        """Disconnect from MCP server."""
        try:
            await self.mcp_service.disconnect()
            self.is_connected = False
            self.logger.info("Disconnected from MCP server")
        except Exception as e:
            self.logger.error(f"Error disconnecting: {e}")
    
    async def process_query_adapted(
        self,
        query: str,
        max_tokens: int = 4096,
        temperature: float = 1.0
    ) -> Dict[str, Any]:
        """
        Process query using new services and return old format.
        
        This method uses the new LLMService but returns data in the
        format expected by legacy tui_app.py code.
        
        Args:
            query: User query text
            max_tokens: Maximum tokens for response
            temperature: Sampling temperature
            
        Returns:
            Dict with 'text' and 'tool_calls' keys (old format)
        """
        try:
            # Get current conversation
            conversation = self.conversation_service.get_current()
            
            # Process with new service
            response = await self.llm_service.process_query(
                query=query,
                conversation=conversation,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Save conversation
            self.conversation_service.save(conversation)
            
            # Convert to old format
            return self._convert_to_old_format(response)
            
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            raise
    
    def _convert_to_old_format(self, response: LLMResponse) -> Dict[str, Any]:
        """
        Convert new LLMResponse to old dictionary format.
        
        Args:
            response: New LLMResponse object
            
        Returns:
            Dictionary with 'text' and 'tool_calls' in old format
        """
        # Convert tool calls to old format
        tool_calls_old = []
        for tool_call in response.tool_calls:
            tool_calls_old.append({
                "type": "tool_use",
                "id": tool_call.id,
                "name": tool_call.name,
                "input": tool_call.arguments
            })
        
        return {
            "text": response.text,
            "tool_calls": tool_calls_old if tool_calls_old else None,
            "provider": response.provider,
            "model": response.model
        }
    
    def get_conversation_messages(self) -> List[Dict[str, Any]]:
        """
        Get current conversation messages in old format.
        
        Returns:
            List of message dicts with 'role' and 'content'
        """
        conversation = self.conversation_service.get_current()
        
        messages = []
        for msg in conversation.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp
            })
        
        return messages
    
    def add_message_to_conversation(
        self,
        role: str,
        content: Any
    ) -> None:
        """
        Add message to current conversation.
        
        Args:
            role: Message role ('user', 'assistant', 'tool')
            content: Message content
        """
        self.conversation_service.add_message(role, content)
    
    def clear_conversation(self) -> None:
        """Clear current conversation."""
        self.conversation_service.clear_current()
    
    def start_new_conversation(self) -> str:
        """
        Start a new conversation.
        
        Returns:
            New conversation ID
        """
        conv = self.conversation_service.start_new_conversation()
        return conv.id
    
    def save_conversation(self, filename: Optional[str] = None) -> str:
        """
        Save current conversation.
        
        Args:
            filename: Optional filename (auto-generated if None)
            
        Returns:
            Path to saved conversation
        """
        conversation = self.conversation_service.get_current()
        return self.conversation_service.save(conversation)
    
    def load_conversation(self, conversation_id: str) -> bool:
        """
        Load a saved conversation.
        
        Args:
            conversation_id: ID of conversation to load
            
        Returns:
            True if loaded successfully
        """
        try:
            conversation = self.conversation_service.load(conversation_id)
            # Set as current
            self.conversation_service._current_conversation = conversation
            return True
        except Exception as e:
            self.logger.error(f"Failed to load conversation: {e}")
            return False
    
    def list_conversations(self) -> List[Dict[str, Any]]:
        """
        List all saved conversations.
        
        Returns:
            List of conversation metadata dicts
        """
        return self.conversation_service.list_conversations()
    
    async def list_available_tools(self) -> List[Dict[str, Any]]:
        """
        List available MCP tools.
        
        Returns:
            List of tool definitions
        """
        if not self.is_connected:
            return []
        
        return await self.mcp_service.list_tools()
    
    async def list_available_resources(self) -> List[Dict[str, Any]]:
        """
        List available MCP resources.
        
        Returns:
            List of resource definitions
        """
        if not self.is_connected:
            return []
        
        return await self.mcp_service.list_resources()
    
    async def read_resource(self, uri: str) -> str:
        """
        Read MCP resource content by URI.
        
        Args:
            uri: Resource URI to read
            
        Returns:
            Resource content as string
        """
        if not self.is_connected:
            return ""
        
        return await self.mcp_service.read_resource(uri)
    
    def switch_provider(
        self,
        provider_name: str,
        model_key: Optional[str] = None
    ) -> None:
        """
        Switch LLM provider.
        
        Args:
            provider_name: New provider name
            model_key: Optional model key
        """
        try:
            # Create new provider
            new_provider = LLMProviderFactory.create_provider(provider_name)
            
            # Switch in service
            self.llm_service.switch_provider(new_provider)
            
            self.current_provider = provider_name
            if model_key:
                self.current_model_key = model_key
            
            self.logger.info(f"Switched to provider: {provider_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to switch provider: {e}")
            raise
    
    def get_provider_info(self) -> Dict[str, str]:
        """
        Get current provider information.
        
        Returns:
            Dict with provider and model info
        """
        info = self.llm_service.get_provider_info()
        info["model_key"] = self.current_model_key
        # Ensure 'model' key exists for compatibility
        if "model_id" in info and "model" not in info:
            info["model"] = info["model_id"]
        return info
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get MCP connection status.
        
        Returns:
            Dict with connection information
        """
        if not self.is_connected:
            return {
                "connected": False,
                "tools_count": 0,
                "resources_count": 0
            }
        
        return {
            "connected": True,
            "tools_count": self.mcp_service.get_tools_count(),
            "resources_count": self.mcp_service.get_resources_count()
        }
