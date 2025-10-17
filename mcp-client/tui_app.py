"""
Macro MCP - Textual TUI Application
Modern Terminal User Interface for Economic Analysis
"""
import asyncio
import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import json

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Header,
    Footer,
    Input,
    Static,
    Button,
    DataTable,
    Label,
    Markdown,
    TabbedContent,
    TabPane,
)
from textual.message import Message
from textual.reactive import reactive

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic
from dotenv import load_dotenv
from contextlib import AsyncExitStack

from utils import ConversationHistory, ResourceCache

# Setup logging for debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# NEW: Import GUI backend (v0.4.0)
try:
    from gui_backend import get_gui_backend, can_display_gui
    GUI_BACKEND_AVAILABLE = True
    logger.info("✅ GUI backend imported successfully")
except ImportError as e:
    GUI_BACKEND_AVAILABLE = False
    get_gui_backend = None
    can_display_gui = lambda: False
    logger.warning(f"⚠️ GUI backend not available: {e}")

# Import Google Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

# Import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

load_dotenv()

# GUI configuration (v0.4.0)
GUI_AUTO_OPEN = os.getenv("GUI_AUTO_OPEN", "true").lower() == "true"
logger.info(f"GUI_AUTO_OPEN = {GUI_AUTO_OPEN}")

# ==================== LLM PROVIDERS CONFIGURATION ====================

LLM_PROVIDERS = {
    "claude": {
        "name": "Anthropic Claude",
        "models": {
            "sonnet-4.5": {
                "id": "claude-sonnet-4-5-20250929",
                "name": "Claude Sonnet 4.5",
                "description": "Latest Sonnet, most capable"
            },
            "sonnet-3.7": {
                "id": "claude-3-7-sonnet-20250219",
                "name": "Claude 3.7 Sonnet",
                "description": "Balanced performance"
            },
            "sonnet-4": {
                "id": "claude-sonnet-4-20250514",
                "name": "Claude Sonnet 4",
                "description": "High capability"
            },
            "opus-4.1": {
                "id": "claude-opus-4-1-20250805",
                "name": "Claude Opus 4.1",
                "description": "Most intelligent"
            },
            "opus-4": {
                "id": "claude-opus-4-20250514",
                "name": "Claude Opus 4",
                "description": "Powerful reasoning"
            },
            "haiku-3.5": {
                "id": "claude-3-5-haiku-20241022",
                "name": "Claude 3.5 Haiku",
                "description": "Fastest, most affordable"
            }
        },
        "default": "sonnet-3.7"
    },
    "openai": {
        "name": "OpenAI GPT",
        "models": {
            "gpt-4o": {
                "id": "gpt-4o",
                "name": "GPT-4o",
                "description": "Latest model, fast and capable"
            },
            "gpt-4-turbo": {
                "id": "gpt-4-turbo-preview",
                "name": "GPT-4 Turbo",
                "description": "High capability, balanced"
            },
            "gpt-4": {
                "id": "gpt-4",
                "name": "GPT-4",
                "description": "Original GPT-4"
            },
            "gpt-3.5-turbo": {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "description": "Fast and affordable"
            }
        },
        "default": "gpt-4o"
    },
    "gemini": {
        "name": "Google Gemini",
        "models": {
            "flash-2.0": {
                "id": "gemini-2.0-flash-exp",
                "name": "Gemini 2.0 Flash",
                "description": "Fast (⚠️ No tool support)"
            },
            "pro-1.5": {
                "id": "gemini-1.5-pro",
                "name": "Gemini 1.5 Pro",
                "description": "Advanced (⚠️ No tool support)"
            },
            "flash-1.5": {
                "id": "gemini-1.5-flash",
                "name": "Gemini 1.5 Flash",
                "description": "Balanced (⚠️ No tool support)"
            }
        },
        "default": "flash-2.0"
    }
}

class ChatPanel(VerticalScroll):
    """Panel principal de chat"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.messages = []
        self.message_timestamps = {}  # Store timestamps for relative calculation

    def _get_relative_time(self, message_time: datetime) -> str:
        """Calculate relative time string from message timestamp"""
        now = datetime.now()
        delta = now - message_time
        
        if delta < timedelta(seconds=10):
            return "just now"
        elif delta < timedelta(minutes=1):
            seconds = int(delta.total_seconds())
            return f"{seconds}s ago"
        elif delta < timedelta(hours=1):
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes}m ago"
        elif delta < timedelta(days=1):
            hours = int(delta.total_seconds() / 3600)
            return f"{hours}h ago"
        elif delta < timedelta(days=7):
            days = delta.days
            return f"{days}d ago"
        else:
            return message_time.strftime("%Y-%m-%d")

    def add_message(self, role: str, content: str):
        """Agregar un nuevo mensaje al chat"""
        message_time = datetime.now()
        timestamp_abs = message_time.strftime("%H:%M:%S")
        timestamp_rel = self._get_relative_time(message_time)
        
        icon = "🧑" if role == "user" else "🤖"
        role_name = "You" if role == "user" else "Claude"
        
        # Crear widgets directamente sin contenedor
        header_class = "user-header" if role == "user" else "assistant-header"
        content_class = "user-content" if role == "user" else "assistant-content"
        
        # Header with relative and absolute time
        header_text = f"{icon} {role_name} • {timestamp_rel} ({timestamp_abs})"
        header = Label(header_text, classes=header_class)
        message_widget = Markdown(content, classes=content_class)
        
        # Store timestamp for future relative time updates
        message_id = len(self.messages)
        self.message_timestamps[message_id] = {
            "time": message_time,
            "header": header
        }
        
        self.mount(header)
        self.mount(message_widget)
        self.messages.extend([header, message_widget])
        self.scroll_end(animate=True)

    def update_relative_timestamps(self):
        """Update all relative timestamps (called periodically)"""
        for msg_id, msg_data in self.message_timestamps.items():
            message_time = msg_data["time"]
            header_widget = msg_data["header"]
            
            timestamp_abs = message_time.strftime("%H:%M:%S")
            timestamp_rel = self._get_relative_time(message_time)
            
            # Extract icon and role name from current header
            current_text = header_widget.render()
            if "🧑" in current_text:
                icon = "🧑"
                role_name = "You"
            else:
                icon = "🤖"
                role_name = "Claude"
            
            # Update header text
            new_header_text = f"{icon} {role_name} • {timestamp_rel} ({timestamp_abs})"
            header_widget.update(new_header_text)

    def clear_messages(self):
        """Limpiar todos los mensajes"""
        for message in self.messages:
            message.remove()
        self.messages.clear()
        self.message_timestamps.clear()


class DatasetPanel(VerticalScroll):
    """Panel lateral para mostrar datasets disponibles"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.datasets_info = []

    def compose(self) -> ComposeResult:
        yield Label("📊 Recent Datasets", classes="panel-title")
        yield Static(id="datasets-list", classes="datasets-list")
        yield Button("🔄 Refresh", id="refresh-datasets", variant="primary")
        yield Button("➕ Build New", id="build-dataset", variant="success")

    async def update_datasets(self, datasets_text: str):
        """Actualizar la lista de datasets"""
        datasets_widget = self.query_one("#datasets-list", Static)
        datasets_widget.update(datasets_text)


