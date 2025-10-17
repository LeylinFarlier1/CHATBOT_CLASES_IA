"""
Message Formatter
Formats chat messages with timestamps and styling
"""
from datetime import datetime
from typing import Dict, List


class MessageFormatter:
    """Formats messages for display in the chat panel"""

    @staticmethod
    def format_user_message(content: str, timestamp: str = None) -> Dict[str, str]:
        """
        Format a user message
        
        Args:
            content: Message content
            timestamp: Optional timestamp (will be generated if not provided)
            
        Returns:
            Formatted message dictionary
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M:%S")
        
        return {
            "role": "user",
            "content": content,
            "timestamp": timestamp,
            "prefix": f"**You** ({timestamp})"
        }

    @staticmethod
    def format_assistant_message(content: str, timestamp: str = None) -> Dict[str, str]:
        """
        Format an assistant message
        
        Args:
            content: Message content
            timestamp: Optional timestamp (will be generated if not provided)
            
        Returns:
            Formatted message dictionary
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M:%S")
        
        return {
            "role": "assistant",
            "content": content,
            "timestamp": timestamp,
            "prefix": f"**Assistant** ({timestamp})"
        }

    @staticmethod
    def format_system_message(content: str, timestamp: str = None) -> Dict[str, str]:
        """
        Format a system message
        
        Args:
            content: Message content
            timestamp: Optional timestamp (will be generated if not provided)
            
        Returns:
            Formatted message dictionary
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M:%S")
        
        return {
            "role": "system",
            "content": content,
            "timestamp": timestamp,
            "prefix": f"**System** ({timestamp})"
        }

    @staticmethod
    def format_error_message(error: str, timestamp: str = None) -> Dict[str, str]:
        """
        Format an error message
        
        Args:
            error: Error message
            timestamp: Optional timestamp (will be generated if not provided)
            
        Returns:
            Formatted error message dictionary
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M:%S")
        
        return {
            "role": "system",
            "content": f"❌ **Error:** {error}",
            "timestamp": timestamp,
            "prefix": f"**Error** ({timestamp})"
        }

    @staticmethod
    def render_messages(messages: List[Dict[str, str]]) -> str:
        """
        Render a list of messages as markdown
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Formatted markdown string
        """
        if not messages:
            return ""
        
        full_content = ""
        for msg in messages:
            role_prefix = msg.get("prefix", "**Message**")
            content = msg.get("content", "")
            full_content += f"\n\n{role_prefix}\n\n{content}\n\n---"
        
        return full_content
