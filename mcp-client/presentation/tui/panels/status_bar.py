"""
Status Bar Component
Displays connection status, tool count, and current model
"""
from textual.widgets import Static
from textual.reactive import reactive


class StatusBar(Static):
    """Barra de estado inferior"""

    connection_status = reactive("🔴 Disconnected")
    current_model = reactive("Not set")
    tools_count = reactive(0)
    resources_count = reactive(0)

    def render(self) -> str:
        return (
            f"{self.connection_status} | "
            f"📦 Tools: {self.tools_count} | "
            f"📚 Resources: {self.resources_count} | "
            f"🤖 {self.current_model}"
        )