class HistoryPanel(VerticalScroll):
    """Panel de historial de conversaciones"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.history_items = []

    def compose(self) -> ComposeResult:
        yield Label("📚 Conversation History", classes="panel-title")
        yield Input(placeholder="🔍 Search history...", id="history-search")
        yield Static(id="history-list", classes="history-list")
        yield Button("🗑️ Clear History", id="clear-history", variant="error")

    def update_history(self, history_items: list):
        """Actualizar la lista de historial"""
        self.history_items = history_items
        history_widget = self.query_one("#history-list", Static)

        # Formatear items del historial
        history_text = ""
        for i, item in enumerate(history_items[-10:], 1):  # Últimos 10
            timestamp = item.get('timestamp', 'Unknown')
            query = item.get('query', '')[:50]  # Truncar a 50 chars
            history_text += f"\n{i}. {timestamp}\n   {query}...\n"

        history_widget.update(history_text or "No history yet")


class StatusBar(Static):
    """Barra de estado inferior"""

    connection_status = reactive("⚪ Disconnected")
    tools_count = reactive(0)
    resources_count = reactive(0)
    message_count = reactive(0)
    current_model = reactive("")

    def render(self) -> str:
        model_display = f" | 🤖 {self.current_model}" if self.current_model else ""
        return f"{self.connection_status} | 🔧 {self.tools_count} tools | 📦 {self.resources_count} resources | 💬 {self.message_count} messages{model_display}"


class MacroMCPApp(App):
    """Aplicación TUI principal de Macro MCP"""

    CSS = """
    Screen {
        background: $surface;
    }

    /* Layout principal */
    #main-container {
        layout: horizontal;
        height: 1fr;
    }

    #sidebar {
        width: 30;
        background: $panel;
        border-right: solid $primary;
    }

    #chat-container {
        width: 1fr;
        layout: vertical;
    }

    #chat-panel {
        height: 1fr;
        background: $surface;
        padding: 1;
    }

    #input-container {
        height: auto;
        background: $panel;
        padding: 1;
        border-top: solid $primary;
    }

    /* Headers de mensajes */
    .user-header {
        color: $success;
        text-style: bold;
        margin: 1 0 0 0;
    }

    .assistant-header {
        color: $primary;
        text-style: bold;
        margin: 2 0 0 0;
    }

    /* Contenido de mensajes */
    .user-content {
        background: $boost;
        padding: 1;
        margin: 0 0 1 2;
        border-left: thick $success;
    }

    .assistant-content {
        background: $panel;
        padding: 1;
        margin: 0 0 1 2;
        border-left: thick $primary;
    }

    /* Paneles laterales */
    .panel-title {
        background: $primary;
        color: $text;
        padding: 1;
        text-style: bold;
        text-align: center;
    }

    .datasets-list, .history-list {
        padding: 1;
        height: 1fr;
    }

    /* Tabs */
    TabbedContent {
        height: 1fr;
    }

    TabPane {
        padding: 0;
    }

    /* Input */
    Input {
        width: 1fr;
    }

    /* Botones */
    Button {
        margin: 1;
        width: 100%;
    }

    /* Status bar */
    StatusBar {
        background: $panel;
        color: $text-muted;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("ctrl+d", "toggle_sidebar", "Toggle Datasets", show=True),
        Binding("ctrl+h", "toggle_history", "Toggle History", show=False),
        Binding("ctrl+n", "new_conversation", "New Chat", show=True),
        Binding("ctrl+s", "save_conversation", "Save", show=True),
        Binding("ctrl+r", "refresh_resources", "Refresh", show=False),
        Binding("ctrl+c", "copy_to_clipboard", "Copy", show=False),
        Binding("escape", "focus_input", "Focus Input", show=False),
    ]

    TITLE = "Macro MCP - Economic Analysis System"
    SUB_TITLE = "Powered by Multi-LLM AI & FRED Data"

    def __init__(self):
        super().__init__()

        # MCP Session
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

        # LLM Configuration
        self.current_provider = None
        self.current_model_key = None
        self.current_model_id = None
        
        # LLM Clients
        self.anthropic_client = None
        self.openai_client = None
        self.gemini_model = None
        
        # Initialize LLM
        self._initialize_llm()

        # Conversation
        self.conversation_history = []
        self.history_manager = ConversationHistory(max_items=100)
        self.cache = ResourceCache(ttl=300)

        # State
        self.tools_available = []
        self.resources_available = []
        self.sidebar_visible = True
        self.current_tab = "datasets"

        # GUI backend (v0.4.0)
        if GUI_BACKEND_AVAILABLE:
            try:
                self.gui_backend = get_gui_backend()
                logger.info(f"GUI backend initialized: {self.gui_backend.backend}")
                logger.info(f"Can display GUI: {self.gui_backend.can_display_gui()}")
            except Exception as e:
                logger.error(f"Failed to initialize GUI backend: {e}")
                self.gui_backend = None
        else:
            self.gui_backend = None
            logger.warning("GUI backend not available")

    def _initialize_llm(self):
        """Initialize LLM clients and set default model"""
        # Get API keys
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        # Initialize Claude
        if anthropic_key:
            try:
                self.anthropic_client = Anthropic(api_key=anthropic_key)
            except Exception as e:
                self.anthropic_client = None
        
        # Initialize OpenAI
        if openai_key and OPENAI_AVAILABLE:
            try:
                self.openai_client = OpenAI(api_key=openai_key)
            except Exception as e:
                self.openai_client = None
        
        # Initialize Gemini
        if gemini_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=gemini_key)
            except Exception as e:
                pass
        
        # Set default model from .env or fallback
        default_model = os.getenv("DEFAULT_MODEL")
        default_provider = os.getenv("DEFAULT_LLM_PROVIDER", "claude")
        
        if default_model:
            # Try to find provider and model key from full model ID
            for provider, config in LLM_PROVIDERS.items():
                for key, model_info in config["models"].items():
                    if model_info["id"] == default_model:
                        self._set_model(provider, key)
                        return
        
        # Fallback: Use default from first available provider
        if self.anthropic_client:
            default_key = LLM_PROVIDERS["claude"]["default"]
            self._set_model("claude", default_key)
        elif self.openai_client:
            default_key = LLM_PROVIDERS["openai"]["default"]
            self._set_model("openai", default_key)
        elif GEMINI_AVAILABLE and gemini_key:
            default_key = LLM_PROVIDERS["gemini"]["default"]
            self._set_model("gemini", default_key)
        else:
            # No providers available
            self.current_model_id = "No LLM available"

    def _set_model(self, provider: str, model_key: str):
        """Set current model by provider and model key"""
        if provider not in LLM_PROVIDERS:
            return False
        
        if model_key not in LLM_PROVIDERS[provider]["models"]:
            return False
        
        model_info = LLM_PROVIDERS[provider]["models"][model_key]
        
        self.current_provider = provider
        self.current_model_key = model_key
        self.current_model_id = model_info["id"]
        
        # Initialize Gemini model if needed
        if provider == "gemini" and GEMINI_AVAILABLE:
            try:
                self.gemini_model = genai.GenerativeModel(model_info["id"])
            except Exception as e:
                return False
        
        # Update status bar
        try:
            status_bar = self.query_one("#status-bar", StatusBar)
            status_bar.current_model = f"{LLM_PROVIDERS[provider]['name']} - {model_info['name']}"
        except:
            pass
        
        return True

    def compose(self) -> ComposeResult:
        """Crear el layout de la aplicación"""
        yield Header()

        with Container(id="main-container"):
            # Sidebar con tabs
            with Container(id="sidebar"):
                with TabbedContent(initial="datasets-tab"):
                    with TabPane("Datasets", id="datasets-tab"):
                        yield DatasetPanel(id="dataset-panel")
                    with TabPane("History", id="history-tab"):
                        yield HistoryPanel(id="history-panel")

            # Área principal de chat
            with Container(id="chat-container"):
                yield ChatPanel(id="chat-panel")

                with Container(id="input-container"):
                    yield Input(
                        placeholder="Ask about economic data... (ESC to focus)",
                        id="chat-input"
                    )

        yield StatusBar(id="status-bar")
        yield Footer()

    async def on_mount(self) -> None:
        """Ejecutar al montar la aplicación"""
        # Conectar al servidor MCP
        await self.connect_to_mcp()

        # Cargar datasets iniciales
        await self.load_datasets()

        # Focus en el input
        self.query_one("#chat-input", Input).focus()

        # Set up periodic timestamp updates (every 30 seconds)
        self.set_interval(30, self.update_timestamps)

        # Mensaje de bienvenida
        chat_panel = self.query_one("#chat-panel", ChatPanel)
        chat_panel.add_message(
            "assistant",
            """# Welcome to Macro MCP! 🎉

I'm your AI assistant for macroeconomic analysis.

**What I can help you with:**
- 📊 Search and fetch FRED economic data
- 📈 Create publication-quality plots
- 🔄 Build custom datasets with transformations
- 📉 Analyze time series (stationarity tests)
- 💾 Export data in CSV/Excel formats

**Try asking:**
- "Show me GDP data from 2020 to 2024"
- "Plot unemployment vs inflation"
- "Build a dataset with UNRATE and CPIAUCSL (YoY)"

**Slash commands:** (type `/help` for full list)
- `/tools` - List all MCP tools
- `/model` - Show/change LLM model
- `/examples` - Show example queries
- `/status` - Show connection status
- `/save` - Save conversation

**Keyboard shortcuts:**
- `Ctrl+D` - Toggle datasets panel
- `Ctrl+N` - New conversation
- `Ctrl+S` - Save conversation
- `ESC` - Focus input
- `Q` - Quit

Type your question or `/help` below to get started!
"""
        )

    def update_timestamps(self):
        """Periodic callback to update relative timestamps"""
        try:
            chat_panel = self.query_one("#chat-panel", ChatPanel)
            chat_panel.update_relative_timestamps()
        except Exception:
            pass  # Ignore errors if panel not available

    async def connect_to_mcp(self) -> None:
        """Conectar al servidor MCP"""
        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.connection_status = "🟡 Connecting..."

        try:
            server_params = StdioServerParameters(
                command="uv",
                args=[
                    "--directory",
                    "C:/Users/agust/OneDrive/Documentos/VSCODE/macro/macro/app",
                    "run",
                    "python",
                    "server_mcp.py",
                ],
                env=None,
            )

            # Crear transporte y sesión
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            self.stdio, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(self.stdio, self.write)
            )

            # Inicializar sesión
            await self.session.initialize()

            # Obtener herramientas
            response = await self.session.list_tools()
            self.tools_available = response.tools

            # Obtener recursos
            resources_response = await self.session.list_resources()
            self.resources_available = resources_response.resources

            # Actualizar status
            status_bar.connection_status = "🟢 Connected"
            status_bar.tools_count = len(self.tools_available)
            status_bar.resources_count = len(self.resources_available)

        except Exception as e:
            status_bar.connection_status = f"🔴 Error: {str(e)[:30]}"
            self.notify(
                f"Failed to connect to MCP server: {str(e)}",
                severity="error",
                timeout=10
            )

    async def load_datasets(self) -> None:
        """Cargar lista de datasets desde el recurso MCP"""
        try:
            if not self.session:
                return

            # Leer recurso fred://datasets/recent
            resources_response = await self.session.list_resources()

            for resource in resources_response.resources:
                if str(resource.uri) == "fred://datasets/recent":
                    result = await self.session.read_resource(resource.uri)
                    datasets_text = result.contents[0].text if result.contents else "No datasets found"

                    # Actualizar panel de datasets
                    dataset_panel = self.query_one("#dataset-panel", DatasetPanel)
                    await dataset_panel.update_datasets(datasets_text)
                    break
        except Exception as e:
            self.notify(f"Error loading datasets: {str(e)}", severity="warning")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Manejar envío de mensaje del usuario"""
        if event.input.id != "chat-input":
            return

        query = event.value.strip()
        if not query:
            return

        # Limpiar input
        event.input.value = ""

        # Detectar si es un comando slash
        if query.startswith("/"):
            await self.handle_slash_command(query)
            return

        # Agregar mensaje del usuario al chat
        chat_panel = self.query_one("#chat-panel", ChatPanel)
        chat_panel.add_message("user", query)

        # Mostrar indicador de "pensando"
        thinking_label = Label("⏳ Thinking...", classes="assistant-header")
        chat_panel.mount(thinking_label)
        chat_panel.scroll_end(animate=True)

        # Procesar query con LLM
        try:
            response = await self.process_query(query)

            # Remover indicador de "pensando"
            thinking_label.remove()

            # Agregar respuesta
            chat_panel.add_message("assistant", response)

            # Actualizar contador de mensajes
            status_bar = self.query_one("#status-bar", StatusBar)
            status_bar.message_count = len(self.conversation_history)

        except Exception as e:
            thinking_label.remove()
            chat_panel.add_message("assistant", f"❌ Error: {str(e)}")
            self.notify(f"Error processing query: {str(e)}", severity="error")

    async def handle_slash_command(self, command_text: str) -> None:
        """Manejar comandos slash"""
        chat_panel = self.query_one("#chat-panel", ChatPanel)

        # Parsear comando y argumentos
        parts = command_text[1:].split(maxsplit=1)
        cmd_name = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        # Agregar comando al chat
        chat_panel.add_message("user", command_text)

        # Ejecutar comando correspondiente
        try:
            if cmd_name in ["help", "h", "?"]:
                await self.cmd_help(args)
            elif cmd_name in ["tools", "t"]:
                await self.cmd_tools(args)
            elif cmd_name in ["resources", "r"]:
                await self.cmd_resources(args)
            elif cmd_name in ["clear", "cls"]:
                await self.cmd_clear(args)
            elif cmd_name in ["history", "hist"]:
                await self.cmd_history(args)
            elif cmd_name in ["new", "reset"]:
                self.action_new_conversation()
            elif cmd_name in ["status", "info"]:
                await self.cmd_status(args)
            elif cmd_name in ["save"]:
                self.action_save_conversation()
            elif cmd_name in ["load"]:
                await self.cmd_load(args)
            elif cmd_name in ["export"]:
                await self.cmd_export(args)
            elif cmd_name in ["search", "find"]:
                await self.cmd_search(args)
            elif cmd_name in ["stats", "statistics"]:
                await self.cmd_stats(args)
            elif cmd_name in ["examples", "ejemplos", "ex"]:
                await self.cmd_examples(args)
            elif cmd_name in ["model", "m"]:
                await self.cmd_model(args)
            elif cmd_name in ["exit", "quit", "q"]:
                self.exit()
            else:
                chat_panel.add_message("assistant", f"❌ Unknown command: `/{cmd_name}`\n\nType `/help` to see available commands.")
        except Exception as e:
            chat_panel.add_message("assistant", f"❌ Error executing command: {str(e)}")
            self.notify(f"Command error: {str(e)}", severity="error")

    # ==================== NEW: MODEL COMMAND ====================

    async def cmd_model(self, args: str) -> None:
        """Cambiar modelo de LLM"""
        chat_panel = self.query_one("#chat-panel", ChatPanel)

        if not args.strip():
            # Show current model and available options
            current_info = f"**Current Model:** {self.current_provider} - {self.current_model_key} ({self.current_model_id})\n\n"
            
            available_text = "**Available Models:**\n\n"
            
            # Claude models
            if self.anthropic_client:
                available_text += "**Claude (Anthropic):** ✅ Full MCP tool support\n"
                for key, model_info in LLM_PROVIDERS["claude"]["models"].items():
                    marker = "✅" if self.current_provider == "claude" and self.current_model_key == key else "  "
                    available_text += f"{marker} `claude:{key}` - {model_info['name']}\n"
                    available_text += f"    {model_info['description']}\n"
                available_text += "\n"
            
            # OpenAI models
            if self.openai_client:
                available_text += "**OpenAI (GPT):** ✅ Full MCP tool support\n"
                for key, model_info in LLM_PROVIDERS["openai"]["models"].items():
                    marker = "✅" if self.current_provider == "openai" and self.current_model_key == key else "  "
                    available_text += f"{marker} `openai:{key}` - {model_info['name']}\n"
                    available_text += f"    {model_info['description']}\n"
                available_text += "\n"
            
            # Gemini models
            if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"):
                available_text += "**Gemini (Google):** ❌ No MCP tool support\n"
                for key, model_info in LLM_PROVIDERS["gemini"]["models"].items():
                    marker = "✅" if self.current_provider == "gemini" and self.current_model_key == key else "  "
                    available_text += f"{marker} `gemini:{key}` - {model_info['name']}\n"
                    available_text += f"    {model_info['description']}\n"
                available_text += "\n"
            
            usage_text = "\n**Usage:**\n`/model <provider>:<model_key>`\n\n**Examples:**\n- `/model claude:sonnet-4.5`\n- `/model openai:gpt-4o`\n- `/model openai:gpt-3.5-turbo` (fast & cheap)\n- `/model gemini:flash-2.0` (theory only)"
            
            chat_panel.add_message("assistant", current_info + available_text + usage_text)
            return
        
        # Parse provider:model_key
        if ":" not in args:
            chat_panel.add_message("assistant", "❌ Invalid format. Use `/model <provider>:<model_key>`\n\nExample: `/model claude:sonnet-3.7`")
            return
        
        provider, model_key = args.strip().split(":", 1)
        provider = provider.lower()
        model_key = model_key.lower()
        
        # Validate provider
        if provider not in LLM_PROVIDERS:
            chat_panel.add_message("assistant", f"❌ Unknown provider: `{provider}`\n\nAvailable: `claude`, `gemini`")
            return
        
        # Check if provider is available
        if provider == "claude" and not self.anthropic_client:
            chat_panel.add_message("assistant", "❌ Claude not available. Check ANTHROPIC_API_KEY in .env")
            return
        
        if provider == "openai" and not self.openai_client:
            chat_panel.add_message("assistant", "❌ OpenAI not available. Install openai package and check OPENAI_API_KEY in .env")
            return
        
        if provider == "gemini" and (not GEMINI_AVAILABLE or not os.getenv("GEMINI_API_KEY")):
            chat_panel.add_message("assistant", "❌ Gemini not available. Install google-generativeai and check GEMINI_API_KEY in .env")
            return
        
        # Validate model key
        if model_key not in LLM_PROVIDERS[provider]["models"]:
            available_keys = ", ".join(LLM_PROVIDERS[provider]["models"].keys())
            chat_panel.add_message("assistant", f"❌ Unknown model: `{model_key}`\n\n**Available for {provider}:** {available_keys}")
            return
        
        # Set model
        success = self._set_model(provider, model_key)
        
        if success:
            model_info = LLM_PROVIDERS[provider]["models"][model_key]
            chat_panel.add_message("assistant", f"✅ Switched to: **{LLM_PROVIDERS[provider]['name']} - {model_info['name']}**\n\nModel ID: `{model_info['id']}`")
            self.notify(f"Model: {provider}:{model_key}", severity="information")
            
            # Update status bar
            status_bar = self.query_one("#status-bar", StatusBar)
            status_bar.current_model = f"{LLM_PROVIDERS[provider]['name']} - {model_info['name']}"
        else:
            chat_panel.add_message("assistant", f"❌ Failed to switch model. Please try again.")

    # ==================== UPDATED: PROCESS QUERY ====================

    async def process_query(self, query: str) -> str:
        """Procesar query del usuario usando LLM + MCP tools"""
        # Agregar al historial
        self.conversation_history.append({
            "role": "user",
            "content": query
        })

        # Obtener herramientas disponibles
        available_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
            }
            for tool in self.tools_available
        ]

        # Call LLM based on provider
        if self.current_provider == "claude":
            return await self._process_with_claude(available_tools)
        elif self.current_provider == "openai":
            return await self._process_with_openai(available_tools)
        elif self.current_provider == "gemini":
            return await self._process_with_gemini(available_tools)
        else:
            return "❌ No LLM provider configured"

    async def _process_with_claude(self, available_tools: List[Dict]) -> str:
        """Process query with Claude"""
        # Llamar a Claude
        claude_response = self.anthropic_client.messages.create(
            model=self.current_model_id,
            max_tokens=4096,
            messages=self.conversation_history.copy(),
            tools=available_tools,
        )

        # Procesar respuesta
        assistant_content = []
        tool_results = []
        tools_used = []
        formatted_tool_outputs = []
        final_output = []

        for content in claude_response.content:
            if content.type == "text":
                assistant_content.append({"type": "text", "text": content.text})
                final_output.append(content.text)
            elif content.type == "tool_use":
                assistant_content.append({
                    "type": "tool_use",
                    "id": content.id,
                    "name": content.name,
                    "input": content.input
                })

                # Ejecutar herramienta
                tool_name = content.name
                tool_args = content.input or {}
                tools_used.append(tool_name)

                try:
                    # Mostrar que se está ejecutando la tool
                    chat_panel = self.query_one("#chat-panel", ChatPanel)
                    args_preview = ", ".join([f"{k}={str(v)[:20]}" for k, v in list(tool_args.items())[:2]])
                    chat_panel.add_message("assistant", f"🔧 **Ejecutando:** `{tool_name}({args_preview}...)`")

                    # ==================== SUPPRESS LOGGING DURING TOOL CALL ====================
                    # Temporarily suppress all logging to prevent terminal corruption
                    old_level = logging.root.level
                    logging.root.setLevel(logging.CRITICAL + 1)  # Disable all logs
                    
                    try:
                        # Call tool (now silent)
                        tool_result = await self.session.call_tool(tool_name, tool_args)
                        
                        result_text = (
                            tool_result.content[0].text
                            if tool_result.content and hasattr(tool_result.content[0], "text")
                            else str(tool_result.content)
                        )
                    finally:
                        # Restore logging level
                        logging.root.setLevel(old_level)
                    # ==================== END SUPPRESSION ====================

                    # Formatear resultado (NOW plot_path should exist)
                    formatted_result = self._format_tool_result(tool_name, result_text)
                    if formatted_result != result_text:
                        formatted_tool_outputs.append(formatted_result)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": content.id,
                        "content": result_text
                    })
                except Exception as e:
                    error_msg = f"❌ Error ejecutando `{tool_name}`: {str(e)}"
                    chat_panel.add_message("assistant", error_msg)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": content.id,
                        "content": f"Error: {str(e)}",
                        "is_error": True
                    })

        # Guardar respuesta de Claude
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_content
        })

        # Mostrar resultados formateados de tools
        if formatted_tool_outputs:
            chat_panel = self.query_one("#chat-panel", ChatPanel)
            for formatted_output in formatted_tool_outputs:
                chat_panel.add_message("assistant", formatted_output)

        # Si hubo tool use, obtener respuesta final
        if tool_results:
            self.conversation_history.append({
                "role": "user",
                "content": tool_results
            })

            followup = self.anthropic_client.messages.create(
                model=self.current_model_id,
                max_tokens=4096,
                messages=self.conversation_history,
            )

            followup_content = []
            for content in followup.content:
                if content.type == "text":
                    followup_content.append({"type": "text", "text": content.text})
                    final_output.append(content.text)

            self.conversation_history.append({
                "role": "assistant",
                "content": followup_content
            })

        # Guardar en history manager
        final_response = "\n".join(final_output) if final_output else "No response generated."
        self.history_manager.add(
            query=self.conversation_history[-2]["content"] if len(self.conversation_history) >= 2 else "",
            response=final_response,
            tools_used=tools_used
        )

        # Actualizar panel de historial
        history_panel = self.query_one("#history-panel", HistoryPanel)
        history_panel.update_history(list(self.history_manager.history))

        return final_response

    async def _process_with_openai(self, available_tools: List[Dict]) -> str:
        """Process query with OpenAI"""
        if not self.openai_client:
            return "❌ OpenAI client not initialized"
        
        try:
            # Convert MCP tools to OpenAI format
            openai_tools = self._convert_tools_to_openai_format(available_tools)
            
            # Convert conversation history to OpenAI format
            openai_messages = []
            for msg in self.conversation_history:
                if msg["role"] == "user":
                    openai_messages.append({
                        "role": "user",
                        "content": msg["content"] if isinstance(msg["content"], str) else json.dumps(msg["content"])
                    })
                elif msg["role"] == "assistant":
                    # Handle complex content
                    if isinstance(msg["content"], list):
                        text_parts = [c.get("text", "") for c in msg["content"] if c.get("type") == "text"]
                        if text_parts:
                            openai_messages.append({
                                "role": "assistant",
                                "content": "\n".join(text_parts)
                            })
                    elif isinstance(msg["content"], str):
                        openai_messages.append({
                            "role": "assistant",
                            "content": msg["content"]
                        })
            
            # Call OpenAI
            response = self.openai_client.chat.completions.create(
                model=self.current_model_id,
                messages=openai_messages,
                tools=openai_tools if openai_tools else None,
                tool_choice="auto" if openai_tools else None,
                max_tokens=4096,
                temperature=0.7
            )
            
            # Process response
            message = response.choices[0].message
            final_output = []
            tools_used = []
            
            # Handle text response
            if message.content:
                final_output.append(message.content)
            
            # Handle tool calls
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    tools_used.append(tool_name)
                    
                    try:
                        # Show execution
                        chat_panel = self.query_one("#chat-panel", ChatPanel)
                        args_preview = ", ".join([f"{k}={str(v)[:20]}" for k, v in list(tool_args.items())[:2]])
                        chat_panel.add_message("assistant", f"🔧 **Ejecutando:** `{tool_name}({args_preview}...)`")
                        
                        # Execute MCP tool
                        tool_result = await self.session.call_tool(tool_name, tool_args)
                        result_text = (
                            tool_result.content[0].text
                            if tool_result.content and hasattr(tool_result.content[0], "text")
                            else str(tool_result.content)
                        )
                        
                        # Format result
                        formatted_result = self._format_tool_result(tool_name, result_text)
                        if formatted_result != result_text:
                            chat_panel.add_message("assistant", formatted_result)
                        
                        # Add tool result to conversation for follow-up
                        openai_messages.append({
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [tool_call]
                        })
                        openai_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result_text
                        })
                        
                    except Exception as e:
                        # Capturar el mensaje de error inmediatamente
                        error_message = str(e)
                        error_msg = f"❌ Error ejecutando `{tool_name}`: {error_message}"
                        
                        # Mostrar error en el chat (puede fallar, pero ya tenemos error_message)
                        try:
                            chat_panel.add_message("assistant", error_msg)
                        except:
                            pass  # Ignorar si no se puede mostrar en UI
                
                # Get follow-up response with tool results
                if openai_messages[-1]["role"] == "tool":
                    followup = self.openai_client.chat.completions.create(
                        model=self.current_model_id,
                        messages=openai_messages,
                        max_tokens=4096,
                        temperature=0.7
                    )
                    if followup.choices[0].message.content:
                        final_output.append(followup.choices[0].message.content)
            
            # Save to history
            final_response = "\n".join(final_output) if final_output else "No response generated."
            
            self.conversation_history.append({
                "role": "assistant",
                "content": final_response
            })
            
            self.history_manager.add(
                query=self.conversation_history[-2]["content"] if len(self.conversation_history) >= 2 else "",
                response=final_response,
                tools_used=tools_used
            )
            
            # Update history panel
            history_panel = self.query_one("#history-panel", HistoryPanel)
            history_panel.update_history(list(self.history_manager.history))
            
            return final_response
            
        except Exception as e:
            return f"❌ OpenAI error: {str(e)}"

    def _convert_tools_to_openai_format(self, mcp_tools: List[Dict]) -> List[Dict]:
        """Convert MCP tools to OpenAI function calling format"""
        openai_tools = []
        for tool in mcp_tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"]
                }
            })
        return openai_tools

    # ==================== SLASH COMMAND HANDLERS ====================

    async def cmd_help(self, args: str) -> None:
        """Mostrar ayuda de comandos"""
        chat_panel = self.query_one("#chat-panel", ChatPanel)

        help_text = """# 📚 Available Commands

