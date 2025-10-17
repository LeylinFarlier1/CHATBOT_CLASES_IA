"""
Chat Panel Component
Displays conversation messages with timestamps
"""
from datetime import datetime
from textual.widgets import Markdown
from textual.containers import VerticalScroll
from textual.app import ComposeResult


class ChatPanel(VerticalScroll):
    """Panel de chat con historial de mensajes"""
    
    # Prevent this panel from taking focus
    can_focus = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.messages = []

    def compose(self) -> ComposeResult:
        yield Markdown("", id="chat-content")

    def add_message(self, role: str, content: str):
        """Add a message to the chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if role == "user":
            prefix = f"**You** ({timestamp})"
            style = "user-message"
        else:
            prefix = f"**Assistant** ({timestamp})"
            style = "assistant-message"

        self.messages.append({"role": role, "content": content, "timestamp": timestamp})
        
        # Update display
        content_widget = self.query_one("#chat-content", Markdown)
        full_content = ""
        for msg in self.messages:
            role_prefix = "**You**" if msg["role"] == "user" else "**Assistant**"
            full_content += f"\n\n{role_prefix} ({msg['timestamp']})\n\n{msg['content']}\n\n---"
        
        # Update with markdown string
        content_widget.update(full_content)
        self.scroll_end(animate=False)

    def clear_messages(self):
        """Clear all messages"""
        self.messages = []
        content_widget = self.query_one("#chat-content", Markdown)
        content_widget.update("")
