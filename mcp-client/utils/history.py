"""
Conversation History Management
Handles storing, searching, and exporting conversation history.
"""

from typing import List, Dict, Optional
from datetime import datetime
import json
import os


class ConversationHistory:
    """Manages conversation history with search and export capabilities."""

    def __init__(self, max_items: int = 100):
        """
        Initialize conversation history.

        Args:
            max_items: Maximum number of conversation items to store
        """
        self.history: List[Dict] = []
        self.max_items = max_items

    def add(self, query: str, response: str, tools_used: List[str] = None, timestamp: datetime = None):
        """
        Add a conversation item to history.

        Args:
            query: User query
            response: Claude's response
            tools_used: List of tool names used
            timestamp: Timestamp of the conversation (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()

        self.history.append({
            'query': query,
            'response': response,
            'timestamp': timestamp.isoformat(),
            'tools_used': tools_used or []
        })

        # Remove oldest items if exceeding max
        if len(self.history) > self.max_items:
            self.history.pop(0)

    def search(self, keyword: str) -> List[Dict]:
        """
        Search conversation history by keyword.

        Args:
            keyword: Keyword to search for (case-insensitive)

        Returns:
            List of matching conversation items
        """
        keyword_lower = keyword.lower()
        return [
            item for item in self.history
            if keyword_lower in item['query'].lower() or keyword_lower in item['response'].lower()
        ]

    def get_last_n(self, n: int) -> List[Dict]:
        """
        Get last N conversation items.

        Args:
            n: Number of items to retrieve

        Returns:
            List of last N conversation items
        """
        return self.history[-n:] if n < len(self.history) else self.history

    def clear(self):
        """Clear all conversation history."""
        self.history.clear()

    def export_markdown(self, filename: str, directory: str = "conversations") -> str:
        """
        Export conversation history to markdown file.

        Args:
            filename: Name of the file (without extension)
            directory: Directory to save the file

        Returns:
            Path to the saved file
        """
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)

        # Add .md extension if not present
        if not filename.endswith('.md'):
            filename = f"{filename}.md"

        filepath = os.path.join(directory, filename)

        # Generate markdown content
        markdown_content = self._generate_markdown()

        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return filepath

    def export_json(self, filename: str, directory: str = "conversations") -> str:
        """
        Export conversation history to JSON file.

        Args:
            filename: Name of the file (without extension)
            directory: Directory to save the file

        Returns:
            Path to the saved file
        """
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)

        # Add .json extension if not present
        if not filename.endswith('.json'):
            filename = f"{filename}.json"

        filepath = os.path.join(directory, filename)

        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

        return filepath

    def load_json(self, filepath: str) -> int:
        """
        Load conversation history from JSON file.

        Args:
            filepath: Path to the JSON file

        Returns:
            Number of items loaded
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            loaded_history = json.load(f)

        # Clear current history and load new one
        self.history.clear()
        self.history.extend(loaded_history)

        # Trim if exceeds max_items
        if len(self.history) > self.max_items:
            self.history = self.history[-self.max_items:]

        return len(self.history)

    def _generate_markdown(self) -> str:
        """Generate markdown content from history."""
        lines = [
            "# Conversation History",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Conversations:** {len(self.history)}",
            "",
            "---",
            ""
        ]

        for i, item in enumerate(self.history, 1):
            timestamp = item.get('timestamp', 'Unknown')
            query = item.get('query', '')
            response = item.get('response', '')
            tools_used = item.get('tools_used', [])

            lines.append(f"## Conversation {i}")
            lines.append("")
            lines.append(f"**Date:** {timestamp}")

            if tools_used:
                tools_str = ", ".join([f"`{tool}`" for tool in tools_used])
                lines.append(f"**Tools Used:** {tools_str}")

            lines.append("")
            lines.append("### User Query")
            lines.append("")
            lines.append(query)
            lines.append("")
            lines.append("### Claude Response")
            lines.append("")
            lines.append(response)
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def get_stats(self) -> Dict:
        """
        Get statistics about conversation history.

        Returns:
            Dictionary with statistics
        """
        if not self.history:
            return {
                'total_conversations': 0,
                'total_queries': 0,
                'total_responses': 0,
                'tools_usage': {},
                'date_range': None
            }

        # Count tool usage
        tools_usage = {}
        for item in self.history:
            for tool in item.get('tools_used', []):
                tools_usage[tool] = tools_usage.get(tool, 0) + 1

        # Get date range
        timestamps = [item['timestamp'] for item in self.history]
        date_range = {
            'first': min(timestamps),
            'last': max(timestamps)
        }

        return {
            'total_conversations': len(self.history),
            'total_queries': len(self.history),
            'total_responses': len(self.history),
            'tools_usage': tools_usage,
            'date_range': date_range
        }

    def __len__(self) -> int:
        """Return number of items in history."""
        return len(self.history)

    def __getitem__(self, index: int) -> Dict:
        """Get item by index."""
        return self.history[index]