## Chat & Conversation
- `/new` - Start a new conversation
- `/clear` - Clear the chat screen
- `/save [name]` - Save conversation to file
- `/load <name>` - Load a saved conversation
- `/export <format>` - Export conversation (md/json)

## MCP Tools & Resources
- `/tools [name]` - List all tools or inspect specific tool
- `/resources [uri]` - List resources or read specific resource
- `/examples` - Show example queries

## LLM Management
- `/model [provider:model]` - Show or change LLM model
  - Examples: `/model claude:sonnet-4.5`, `/model gemini:flash-2.0`

## History & Search
- `/history` - Show conversation history
- `/search <keyword>` - Search in history
- `/stats` - Show usage statistics

## Information
- `/status` - Show client connection status
- `/help` - Show this help message

## Exit
- `/exit` - Exit the application (or press Q)

**Keyboard Shortcuts:**
- `Ctrl+N` - New conversation
- `Ctrl+S` - Save conversation
- `Ctrl+D` - Toggle sidebar
- `Ctrl+R` - Refresh datasets
- `ESC` - Focus input
- `Q` - Quit
"""
        chat_panel.add_message("assistant", help_text)

    async def cmd_tools(self, args: str) -> None:
        """Listar herramientas o mostrar detalles"""
        chat_panel = self.query_one("#chat-panel", ChatPanel)

        if not self.session:
            chat_panel.add_message("assistant", "❌ Not connected to MCP server")
            return

        try:
            response = await self.session.list_tools()
            tools = response.tools

            if not tools:
                chat_panel.add_message("assistant", "⚠️ No tools available")
                return

            if args.strip():
                # Mostrar detalles de herramienta específica
                tool_name = args.strip()
                tool = next((t for t in tools if t.name == tool_name), None)

                if not tool:
                    chat_panel.add_message("assistant", f"❌ Tool not found: `{tool_name}`\n\nUse `/tools` to see all available tools.")
                    return

                # Formatear detalles de la tool
                schema = json.dumps(tool.inputSchema, indent=2) if hasattr(tool, 'inputSchema') else "N/A"

                details = f"""### 🔧 {tool.name}

