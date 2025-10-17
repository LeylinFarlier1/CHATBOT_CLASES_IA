"""
Conversation Service - Manages conversation history and persistence.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import os
from pathlib import Path

from core.models.conversation import Conversation, Message


class ConversationService:
    """
    Service for managing conversations.
    
    Responsibilities:
    - Manage current conversation
    - Save/load conversations
    - Export conversations
    - Track conversation history
    """
    
    def __init__(self, conversations_dir: str = "conversations"):
        """
        Initialize conversation service.
        
        Args:
            conversations_dir: Directory to store conversation files
        """
        self.conversations_dir = Path(conversations_dir)
        self.conversations_dir.mkdir(exist_ok=True)
        
        self._current_conversation: Optional[Conversation] = None
        self._conversation_index: List[Dict[str, str]] = []
    
    def get_current(self) -> Conversation:
        """
        Get current conversation.
        
        Creates new conversation if none exists.
        """
        if self._current_conversation is None:
            self._current_conversation = Conversation(
                messages=[],
                id=self._generate_conversation_id()
            )
        
        return self._current_conversation
    
    def start_new_conversation(self) -> Conversation:
        """
        Start a new conversation.
        
        Saves current conversation if it exists and has messages.
        """
        if self._current_conversation and len(self._current_conversation.messages) > 0:
            self.save(self._current_conversation)
        
        self._current_conversation = Conversation(
            messages=[],
            id=self._generate_conversation_id()
        )
        
        return self._current_conversation
    
    def add_message(self, role: str, content: Any) -> Message:
        """
        Add message to current conversation.
        
        Args:
            role: Message role ("user" or "assistant")
            content: Message content (text or structured)
            
        Returns:
            Created Message object
        """
        conversation = self.get_current()
        
        message = Message(role=role, content=content)
        conversation.messages.append(message)
        
        return message
    
    def get_messages(self) -> List[Message]:
        """Get all messages from current conversation."""
        return self.get_current().messages
    
    def clear_current(self) -> None:
        """Clear current conversation without saving."""
        self._current_conversation = None
    
    def save(self, conversation: Optional[Conversation] = None) -> str:
        """
        Save conversation to file.
        
        Args:
            conversation: Conversation to save (defaults to current)
            
        Returns:
            Path to saved file
        """
        if conversation is None:
            conversation = self.get_current()
        
        # Generate filename
        filename = f"conversation_{conversation.id}.json"
        filepath = self.conversations_dir / filename
        
        # Convert to dict
        conversation_dict = {
            "id": conversation.id,
            "created_at": conversation.created_at.isoformat(),
            "tools_used": conversation.tools_used,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in conversation.messages
            ]
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation_dict, f, indent=2, ensure_ascii=False)
        
        # Update index
        self._update_index(conversation)
        
        return str(filepath)
    
    def load(self, conversation_id: str) -> Conversation:
        """
        Load conversation from file.
        
        Args:
            conversation_id: ID of conversation to load
            
        Returns:
            Loaded Conversation object
        """
        filename = f"conversation_{conversation_id}.json"
        filepath = self.conversations_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Conversation {conversation_id} not found")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Reconstruct conversation
        messages = [
            Message(
                role=msg["role"],
                content=msg["content"],
                timestamp=datetime.fromisoformat(msg["timestamp"])
            )
            for msg in data["messages"]
        ]
        
        conversation = Conversation(
            messages=messages,
            id=data["id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            tools_used=data.get("tools_used", [])
        )
        
        return conversation
    
    def list_conversations(self) -> List[Dict[str, str]]:
        """
        List all saved conversations.
        
        Returns:
            List of conversation metadata (id, created_at, message_count)
        """
        conversations = []
        
        for filepath in self.conversations_dir.glob("conversation_*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                conversations.append({
                    "id": data["id"],
                    "created_at": data["created_at"],
                    "message_count": len(data["messages"]),
                    "tools_used": data.get("tools_used", [])
                })
            except Exception:
                continue
        
        # Sort by created_at descending
        conversations.sort(key=lambda x: x["created_at"], reverse=True)
        
        return conversations
    
    def delete(self, conversation_id: str) -> bool:
        """
        Delete conversation file.
        
        Args:
            conversation_id: ID of conversation to delete
            
        Returns:
            True if deleted successfully
        """
        filename = f"conversation_{conversation_id}.json"
        filepath = self.conversations_dir / filename
        
        if filepath.exists():
            filepath.unlink()
            return True
        
        return False
    
    def export_to_text(self, conversation: Optional[Conversation] = None) -> str:
        """
        Export conversation to plain text format.
        
        Args:
            conversation: Conversation to export (defaults to current)
            
        Returns:
            Text representation of conversation
        """
        if conversation is None:
            conversation = self.get_current()
        
        lines = [
            f"Conversation ID: {conversation.id}",
            f"Created: {conversation.created_at}",
            f"Messages: {len(conversation.messages)}",
            ""
        ]
        
        for i, msg in enumerate(conversation.messages, 1):
            role_label = "USER" if msg.role == "user" else "ASSISTANT"
            lines.append(f"[{i}] {role_label} ({msg.timestamp}):")
            
            if isinstance(msg.content, str):
                lines.append(msg.content)
            else:
                lines.append(str(msg.content))
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_conversation_id(self) -> str:
        """Generate unique conversation ID."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _update_index(self, conversation: Conversation) -> None:
        """Update conversation index."""
        # Simple implementation: just track IDs
        entry = {
            "id": conversation.id,
            "created_at": conversation.created_at.isoformat()
        }
        
        # Remove old entry if exists
        self._conversation_index = [
            e for e in self._conversation_index
            if e["id"] != conversation.id
        ]
        
        # Add new entry
        self._conversation_index.append(entry)
