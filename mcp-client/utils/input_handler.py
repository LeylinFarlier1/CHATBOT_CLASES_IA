"""
Enhanced Input Handler with Autocompletion
Uses prompt_toolkit for advanced input features.
"""

from typing import List, Optional
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter, Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
import os


class MCPCompleter(Completer):
    """Custom completer for MCP client with commands and keywords."""

    def __init__(self, commands: List[str] = None, keywords: List[str] = None):
        """
        Initialize completer.

        Args:
            commands: List of commands (with / prefix)
            keywords: List of common keywords (without / prefix)
        """
        self.commands = commands or []
        self.keywords = keywords or []

    def get_completions(self, document, complete_event):
        """Generate completions based on current input."""
        text = document.text_before_cursor
        word = document.get_word_before_cursor()

        # Complete commands if line starts with /
        if text.startswith('/'):
            for cmd in self.commands:
                if cmd.startswith(word):
                    yield Completion(cmd, start_position=-len(word))

        # Complete keywords otherwise
        else:
            for keyword in self.keywords:
                if keyword.lower().startswith(word.lower()):
                    yield Completion(keyword, start_position=-len(word))

    def update_commands(self, commands: List[str]):
        """Update command list."""
        self.commands = commands

    def update_keywords(self, keywords: List[str]):
        """Update keyword list."""
        self.keywords = keywords


class InputHandler:
    """Enhanced input handler with autocompletion and history."""

    def __init__(self, history_file: str = ".mcp_history"):
        """
        Initialize input handler.

        Args:
            history_file: Path to history file
        """
        # Default commands
        self.commands = [
            '/help', '/h', '/?',
            '/tools', '/t',
            '/resources', '/r',
            '/clear', '/cls',
            '/history', '/hist',
            '/new', '/reset',
            '/status', '/info',
            '/save',
            '/load',
            '/export',
            '/search',
            '/stats', '/statistics',
            '/examples', '/ejemplos', '/ex',
            '/exit', '/quit', '/q'
        ]

        # Default keywords (common economic indicators)
        self.keywords = [
            'GDP', 'inflation', 'unemployment', 'CPI', 'interest rate',
            'dataset', 'plot', 'compare', 'analyze', 'download',
            'UNRATE', 'CPIAUCSL', 'FEDFUNDS', 'DGS10', 'PAYEMS',
            'monthly', 'quarterly', 'annual', 'yearly',
            'show', 'get', 'fetch', 'display'
        ]

        # Create completer
        self.completer = MCPCompleter(self.commands, self.keywords)

        # Create style
        self.style = Style.from_dict({
            'prompt': 'bold cyan',
            'completion-menu.completion': 'bg:#008888 #ffffff',
            'completion-menu.completion.current': 'bg:#00aaaa #000000',
            'completion-menu.meta': 'bg:#999999 #ffffff',
        })

        # Create session with history
        history_path = os.path.join(os.path.dirname(__file__), '..', history_file)
        self.session = PromptSession(
            history=FileHistory(history_path),
            completer=self.completer,
            complete_while_typing=True,
            style=self.style
        )

    async def get_input(self, prompt: str = "Consulta: ") -> str:
        """
        Get input from user with autocompletion.

        Args:
            prompt: Prompt text to display

        Returns:
            User input string
        """
        try:
            result = await self.session.prompt_async(
                f"{prompt}",
                multiline=False
            )
            return result.strip()
        except (KeyboardInterrupt, EOFError):
            return ""

    def add_keyword(self, keyword: str):
        """Add a keyword to autocompletion."""
        if keyword and keyword not in self.keywords:
            self.keywords.append(keyword)
            self.completer.update_keywords(self.keywords)

    def add_keywords(self, keywords: List[str]):
        """Add multiple keywords to autocompletion."""
        for keyword in keywords:
            self.add_keyword(keyword)

    def remove_keyword(self, keyword: str):
        """Remove a keyword from autocompletion."""
        if keyword in self.keywords:
            self.keywords.remove(keyword)
            self.completer.update_keywords(self.keywords)

    def add_command(self, command: str):
        """Add a command to autocompletion."""
        if command and command not in self.commands:
            if not command.startswith('/'):
                command = f'/{command}'
            self.commands.append(command)
            self.completer.update_commands(self.commands)

    def get_keywords(self) -> List[str]:
        """Get current keyword list."""
        return self.keywords.copy()

    def get_commands(self) -> List[str]:
        """Get current command list."""
        return self.commands.copy()