**Description:**
{tool.description}

**Input Schema:**
```json
{schema}
```
"""
                chat_panel.add_message("assistant", details)
            else:
                # Listar todas las herramientas
                tools_list = f"### 🔧 Available Tools ({len(tools)})\n\n"
                for i, tool in enumerate(tools, 1):
                    desc = tool.description[:80] + "..." if len(tool.description) > 80 else tool.description
                    tools_list += f"{i}. **{tool.name}**\n   {desc}\n\n"

                tools_list += "\n💡 Use `/tools <name>` to see details of a specific tool."
                chat_panel.add_message("assistant", tools_list)

        except Exception as e:
            chat_panel.add_message("assistant", f"❌ Error listing tools: {str(e)}")

    async def cmd_resources(self, args: str) -> None:
        """Listar recursos o leer uno específico"""
        chat_panel = self.query_one("#chat-panel", ChatPanel)

        if not self.session:
            chat_panel.add_message("assistant", "❌ Not connected to MCP server")
            return

        try:
            response = await self.session.list_resources()
            resources = response.resources

            if not resources:
                chat_panel.add_message("assistant", "⚠️ No resources available")
                return

            if args.strip():
                # Leer recurso específico
                resource_uri = args.strip()
                resource = next((r for r in resources if str(r.uri) == resource_uri), None)

                if not resource:
                    chat_panel.add_message("assistant", f"❌ Resource not found: `{resource_uri}`\n\nUse `/resources` to see all available resources.")
                    return

                # Leer contenido del recurso
                result = await self.session.read_resource(resource_uri)

                if result.contents:
                    content = result.contents[0]
                    content_text = content.text if hasattr(content, 'text') else str(content)

                    output = f"### 📦 Resource: `{resource_uri}`\n\n{content_text}"
                    chat_panel.add_message("assistant", output)
                else:
                    chat_panel.add_message("assistant", f"⚠️ Resource `{resource_uri}` is empty")
            else:
                # Listar todos los recursos
                resources_list = f"### 📦 Available Resources ({len(resources)})\n\n"
                for i, resource in enumerate(resources, 1):
                    uri = str(resource.uri)
                    name = resource.name if hasattr(resource, 'name') else uri
                    desc = resource.description[:80] + "..." if hasattr(resource, 'description') and len(resource.description) > 80 else ""
                    resources_list += f"{i}. **{name}**\n   URI: `{uri}`\n"
                    if desc:
                        resources_list += f"   {desc}\n"
                    resources_list += "\n"

                resources_list += "\n💡 Use `/resources <uri>` to read a specific resource."
                chat_panel.add_message("assistant", resources_list)

        except Exception as e:
            chat_panel.add_message("assistant", f"❌ Error listing resources: {str(e)}")

    async def cmd_clear(self, args: str) -> None:
        """Limpiar el panel de chat"""
        chat_panel = self.query_one("#chat-panel", ChatPanel)
        chat_panel.clear_messages()
        chat_panel.add_message("assistant", "✅ Chat cleared!")
        self.notify("Chat cleared", severity="information")

    async def cmd_history(self, args: str) -> None:
        """Mostrar historial de conversación"""
        chat_panel = self.query_one("#chat-panel", ChatPanel)

        if len(self.history_manager) == 0:
            chat_panel.add_message("assistant", "ℹ️ History is empty")
            return

        history_text = f"### 📚 Conversation History ({len(self.history_manager)} items)\n\n"

        for i, item in enumerate(list(self.history_manager.history)[-10:], 1):
            timestamp = item.get('timestamp', 'Unknown')
            query = item.get('query', '')[:60] + "..." if len(item.get('query', '')) > 60 else item.get('query', '')
            response = item.get('response', '')[:100] + "..." if len(item.get('response', '')) > 100 else item.get('response', '')
            tools = ", ".join(item.get('tools_used', [])) or "None"

            history_text += f"**{i}. {timestamp}**\n"
            history_text += f"   *Query:* {query}\n"
            history_text += f"   *Tools:* {tools}\n\n"

        history_text += "\n*Showing last 10 items*"
        chat_panel.add_message("assistant", history_text)

    async def cmd_status(self, args: str) -> None:
        """Mostrar estado del cliente"""
        chat_panel = self.query_one("#chat-panel", ChatPanel)

        try:
            tools_count = len(self.tools_available) if self.tools_available else 0
            resources_count = len(self.resources_available) if self.resources_available else 0

            history_count = len(self.conversation_history)
            total_conversations = len(self.history_manager)

            connection = "🟢 Connected" if self.session else "🔴 Disconnected"

            status_text = f"""### 📊 Client Status

