"""
Command System for MCP Client
Handles slash commands like /help, /tools, /resources, etc.
"""

from typing import Optional, Dict, Callable, Any
from datetime import datetime
import os


class Command:
    """Representa un comando del sistema."""

    def __init__(self, name: str, description: str, handler: Callable, aliases: list = None):
        self.name = name
        self.description = description
        self.handler = handler
        self.aliases = aliases or []


class CommandHandler:
    """Maneja el registro y ejecucion de comandos."""

    def __init__(self, client):
        self.client = client
        self.commands: Dict[str, Command] = {}
        self._register_default_commands()

    def _register_default_commands(self):
        """Registra los comandos por defecto."""

        # Comando: help
        self.register_command(
            name="help",
            description="Muestra esta ayuda con todos los comandos disponibles",
            handler=self.cmd_help,
            aliases=["h", "?"]
        )

        # Comando: tools
        self.register_command(
            name="tools",
            description="Lista todas las herramientas MCP o muestra detalles de una específica (ej: /t fetch_series_metadata)",
            handler=self.cmd_tools,
            aliases=["t"]
        )

        # Comando: resources
        self.register_command(
            name="resources",
            description="Lista todos los recursos MCP o lee un recurso específico (ej: /r fred://datasets/recent)",
            handler=self.cmd_resources,
            aliases=["r"]
        )

        # Comando: clear
        self.register_command(
            name="clear",
            description="Limpia la pantalla de la consola",
            handler=self.cmd_clear,
            aliases=["cls"]
        )

        # Comando: history
        self.register_command(
            name="history",
            description="Muestra el historial de la conversacion actual",
            handler=self.cmd_history,
            aliases=["hist"]
        )

        # Comando: new
        self.register_command(
            name="new",
            description="Inicia una nueva conversacion (limpia el historial)",
            handler=self.cmd_new,
            aliases=["reset"]
        )

        # Comando: status
        self.register_command(
            name="status",
            description="Muestra el estado actual del cliente",
            handler=self.cmd_status,
            aliases=["info"]
        )

        # Comando: save
        self.register_command(
            name="save",
            description="Guarda la conversacion actual en un archivo",
            handler=self.cmd_save,
            aliases=[]
        )

        # Comando: load
        self.register_command(
            name="load",
            description="Carga una conversacion guardada desde un archivo",
            handler=self.cmd_load,
            aliases=[]
        )

        # Comando: export
        self.register_command(
            name="export",
            description="Exporta la conversacion (formato: md o json)",
            handler=self.cmd_export,
            aliases=[]
        )

        # Comando: search
        self.register_command(
            name="search",
            description="Busca en el historial por palabra clave",
            handler=self.cmd_search,
            aliases=["find"]
        )

        # Comando: stats
        self.register_command(
            name="stats",
            description="Muestra estadisticas de uso y conversaciones",
            handler=self.cmd_stats,
            aliases=["statistics"]
        )

        # Comando: examples
        self.register_command(
            name="examples",
            description="Muestra ejemplos de consultas basados en tus herramientas",
            handler=self.cmd_examples,
            aliases=["ejemplos", "ex"]
        )

        # Comando: exit
        self.register_command(
            name="exit",
            description="Sale del cliente MCP",
            handler=self.cmd_exit,
            aliases=["quit", "q"]
        )

    def register_command(self, name: str, description: str, handler: Callable, aliases: list = None):
        """Registra un nuevo comando."""
        cmd = Command(name, description, handler, aliases)
        self.commands[name] = cmd

        # Registrar aliases
        if aliases:
            for alias in aliases:
                self.commands[alias] = cmd

    def is_command(self, text: str) -> bool:
        """Verifica si el texto es un comando."""
        return text.startswith("/")

    async def execute(self, text: str) -> Optional[str]:
        """Ejecuta un comando y retorna resultado o None."""
        if not self.is_command(text):
            return None

        # Parsear comando y argumentos
        parts = text[1:].split(maxsplit=1)
        cmd_name = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        # Buscar comando
        if cmd_name not in self.commands:
            self.client.ui.show_warning(f"Comando desconocido: /{cmd_name}")
            self.client.ui.show_info("Usa /help para ver comandos disponibles")
            return "COMMAND_NOT_FOUND"

        # Ejecutar comando
        command = self.commands[cmd_name]
        try:
            result = await command.handler(args)
            return result
        except Exception as e:
            self.client.ui.show_error(e, f"Al ejecutar comando /{cmd_name}")
            return "COMMAND_ERROR"

    # ==================== COMMAND HANDLERS ====================

    async def cmd_help(self, args: str) -> str:
        """Muestra ayuda de comandos."""
        self.client.ui.show_commands_help(self.get_primary_commands())
        return "COMMAND_EXECUTED"

    async def cmd_tools(self, args: str) -> str:
        """Lista herramientas disponibles o muestra detalles de una herramienta específica."""
        try:
            response = await self.client.session.list_tools()
            tools = response.tools

            if not tools:
                self.client.ui.show_warning("No hay herramientas disponibles")
                return "COMMAND_EXECUTED"

            # Si se especifica un nombre de tool, mostrar detalles
            if args.strip():
                tool_name = args.strip()
                tool = next((t for t in tools if t.name == tool_name), None)

                if not tool:
                    self.client.ui.show_warning(f"Tool no encontrada: {tool_name}")
                    self.client.ui.show_info(f"Usa /tools para ver todas las herramientas disponibles")
                    return "COMMAND_EXECUTED"

                # Mostrar detalles de la tool específica
                self.client.ui.show_tool_details(tool)
            else:
                # Listar todas las tools
                self.client.ui.show_tools_list(tools)

            return "COMMAND_EXECUTED"
        except Exception as e:
            self.client.ui.show_error(e, "Al listar herramientas")
            return "COMMAND_ERROR"

    async def cmd_resources(self, args: str) -> str:
        """Lista recursos disponibles o lee un recurso específico."""
        try:
            response = await self.client.session.list_resources()
            resources = response.resources

            if not resources:
                self.client.ui.show_warning("No hay recursos disponibles")
                return "COMMAND_EXECUTED"

            # Si se especifica un URI, leer ese recurso
            if args.strip():
                resource_uri = args.strip()

                # Verificar que el URI existe
                resource = next((r for r in resources if str(r.uri) == resource_uri), None)

                if not resource:
                    self.client.ui.show_warning(f"Recurso no encontrado: {resource_uri}")
                    self.client.ui.show_info(f"Usa /resources para ver todos los recursos disponibles")
                    return "COMMAND_EXECUTED"

                # Leer el recurso
                self.client.ui.show_info(f"Leyendo recurso: {resource_uri}")
                try:
                    result = await self.client.session.read_resource(resource_uri)

                    # Mostrar contenido del recurso
                    if result.contents:
                        content = result.contents[0]
                        if hasattr(content, 'text'):
                            self.client.ui.show_resource_content(resource_uri, content.text)
                        else:
                            self.client.ui.show_resource_content(resource_uri, str(content))
                    else:
                        self.client.ui.show_warning("El recurso está vacío")

                except Exception as e:
                    self.client.ui.show_error(e, f"Al leer recurso '{resource_uri}'")
                    return "COMMAND_ERROR"
            else:
                # Listar todos los recursos
                self.client.ui.show_resources_list(resources)

            return "COMMAND_EXECUTED"
        except Exception as e:
            self.client.ui.show_error(e, "Al listar recursos")
            return "COMMAND_ERROR"

    async def cmd_clear(self, args: str) -> str:
        """Limpia la pantalla."""
        self.client.ui.clear_screen()
        return "COMMAND_EXECUTED"

    async def cmd_history(self, args: str) -> str:
        """Muestra historial de conversacion."""
        if not self.client.conversation_history:
            self.client.ui.show_info("El historial esta vacio")
            return "COMMAND_EXECUTED"

        self.client.ui.show_conversation_history(self.client.conversation_history)
        return "COMMAND_EXECUTED"

    async def cmd_new(self, args: str) -> str:
        """Inicia nueva conversacion."""
        if not self.client.conversation_history:
            self.client.ui.show_info("El historial ya esta vacio")
            return "COMMAND_EXECUTED"

        # Guardar cantidad de mensajes antes de limpiar
        msg_count = len(self.client.conversation_history)

        # Limpiar historial
        self.client.conversation_history.clear()

        self.client.ui.show_success(f"Historial limpiado ({msg_count} mensajes eliminados)")
        self.client.ui.show_info("Nueva conversacion iniciada")
        return "COMMAND_EXECUTED"

    async def cmd_status(self, args: str) -> str:
        """Muestra estado del cliente."""
        try:
            # Obtener informacion del servidor
            tools_response = await self.client.session.list_tools()
            tools_count = len(tools_response.tools)

            resources_count = 0
            try:
                resources_response = await self.client.session.list_resources()
                resources_count = len(resources_response.resources)
            except:
                pass

            # Contar mensajes en historial
            history_count = len(self.client.conversation_history)

            # Mostrar status
            self.client.ui.show_client_status(
                tools_count=tools_count,
                resources_count=resources_count,
                history_count=history_count
            )

            return "COMMAND_EXECUTED"
        except Exception as e:
            self.client.ui.show_error(e, "Al obtener estado del cliente")
            return "COMMAND_ERROR"

    async def cmd_save(self, args: str) -> str:
        """Guarda la conversacion actual."""
        if not hasattr(self.client, 'history_manager'):
            self.client.ui.show_error(Exception("History manager not initialized"), "")
            return "COMMAND_ERROR"

        if len(self.client.history_manager) == 0:
            self.client.ui.show_warning("No hay conversaciones para guardar")
            return "COMMAND_EXECUTED"

        # Usar filename del argumento o generar uno por defecto
        filename = args.strip() if args.strip() else f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        try:
            filepath = self.client.history_manager.export_json(filename)
            self.client.ui.show_success(f"Conversacion guardada en: {filepath}")
            return "COMMAND_EXECUTED"
        except Exception as e:
            self.client.ui.show_error(e, "Al guardar conversacion")
            return "COMMAND_ERROR"

    async def cmd_load(self, args: str) -> str:
        """Carga una conversacion guardada."""
        if not hasattr(self.client, 'history_manager'):
            self.client.ui.show_error(Exception("History manager not initialized"), "")
            return "COMMAND_ERROR"

        if not args.strip():
            self.client.ui.show_warning("Debes especificar el nombre del archivo")
            self.client.ui.show_info("Uso: /load <nombre_archivo>")
            return "COMMAND_EXECUTED"

        filename = args.strip()
        # Add .json extension if not present
        if not filename.endswith('.json'):
            filename = f"{filename}.json"

        filepath = os.path.join("conversations", filename)

        try:
            count = self.client.history_manager.load_json(filepath)
            self.client.ui.show_success(f"Conversacion cargada: {count} items")
            self.client.ui.show_info(f"Archivo: {filepath}")
            return "COMMAND_EXECUTED"
        except FileNotFoundError:
            self.client.ui.show_error(FileNotFoundError(f"Archivo no encontrado: {filepath}"), "")
            return "COMMAND_ERROR"
        except Exception as e:
            self.client.ui.show_error(e, "Al cargar conversacion")
            return "COMMAND_ERROR"

    async def cmd_export(self, args: str) -> str:
        """Exporta la conversacion en formato especificado."""
        if not hasattr(self.client, 'history_manager'):
            self.client.ui.show_error(Exception("History manager not initialized"), "")
            return "COMMAND_ERROR"

        if len(self.client.history_manager) == 0:
            self.client.ui.show_warning("No hay conversaciones para exportar")
            return "COMMAND_EXECUTED"

        # Parse args: formato [nombre]
        parts = args.strip().split(maxsplit=1)
        formato = parts[0].lower() if parts else "md"
        filename = parts[1] if len(parts) > 1 else f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if formato not in ["md", "json", "markdown"]:
            self.client.ui.show_warning(f"Formato no valido: {formato}")
            self.client.ui.show_info("Formatos disponibles: md, json")
            return "COMMAND_EXECUTED"

        try:
            if formato in ["md", "markdown"]:
                filepath = self.client.history_manager.export_markdown(filename)
            else:
                filepath = self.client.history_manager.export_json(filename)

            self.client.ui.show_success(f"Conversacion exportada en formato {formato.upper()}")
            self.client.ui.show_info(f"Archivo: {filepath}")
            return "COMMAND_EXECUTED"
        except Exception as e:
            self.client.ui.show_error(e, "Al exportar conversacion")
            return "COMMAND_ERROR"

    async def cmd_search(self, args: str) -> str:
        """Busca en el historial por palabra clave."""
        if not hasattr(self.client, 'history_manager'):
            self.client.ui.show_error(Exception("History manager not initialized"), "")
            return "COMMAND_ERROR"

        if not args.strip():
            self.client.ui.show_warning("Debes especificar una palabra clave")
            self.client.ui.show_info("Uso: /search <keyword>")
            return "COMMAND_EXECUTED"

        keyword = args.strip()

        try:
            results = self.client.history_manager.search(keyword)

            if not results:
                self.client.ui.show_info(f"No se encontraron resultados para: '{keyword}'")
                return "COMMAND_EXECUTED"

            # Mostrar resultados
            self.client.ui.print()
            self.client.ui.print(f"[bold cyan]Resultados de busqueda para: '{keyword}'[/bold cyan]")
            self.client.ui.print(f"[dim]Encontrados: {len(results)} items[/dim]")
            self.client.ui.print()

            for i, item in enumerate(results, 1):
                timestamp = item.get('timestamp', 'Unknown')
                query = item.get('query', '')
                response = item.get('response', '')

                # Truncate long text
                query_preview = query[:100] + "..." if len(query) > 100 else query
                response_preview = response[:100] + "..." if len(response) > 100 else response

                self.client.ui.print(f"[cyan]{i}. {timestamp}[/cyan]")
                self.client.ui.print(f"   [dim]Query:[/dim] {query_preview}")
                self.client.ui.print(f"   [dim]Response:[/dim] {response_preview}")
                self.client.ui.print()

            return "COMMAND_EXECUTED"
        except Exception as e:
            self.client.ui.show_error(e, "Al buscar en historial")
            return "COMMAND_ERROR"

    async def cmd_stats(self, args: str) -> str:
        """Muestra estadisticas de uso y conversaciones."""
        if not hasattr(self.client, 'history_manager'):
            self.client.ui.show_error(Exception("History manager not initialized"), "")
            return "COMMAND_ERROR"

        try:
            stats = self.client.history_manager.get_stats()
            self.client.ui.show_stats(stats)
            return "COMMAND_EXECUTED"
        except Exception as e:
            self.client.ui.show_error(e, "Al obtener estadisticas")
            return "COMMAND_ERROR"

    async def cmd_examples(self, args: str) -> str:
        """Muestra ejemplos de consultas interactivas."""
        try:
            # Obtener herramientas disponibles
            response = await self.client.session.list_tools()
            tools = response.tools

            if not tools:
                self.client.ui.show_warning("No hay herramientas disponibles para generar ejemplos")
                return "COMMAND_EXECUTED"

            # Mostrar ejemplos basados en herramientas
            self.client.ui.show_examples(tools)

            return "COMMAND_EXECUTED"
        except Exception as e:
            self.client.ui.show_error(e, "Al generar ejemplos")
            return "COMMAND_ERROR"

    async def cmd_exit(self, args: str) -> str:
        """Sale del cliente."""
        return "EXIT_REQUESTED"

    def get_primary_commands(self) -> list:
        """Obtiene lista de comandos primarios (sin aliases)."""
        seen = set()
        primary = []

        for name, cmd in self.commands.items():
            if cmd.name not in seen:
                seen.add(cmd.name)
                primary.append(cmd)

        return sorted(primary, key=lambda c: c.name)
