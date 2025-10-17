"""
LLM Service - Orchestrates LLM operations and tool handling.
Extracted and unified from tui_app.py and client.py.
"""
from typing import List, Dict, Any, Optional
import logging

from core.interfaces.llm_provider import ILLMProvider
from core.models.conversation import Message, Conversation
from core.models.tool_result import ToolCall, ToolResult
from core.models.llm_response import LLMResponse
from core.services.mcp_service import MCPService


class LLMService:
    """
    Service for LLM operations (orchestration, tool handling).
    
    Centralizes and unifies LLM logic extracted from:
    - tui_app.py lines 914-1070 (process_query)
    - client.py lines 107-322 (process_query)
    
    Key responsibilities:
    - Orchestrate LLM provider calls
    - Handle tool calling workflow
    - Manage conversation state
    - Coordinate with MCP service for tool execution
    """
    
    def __init__(
        self,
        llm_provider: ILLMProvider,
        mcp_service: MCPService
    ):
        """
        Initialize LLM service.
        
        Args:
            llm_provider: LLM provider implementation (Claude, OpenAI, etc.)
            mcp_service: MCP service for tool execution
        """
        self.provider = llm_provider
        self.mcp_service = mcp_service
        self.logger = logging.getLogger(__name__)
    
    async def process_query(
        self,
        query: str,
        conversation: Conversation,
        max_tokens: int = 4096,
        temperature: float = 1.0
    ) -> LLMResponse:
        """
        Process user query with LLM and handle tool calls.
        
        This is the main orchestration method that:
        1. Adds user message to conversation
        2. Gets available MCP tools
        3. Calls LLM with tools
        4. Executes any tool calls
        5. Gets final response if tools were used
        
        Args:
            query: User query text
            conversation: Current conversation object
            max_tokens: Maximum tokens for LLM response
            temperature: Sampling temperature
            
        Returns:
            LLMResponse with final text and metadata
        """
        self.logger.info(f"Processing query: {query[:50]}...")
        
        # Add user message to conversation
        user_message = Message(role="user", content=query)
        conversation.messages.append(user_message)
        
        # Get available tools from MCP
        available_tools = await self.mcp_service.list_tools()
        
        # Call LLM with tools
        llm_response = await self.provider.process_messages(
            messages=conversation.messages,
            tools=available_tools,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Add assistant response to conversation
        assistant_message = Message(
            role="assistant",
            content=self._build_assistant_content(llm_response)
        )
        conversation.messages.append(assistant_message)
        
        # Handle tool calls if any
        if llm_response.tool_calls:
            self.logger.info(f"Executing {len(llm_response.tool_calls)} tool calls")
            
            # Execute all tool calls
            tool_results = await self._execute_tool_calls(
                llm_response.tool_calls,
                conversation
            )
            
            # Add tool results to conversation
            tool_results_message = Message(
                role="user",
                content=self._build_tool_results_content(tool_results)
            )
            conversation.messages.append(tool_results_message)
            
            # Get final response with tool results
            final_response = await self.provider.process_messages(
                messages=conversation.messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Add final assistant response
            final_message = Message(
                role="assistant",
                content=self._build_assistant_content(final_response)
            )
            conversation.messages.append(final_message)
            
            # Update conversation metadata
            for tool_call in llm_response.tool_calls:
                if tool_call.name not in conversation.tools_used:
                    conversation.tools_used.append(tool_call.name)
            
            return final_response
        
        return llm_response
    
    async def _execute_tool_calls(
        self,
        tool_calls: List[ToolCall],
        conversation: Conversation
    ) -> List[ToolResult]:
        """
        Execute multiple tool calls.
        
        Args:
            tool_calls: List of tool calls to execute
            conversation: Current conversation (for metadata)
            
        Returns:
            List of tool results
        """
        results = []
        
        for tool_call in tool_calls:
            self.logger.debug(f"Executing tool: {tool_call.name}")
            
            try:
                result = await self.mcp_service.execute_tool(tool_call)
                results.append(result)
                
                # Track tool usage
                if tool_call.name not in conversation.tools_used:
                    conversation.tools_used.append(tool_call.name)
                    
            except Exception as e:
                self.logger.error(f"Error executing tool {tool_call.name}: {e}")
                
                # Create error result
                error_result = ToolResult(
                    tool_call_id=tool_call.id,
                    tool_name=tool_call.name,
                    result=None,
                    error=str(e),
                    is_error=True
                )
                results.append(error_result)
        
        return results
    
    def _build_assistant_content(self, llm_response: LLMResponse) -> Any:
        """
        Build assistant message content from LLM response.
        
        Handles both text and tool calls in structured format.
        """
        content = []
        
        # Add text content if present
        if llm_response.text:
            content.append({
                "type": "text",
                "text": llm_response.text
            })
        
        # Add tool calls if present
        if llm_response.tool_calls:
            for tool_call in llm_response.tool_calls:
                content.append({
                    "type": "tool_use",
                    "id": tool_call.id,
                    "name": tool_call.name,
                    "input": tool_call.arguments
                })
        
        # Return simple text if only one text block
        if len(content) == 1 and content[0]["type"] == "text":
            return content[0]["text"]
        
        return content
    
    def _build_tool_results_content(self, tool_results: List[ToolResult]) -> List[Dict[str, Any]]:
        """
        Build tool results content for conversation.
        
        Converts ToolResult objects to message content format.
        """
        content = []
        
        for result in tool_results:
            tool_result_block = {
                "type": "tool_result",
                "tool_use_id": result.tool_call_id,
            }
            
            if result.is_error:
                tool_result_block["content"] = f"Error: {result.error_message}"
                tool_result_block["is_error"] = True
            else:
                tool_result_block["content"] = result.content
            
            content.append(tool_result_block)
        
        return content
    
    def switch_provider(self, provider: ILLMProvider) -> None:
        """
        Switch LLM provider dynamically.
        
        Args:
            provider: New LLM provider instance
        """
        self.logger.info(f"Switching LLM provider to {provider.__class__.__name__}")
        self.provider = provider
    
    def get_current_provider(self) -> ILLMProvider:
        """Get current LLM provider."""
        return self.provider
    
    def get_provider_info(self) -> Dict[str, str]:
        """
        Get information about current provider.
        
        Returns:
            Dict with provider class name and model ID
        """
        return {
            "provider": self.provider.__class__.__name__,
            "model_id": self.provider.get_model_id(),
            "supports_tools": self.provider.supports_tools()
        }