**Connection:** {connection}
**MCP Tools:** {tools_count}
**MCP Resources:** {resources_count}
**Current Session Messages:** {history_count}
**Total Conversations:** {total_conversations}
**Cache Status:** {len(self.cache._cache)} cached items

**Server Path:** `C:/Users/agust/.../macro/app/server_mcp.py`
**Model:** claude-3-7-sonnet-20250219
"""
            chat_panel.add_message("assistant", status_text)

        except Exception as e:
            chat_panel.add_message("assistant", f"❌ Error getting status: {str(e)}")

    async def cmd_load(self, args: str) -> None:
        """Cargar conversación guardada"""
        chat_panel = self.query_one("#chat-panel", ChatPanel)

        if not args.strip():
            chat_panel.add_message("assistant", "❌ Please specify a filename\n\n**Usage:** `/load <filename>`")
            return

        filename = args.strip()
        if not filename.endswith('.json'):
            filename = f"{filename}.json"

        filepath = os.path.join("conversations", filename)

        try:
            count = self.history_manager.load_json(filepath)
            chat_panel.add_message("assistant", f"✅ Loaded conversation: **{count}** items\n\nFile: `{filepath}`")

            # Actualizar panel de historial
            history_panel = self.query_one("#history-panel", HistoryPanel)
            history_panel.update_history(list(self.history_manager.history))

            self.notify(f"Loaded {count} items", severity="information")
        except FileNotFoundError:
            chat_panel.add_message("assistant", f"❌ File not found: `{filepath}`")
        except Exception as e:
            chat_panel.add_message("assistant", f"❌ Error loading conversation: {str(e)}")

    async def cmd_export(self, args: str) -> None:
        """Exportar conversación"""
        chat_panel = self.query_one("#chat-panel", ChatPanel)

        if len(self.history_manager) == 0:
            chat_panel.add_message("assistant", "⚠️ No conversations to export")
            return

        # Parse args: formato [nombre]
        parts = args.strip().split(maxsplit=1) if args.strip() else []
        formato = parts[0].lower() if parts else "md"
        filename = parts[1] if len(parts) > 1 else f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if formato not in ["md", "json", "markdown"]:
            chat_panel.add_message("assistant", f"❌ Invalid format: `{formato}`\n\n**Available formats:** md, json\n**Usage:** `/export <format> [filename]`")
            return

        try:
            if formato in ["md", "markdown"]:
                filepath = self.history_manager.export_markdown(filename)
            else:
                filepath = self.history_manager.export_json(filename)

            chat_panel.add_message("assistant", f"✅ Conversation exported in **{formato.upper()}** format\n\nFile: `{filepath}`")
            self.notify(f"Exported to {filepath}", severity="information")
        except Exception as e:
            chat_panel.add_message("assistant", f"❌ Error exporting: {str(e)}")

    async def cmd_search(self, args: str) -> None:
        """Buscar en historial"""
        chat_panel = self.query_one("#chat-panel", ChatPanel)

        if not args.strip():
            chat_panel.add_message("assistant", "❌ Please specify a keyword\n\n**Usage:** `/search <keyword>`")
            return

        keyword = args.strip()

        try:
            results = self.history_manager.search(keyword)

            if not results:
                chat_panel.add_message("assistant", f"ℹ️ No results found for: **'{keyword}'**")
                return

            # Formatear resultados
            search_text = f"### 🔍 Search Results for: '{keyword}'\n\n**Found:** {len(results)} items\n\n"

            for i, item in enumerate(results[:10], 1):
                timestamp = item.get('timestamp', 'Unknown')
                query = item.get('query', '')[:80] + "..." if len(item.get('query', '')) > 80 else item.get('query', '')
                response = item.get('response', '')[:100] + "..." if len(item.get('response', '')) > 100 else item.get('response', '')

                search_text += f"**{i}. {timestamp}**\n"
                search_text += f"   *Query:* {query}\n"
                search_text += f"   *Response:* {response}\n\n"

            if len(results) > 10:
                search_text += f"\n*Showing first 10 of {len(results)} results*"

            chat_panel.add_message("assistant", search_text)

        except Exception as e:
            chat_panel.add_message("assistant", f"❌ Error searching: {str(e)}")

    async def cmd_stats(self, args: str) -> None:
        """Mostrar estadísticas"""
        chat_panel = self.query_one("#chat-panel", ChatPanel)

        try:
            stats = self.history_manager.get_stats()

            stats_text = f"""### 📊 Usage Statistics

**Total Conversations:** {stats.get('total_conversations', 0)}
**Tools Used:** {stats.get('total_tools_used', 0)} (unique: {len(stats.get('unique_tools', []))})
**Date Range:** {stats.get('first_date', 'N/A')} to {stats.get('last_date', 'N/A')}

**Most Used Tools:**
"""
            tools_usage = stats.get('tools_usage', {})
            if tools_usage:
                sorted_tools = sorted(tools_usage.items(), key=lambda x: x[1], reverse=True)[:5]
                for tool, count in sorted_tools:
                    stats_text += f"  - {tool}: {count} times\n"
            else:
                stats_text += "  - No tools used yet\n"

            chat_panel.add_message("assistant", stats_text)

        except Exception as e:
            chat_panel.add_message("assistant", f"❌ Error getting stats: {str(e)}")

    async def cmd_examples(self, args: str) -> None:
        """Mostrar ejemplos de consultas"""
        chat_panel = self.query_one("#chat-panel", ChatPanel)

        examples_text = """### 💡 Example Queries

**Basic Data Fetching:**
- "Show me GDP data from 2020 to 2024"
- "Get unemployment rate from 2015 to 2023"
- "What is the inflation rate for the last 5 years?"

**Search & Metadata:**
- "Search for inflation series"
- "Show me metadata for UNRATE"
- "Find all GDP related series"

**Visualization:**
- "Plot unemployment vs inflation from 2010 to 2023"
- "Create a chart of GDP growth over time"
- "Show me a dual-axis plot of UNRATE and CPIAUCSL"

**Dataset Building:**
- "Build a dataset with UNRATE and CPIAUCSL (YoY) from 2000 to 2024"
- "Create a dataset with GDP (QoQ), inflation (YoY), and unemployment"
- "Build me a comprehensive macro dataset for the last 10 years"

**Analysis:**
- "Analyze the stationarity of the unemployment rate"
- "Perform differencing analysis on GDP"
- "Test if inflation is stationary"

**Releases & Categories:**
- "List all FRED releases"
- "Show me details about the Employment Situation release"
- "What sources are available in FRED?"

💡 Type your query in natural language and I'll use the appropriate tools!
"""
        chat_panel.add_message("assistant", examples_text)

    # ==================== END SLASH COMMANDS ====================

    def _format_tool_result(self, tool_name: str, result_text: str) -> str:
        """Formatear resultado de herramienta para mejor visualización."""
        import json

        try:
            result_json = json.loads(result_text)
            
            # ==================== FIX: NESTED JSON ====================
            # Check if result is nested (has "message" field with JSON string)
            if isinstance(result_json, dict) and "message" in result_json:
                try:
                    # Parse nested JSON from "message" field
                    nested_json = json.loads(result_json["message"])
                    result_json = nested_json
                except (json.JSONDecodeError, TypeError):
                    pass
            # ==================== END FIX ====================

            # ==================== GUI AUTO-OPEN (v0.4.0) ====================
            
            # Check if this is a plot tool
            if tool_name in ["plot_fred_series_tool", "plot_dual_axis_tool", "plot_from_dataset_tool", "analyze_differencing_tool"]:
                plot_path = result_json.get("plot_path")
                
                # ==================== CRITICAL FIX ====================
                # Only try to open GUI if plot_path is valid AND file exists
                if plot_path and plot_path != "None" and os.path.exists(plot_path):
                    
                    # Try to open in GUI window
                    if GUI_AUTO_OPEN and self.gui_backend and self.gui_backend.can_display_gui():
                        try:
                            # ==================== SUPPRESS LOGGING DURING GUI LAUNCH ====================
                            old_level = logging.root.level
                            logging.root.setLevel(logging.CRITICAL + 1)
                            
                            try:
                                series_id = result_json.get("series_id", "Plot")
                                
                                success = self.gui_backend.open_image(
                                    plot_path,
                                    title=f"FRED Plot - {series_id}"
                                )
                            finally:
                                logging.root.setLevel(old_level)
                            # ==================== END SUPPRESSION ====================
                            
                            if success:
                                # Force screen refresh
                                self.refresh()
                                
                                # Show notification
                                self.notify(
                                    f"🎉 Plot window opened: {series_id}",
                                    severity="information",
                                    timeout=3
                                )
                                
                                # Return success message with GUI info
                                return self._format_plot_result_with_gui(result_json)
                                
                        except Exception as e:
                            # Silently fail (logging disabled anyway)
                            pass
                
                # Fallback: Return file paths info (no GUI)
                return self._format_plot_result(result_json)
            
            if tool_name == "fetch_series_metadata_tool" and "data" in result_json:
                data = result_json["data"]
                formatted = f"""### 📊 {data.get('title', 'N/A')}
**ID:** `{data.get('id', 'N/A')}`

| Campo | Valor |
|-------|-------|
| Frecuencia | {data.get('frequency', 'N/A')} |
| Unidades | {data.get('units', 'N/A')} |
| Ajuste estacional | {data.get('seasonal_adjustment', 'N/A')} |
| Popularidad | {data.get('popularity', 'N/A')} |
| Período | {data.get('observation_start', 'N/A')} a {data.get('observation_end', 'N/A')} |
| Última actualización | {data.get('last_updated', 'N/A')} |
"""
                return formatted

            elif tool_name == "fetch_series_observations_tool" and "data" in result_json:
                data = result_json["data"]
                metadata = result_json.get("metadata", {})
                series_id = result_json.get("series_id", "N/A")
                total = metadata.get("total_count", len(data))

                formatted = f"""### 📈 Observaciones: {series_id}
**Total de observaciones:** {total}

**Primeras 5 observaciones:**
| Fecha | Valor |
|-------|-------|
"""
                for obs in data[:5]:
                    date = str(obs.get('date', 'N/A')).split('T')[0]
                    value = obs.get('value', 'N/A')
                    formatted += f"| {date} | {value} |\n"

                if len(data) > 5:
                    formatted += f"\n**Últimas 5 observaciones:**\n| Fecha | Valor |\n|-------|-------|\n"
                    for obs in data[-5:]:
                        date = str(obs.get('date', 'N/A')).split('T')[0]
                        value = obs.get('value', 'N/A')
                        formatted += f"| {date} | {value} |\n"

                # Estadísticas
                values = [float(obs['value']) for obs in data if obs.get('value') not in ['N/A', None, 'nan']]
                if values:
                    formatted += f"\n**Estadísticas:**\n- Mínimo: {min(values):.2f}\n- Máximo: {max(values):.2f}\n- Promedio: {sum(values)/len(values):.2f}\n"

                return formatted

            elif tool_name == "search_fred_series_tool" and "data" in result_json:
                data = result_json["data"]
                metadata = result_json.get("metadata", {})
                search_text = result_json.get("search_text", "N/A")
                total = metadata.get("total_count", len(data))

                formatted = f"""### 🔍 Búsqueda: "{search_text}"
**Resultados:** {total}

| ID | Título | Popularidad | Frecuencia |
|----|--------|-------------|-----------|
"""
                for result in data[:10]:
                    series_id = result.get('id', 'N/A')
                    title = result.get('title', 'N/A')[:50]
                    pop = result.get('popularity', 'N/A')
                    freq = result.get('frequency_short', 'N/A')
                    formatted += f"| {series_id} | {title}... | {pop} | {freq} |\n"

                if total > 10:
                    formatted += f"\n*Mostrando primeros 10 de {total} resultados*\n"

                return formatted

            # Para otros tools, intentar formatear JSON de manera legible
            if isinstance(result_json, dict) and "data" in result_json:
                return f"```json\n{json.dumps(result_json, indent=2)[:1000]}...\n```"

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse tool result as JSON: {e}")
            pass

        return result_text

    def _format_plot_result_with_gui(self, result_json: dict) -> str:
        """Format plot result when GUI window opened"""
        plot_path = result_json.get("plot_path", "N/A")
        csv_path = result_json.get("csv_path", "N/A")
        excel_path = result_json.get("excel_path", "N/A")
        series_id = result_json.get("series_id", "Unknown")
        
        backend_name = self.gui_backend.backend if self.gui_backend else "Unknown"
        
        return f"""### ✅ Plot Generated & Opened!

**Series:** {series_id}
**Window:** {backend_name.title()} GUI window opened automatically 🎉

**Files saved:**
- 📊 Plot: `{os.path.basename(plot_path) if plot_path != 'N/A' else 'N/A'}`
- 📄 CSV: `{os.path.basename(csv_path) if csv_path != 'N/A' else 'N/A'}`
- 📈 Excel: `{os.path.basename(excel_path) if excel_path != 'N/A' else 'N/A'}`

📁 Full path: `{plot_path}`

💡 **Tip:** Close window with ESC or click Close button.
"""

    def _format_plot_result(self, result_json: dict) -> str:
        """Format plot result (no GUI)"""
        plot_path = result_json.get("plot_path", "N/A")
        csv_path = result_json.get("csv_path", "N/A")
        excel_path = result_json.get("excel_path", "N/A")
        series_id = result_json.get("series_id", "Unknown")
        
        gui_status = ""
        if self.gui_backend and not self.gui_backend.can_display_gui():
            gui_status = "\n\n⚠️ **GUI not available.** Open file manually or enable X forwarding."
        elif not GUI_AUTO_OPEN:
            gui_status = "\n\nℹ️ **GUI auto-open disabled.** Enable with `GUI_AUTO_OPEN=true` in .env"
        elif not self.gui_backend:
            gui_status = "\n\n⚠️ **GUI backend not initialized.** Check installation."
        
        return f"""### ✅ Plot Generated

**Series:** {series_id}

**Files:**
- 📊 Plot: `{os.path.basename(plot_path) if plot_path != 'N/A' else 'N/A'}`
- 📄 CSV: `{os.path.basename(csv_path) if csv_path != 'N/A' else 'N/A'}`
- 📈 Excel: `{os.path.basename(excel_path) if excel_path != 'N/A' else 'N/A'}`

📁 Full path: `{plot_path}`{gui_status}
"""

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Manejar clicks en botones"""
        if event.button.id == "refresh-datasets":
            await self.load_datasets()
            self.notify("Datasets refreshed", severity="information")

        elif event.button.id == "build-dataset":
            # Mostrar mensaje en el chat sugiriendo cómo construir dataset
            chat_panel = self.query_one("#chat-panel", ChatPanel)
            chat_panel.add_message(
                "assistant",
                """To build a new dataset, tell me:
1. Which series you want (e.g., UNRATE, CPIAUCSL, GDP)
2. Any transformations (e.g., YoY, QoQ, log)
3. Date range (optional)

**Example:**
"Build a dataset with UNRATE, CPIAUCSL (YoY) and GDP (QoQ) from 2000 to 2024"
"""
            )

        elif event.button.id == "clear-history":
            self.history_manager.clear()
            history_panel = self.query_one("#history-panel", HistoryPanel)
            history_panel.update_history([])
            self.notify("History cleared", severity="information")

    # === Actions ===

    def action_toggle_sidebar(self) -> None:
        """Toggle visibility del sidebar"""
        sidebar = self.query_one("#sidebar")
        sidebar.display = not sidebar.display

    def action_toggle_history(self) -> None:
        """Cambiar a tab de historial"""
        tabbed = self.query_one(TabbedContent)
        tabbed.active = "history-tab" if tabbed.active == "datasets-tab" else "datasets-tab"

    def action_new_conversation(self) -> None:
        """Iniciar nueva conversación"""
        # Limpiar historial de conversación
        self.conversation_history.clear()
        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.message_count = 0

        self.notify("New conversation started", severity="information")

    def action_save_conversation(self) -> None:
        """Guardar conversación actual"""
        if len(self.history_manager) == 0:
            self.notify("No conversation to save", severity="warning")
            return

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}"
            filepath = self.history_manager.export_json(filename)
            self.notify(f"Saved to: {filepath}", severity="information", timeout=5)
        except Exception as e:
            self.notify(f"Error saving: {str(e)}", severity="error")

    async def action_refresh_resources(self) -> None:
        """Refrescar datasets y recursos"""
        await self.load_datasets()
        
        # Update resource count
        if self.session:
            resources_response = await self.session.list_resources()
            self.resources_available = resources_response.resources
            status_bar = self.query_one("#status-bar", StatusBar)
            status_bar.resources_count = len(self.resources_available)
        
        self.notify("Resources refreshed", severity="information")

    def action_focus_input(self) -> None:
        """Focus en el input de chat"""
        self.query_one("#chat-input", Input).focus()

    async def on_shutdown(self) -> None:
        """Limpiar al cerrar la aplicación"""
        try:
            # Close GUI windows first
            if self.gui_backend and self.gui_backend.current_process:
                try:
                    self.gui_backend._close_current_window()
                except Exception as e:
                    logger.debug(f"Error closing GUI window: {e}")
            
            # Close MCP session
            if self.session:
                try:
                    await self.session.__aexit__(None, None, None)
                except Exception as e:
                    logger.debug(f"Error closing session: {e}")
            
            # Close exit stack
            await self.exit_stack.aclose()
            
        except Exception as e:
            logger.debug(f"Error during shutdown: {e}")
            pass  # Ignore cleanup errors


def main():
    """Punto de entrada de la aplicación TUI"""
    app = MacroMCPApp()
    app.run()


if __name__ == "__main__":
    main()
