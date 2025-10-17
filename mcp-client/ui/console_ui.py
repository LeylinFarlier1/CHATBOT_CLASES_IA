"""
Console UI Module with Rich - Enhanced terminal interface for MCP Client
Implements Phase 1: Colors, Panels, Progress Indicators, and Markdown rendering
Windows compatible version (no emojis)
"""

from typing import List, Optional
from datetime import datetime
import re
import os
import subprocess

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.text import Text
from rich.syntax import Syntax


class ConsoleUI:
    """Enhanced console UI using Rich library."""

    def __init__(self):
        # Configurar console con mejor soporte para Windows
        self.console = Console(
            force_terminal=True,
            legacy_windows=False,
            safe_box=True
        )
        self._progress_context = None

    # ==================== BANNERS Y PANELES ====================

    def show_banner(self):
        """Mostrar banner de inicio."""
        banner_text = Text()
        banner_text.append(">>> ", style="bold cyan")
        banner_text.append("Cliente Macro MCP\n", style="bold cyan")
        banner_text.append("Powered by Claude AI + FRED API", style="dim")

        self.console.print(Panel(
            banner_text,
            border_style="cyan",
            padding=(1, 2)
        ))

    def show_connection_success(self, tools_count: int, resources_count: int):
        """Mostrar mensaje de conexion exitosa."""
        info = Text()
        info.append("[OK] ", style="bold green")
        info.append(f"Herramientas disponibles: ", style="white")
        info.append(f"{tools_count}\n", style="bold cyan")
        info.append("[OK] ", style="bold green")
        info.append(f"Recursos disponibles: ", style="white")
        info.append(f"{resources_count}", style="bold cyan")

        self.console.print(Panel(
            info,
            title="[bold green]Conexion Establecida[/bold green]",
            border_style="green",
            padding=(0, 2)
        ))

    def show_welcome_message(self):
        """Mostrar mensaje de bienvenida con tip aleatorio."""
        import random

        # Lista de tips útiles
        tips = [
            "Usa /examples para ver ejemplos de consultas que puedes hacer",
            "Prueba /stats para ver tus patrones de uso y herramientas favoritas",
            "Escribe /help para descubrir todos los comandos disponibles",
            "Puedes exportar conversaciones con /export md [nombre]",
            "Usa /search [keyword] para buscar en tu historial de conversaciones",
            "El autocompletado está activado - presiona Tab para sugerencias",
            "Guarda tu sesión con /save antes de salir",
            "Usa /tools para ver todas las herramientas MCP disponibles",
            "Los comandos tienen aliases: /h = /help, /t = /tools, /r = /resources",
            "Navega tu historial de comandos con las flechas ↑ y ↓"
        ]

        # Seleccionar un tip aleatorio
        random_tip = random.choice(tips)

        self.console.print()

        # Panel principal de bienvenida con tip
        welcome_text = Text()
        welcome_text.append("Bienvenido al Cliente Macro MCP!\n\n", style="bold cyan")
        welcome_text.append("Escribe tus consultas sobre datos macroeconómicos\n", style="white")
        welcome_text.append("Comandos: 'salir', 'exit', 'quit' para terminar\n\n", style="dim")
        welcome_text.append("💡 Tip: ", style="yellow")
        welcome_text.append(random_tip, style="dim yellow")

        self.console.print(Panel(
            welcome_text,
            border_style="cyan",
            padding=(1, 2)
        ))

        self.console.print()

    # ==================== HERRAMIENTAS Y RECURSOS ====================

    def show_tools_list(self, tools: List):
        """Mostrar lista de herramientas en formato de tabla."""
        table = Table(
            title="Herramientas MCP Disponibles",
            border_style="blue",
            show_lines=True
        )

        table.add_column("#", style="dim", width=3, no_wrap=True)
        table.add_column("Nombre", style="cyan", no_wrap=True)
        table.add_column("Descripcion", style="white")

        for i, tool in enumerate(tools, 1):
            description = tool.description
            if len(description) > 80:
                description = description[:77] + "..."

            table.add_row(
                str(i),
                tool.name,
                description
            )

        self.console.print(table)
        self.console.print()

    def show_tool_details(self, tool):
        """Mostrar detalles completos de una herramienta específica."""
        import json

        # Construir panel con información detallada
        details = Text()
        details.append(f"{tool.name}\n\n", style="bold cyan")

        # Descripción
        details.append("Descripcion:\n", style="bold white")
        details.append(f"{tool.description}\n\n", style="white")

        # Parámetros (inputSchema)
        if hasattr(tool, 'inputSchema') and tool.inputSchema:
            schema = tool.inputSchema
            details.append("Parametros:\n", style="bold white")

            if 'properties' in schema:
                props = schema['properties']
                required = schema.get('required', [])

                for param_name, param_info in props.items():
                    # Indicar si es requerido
                    req_label = "[red]*[/red]" if param_name in required else " "
                    details.append(f"  {req_label} ", style="")
                    details.append(f"{param_name}", style="cyan")
                    details.append(f" ({param_info.get('type', 'any')})", style="dim")

                    # Descripción del parámetro
                    if 'description' in param_info:
                        details.append(f"\n    {param_info['description']}", style="dim")

                    details.append("\n")

                details.append("\n[red]*[/red] = requerido\n", style="dim")

        # Schema JSON (colapsado)
        details.append("\nSchema JSON:\n", style="bold white")
        if hasattr(tool, 'inputSchema'):
            schema_json = json.dumps(tool.inputSchema, indent=2)
            details.append(f"{schema_json[:200]}...", style="dim")

        self.console.print()
        self.console.print(Panel(
            details,
            title=f"[bold cyan]Tool: {tool.name}[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        ))
        self.console.print()

    def show_resources_list(self, resources: List):
        """Mostrar lista de recursos disponibles."""
        table = Table(
            title="Recursos Disponibles",
            border_style="magenta",
            show_lines=True,
            caption="[dim]Usa /r <URI> para leer un recurso (ejemplo: /r fred://datasets/recent)[/dim]"
        )

        table.add_column("#", style="dim", width=3)
        table.add_column("URI", style="magenta", no_wrap=False)
        table.add_column("Descripción", style="white")

        for i, resource in enumerate(resources, 1):
            uri = str(resource.uri)
            name = getattr(resource, 'name', 'N/A')
            description = getattr(resource, 'description', name)

            # Si no hay descripción, usar el nombre
            if not description or description == 'N/A':
                description = name

            table.add_row(
                str(i),
                uri,
                description
            )

        self.console.print()
        self.console.print(table)
        self.console.print()

    def show_resource_content(self, uri: str, content: str):
        """Mostrar contenido de un recurso MCP."""
        # Limitar contenido muy largo
        max_lines = 100
        lines = content.split('\n')

        if len(lines) > max_lines:
            display_content = '\n'.join(lines[:max_lines])
            display_content += f"\n\n[dim]... (mostrando primeras {max_lines} líneas de {len(lines)} totales)[/dim]"
        else:
            display_content = content

        self.console.print()
        self.console.print(Panel(
            display_content,
            title=f"[magenta]Resource: {uri}[/magenta]",
            border_style="magenta",
            padding=(1, 2)
        ))
        self.console.print()

    # ==================== CONSULTAS Y RESPUESTAS ====================

    def show_user_query(self, query: str):
        """Mostrar consulta del usuario."""
        self.console.print(Panel(
            query,
            title="[cyan]Tu Consulta[/cyan]",
            border_style="cyan",
            padding=(0, 2)
        ))

    def show_response(self, response: str, render_markdown: bool = True):
        """Mostrar respuesta de Claude."""
        if render_markdown:
            try:
                markdown = Markdown(response)
                content = markdown
            except Exception:
                # Si falla el parsing de markdown, mostrar como texto
                content = response
        else:
            content = response

        self.console.print(Panel(
            content,
            title="[magenta]Respuesta de Claude[/magenta]",
            border_style="magenta",
            padding=(1, 2)
        ))
        self.console.print()

    def show_tool_call(self, tool_name: str, args: dict):
        """Mostrar cuando se llama a una herramienta."""
        args_str = ", ".join([f"{k}={v}" for k, v in args.items()])
        if len(args_str) > 60:
            args_str = args_str[:57] + "..."

        self.console.print(
            f"[dim][TOOL] Usando herramienta:[/dim] [yellow]{tool_name}[/yellow] [dim]({args_str})[/dim]"
        )

    def show_resource_read(self, uri: str):
        """Mostrar cuando se lee un recurso."""
        self.console.print(
            f"[dim][RESOURCE] Leyendo recurso:[/dim] [magenta]{uri}[/magenta]"
        )

    # ==================== INDICADORES DE PROGRESO ====================

    def create_progress_spinner(self, message: str = "Procesando..."):
        """Crear un spinner de progreso."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        )

    async def show_processing(self, message: str = "Procesando consulta con Claude..."):
        """Mostrar indicador de procesamiento."""
        with self.create_progress_spinner() as progress:
            task = progress.add_task(f"[cyan]{message}[/cyan]", total=None)
            # El spinner se mostrara automaticamente mientras se ejecuta el codigo
            return progress, task

    def create_live_progress(self):
        """Crear un contexto de progreso en vivo para actualizaciones en tiempo real."""
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=False  # Mantener historial de estados
        )
        return progress

    def update_progress_status(self, progress, task_id, message: str, style: str = "cyan"):
        """Actualizar el mensaje de estado del progreso."""
        progress.update(task_id, description=f"[{style}]{message}[/{style}]")

    # ==================== ERRORES Y ADVERTENCIAS ====================

    def _detect_error_type(self, error: Exception) -> str:
        """Detectar tipo de error basado en mensaje y tipo."""
        error_str = str(error).lower()

        # Rate limit
        if "429" in error_str or "rate_limit" in error_str or "rate limit" in error_str:
            return "rate_limit"

        # API Key
        if "401" in error_str or "unauthorized" in error_str or "api_key" in error_str or "api key" in error_str:
            return "api_key"

        # Conexión
        if "connection" in error_str or "timeout" in error_str or "network" in error_str:
            return "connection"

        # Parámetros inválidos
        if "400" in error_str or "bad request" in error_str or "invalid" in error_str:
            return "invalid_params"

        # Servidor caído
        if "500" in error_str or "503" in error_str or "server error" in error_str:
            return "server_error"

        return "unknown"

    def show_error(self, error: Exception, context: str = ""):
        """Mostrar error con formato inteligente basado en tipo."""
        error_type = self._detect_error_type(error)
        error_str = str(error)

        # Construir mensaje según tipo de error
        if error_type == "rate_limit":
            # Extraer tokens si es posible
            import re
            tokens_match = re.search(r'(\d+,?\d*)\s+input tokens per minute', error_str)
            limit = tokens_match.group(1) if tokens_match else "20,000"

            title = "[!] Rate Limit Excedido"
            message = (
                f"[red bold]Has excedido el límite de tokens de entrada[/red bold]\n"
                f"[dim]Límite: {limit} tokens por minuto[/dim]\n\n"
                f"[yellow]Causas comunes:[/yellow]\n"
                f"  • Demasiadas consultas en poco tiempo\n"
                f"  • Historial de conversación muy largo\n"
                f"  • Herramientas que devuelven muchos datos\n\n"
                f"[green]Soluciones:[/green]\n"
                f"  1. Espera 60 segundos antes de reintentar\n"
                f"  2. Usa /new para limpiar el historial\n"
                f"  3. Limita el rango de fechas en tus consultas\n"
                f"  4. Divide consultas grandes en partes más pequeñas\n\n"
                f"[cyan]Tip:[/cyan] El comando /stats te muestra tu uso"
            )
            border_style = "yellow"

        elif error_type == "api_key":
            title = "[!] Error de Autenticación"
            message = (
                f"[red bold]API Key inválida o faltante[/red bold]\n\n"
                f"[yellow]Causas posibles:[/yellow]\n"
                f"  • Variable ANTHROPIC_API_KEY no definida\n"
                f"  • API key expirada o incorrecta\n"
                f"  • Problemas con el archivo .env\n\n"
                f"[green]Soluciones:[/green]\n"
                f"  1. Verifica tu archivo .env en la raíz del proyecto\n"
                f"  2. Asegúrate de que contiene: ANTHROPIC_API_KEY=sk-...\n"
                f"  3. Genera nueva key en: console.anthropic.com\n"
                f"  4. Reinicia el cliente después de editar .env\n\n"
                f"[cyan]Comando útil:[/cyan] /status (verificar conexión)"
            )
            border_style = "red"

        elif error_type == "connection":
            title = "[!] Error de Conexión"
            message = (
                f"[red bold]No se pudo conectar al servidor[/red bold]\n\n"
                f"[yellow]Verificaciones:[/yellow]\n"
                f"  • ¿Está el servidor MCP corriendo?\n"
                f"  • ¿Tienes conexión a internet?\n"
                f"  • ¿Hay problemas de firewall?\n\n"
                f"[green]Soluciones:[/green]\n"
                f"  1. Verifica que el servidor MCP esté activo\n"
                f"  2. Revisa tu conexión de red\n"
                f"  3. Intenta: /status para verificar estado\n"
                f"  4. Reinicia el cliente MCP si es necesario\n\n"
                f"[dim]Error técnico: {error_str[:100]}...[/dim]"
            )
            border_style = "red"

        elif error_type == "invalid_params":
            title = "[!] Parámetros Inválidos"
            message = (
                f"[red bold]Los parámetros enviados no son válidos[/red bold]\n\n"
                f"[yellow]Causas comunes:[/yellow]\n"
                f"  • ID de serie incorrecta\n"
                f"  • Formato de fecha inválido (usar YYYY-MM-DD)\n"
                f"  • Parámetros faltantes\n\n"
                f"[green]Soluciones:[/green]\n"
                f"  1. Usa /examples para ver consultas válidas\n"
                f"  2. Verifica IDs con: search_fred_series_tool\n"
                f"  3. Formato de fechas: YYYY-MM-DD (ej: 2020-01-01)\n"
                f"  4. Usa /tools para ver parámetros requeridos\n\n"
                f"[dim]Error: {error_str[:150]}...[/dim]"
            )
            border_style = "yellow"

        elif error_type == "server_error":
            title = "[!] Error del Servidor"
            message = (
                f"[red bold]El servidor encontró un error interno[/red bold]\n\n"
                f"[yellow]Qué hacer:[/yellow]\n"
                f"  • Este error es del lado del servidor, no tuyo\n"
                f"  • Usualmente es temporal\n\n"
                f"[green]Soluciones:[/green]\n"
                f"  1. Espera 30-60 segundos y reintenta\n"
                f"  2. Si persiste, revisa status de Anthropic/FRED\n"
                f"  3. Intenta una consulta más simple\n\n"
                f"[dim]Error: {error_str[:150]}...[/dim]"
            )
            border_style = "red"

        else:
            # Error genérico - mostrar mensaje original
            title = "[!] Error"
            message = (
                f"[red bold]Error:[/red bold] {error_str}\n"
                + (f"[dim]Contexto: {context}[/dim]\n\n" if context else "\n")
                + "[yellow]Sugerencias generales:[/yellow]\n"
                + "  • Verifica tu conexión\n"
                + "  • Revisa los parámetros de tu consulta\n"
                + "  • Intenta reformular tu pregunta\n"
                + "  • Usa /help para ver comandos disponibles"
            )
            border_style = "red"

        error_panel = Panel(
            message,
            title=title,
            border_style=border_style,
            padding=(1, 2)
        )
        self.console.print(error_panel)
        self.console.print()

    def show_warning(self, message: str):
        """Mostrar advertencia."""
        self.console.print(f"[yellow][!] {message}[/yellow]")

    def show_info(self, message: str):
        """Mostrar informacion."""
        self.console.print(f"[cyan][i] {message}[/cyan]")

    def show_success(self, message: str):
        """Mostrar mensaje de exito."""
        self.console.print(f"[green][OK] {message}[/green]")

    # ==================== UTILIDADES ====================

    def show_separator(self):
        """Mostrar separador visual."""
        self.console.print("[dim]" + "-" * 60 + "[/dim]")

    def clear_screen(self):
        """Limpiar la pantalla."""
        self.console.clear()

    def print(self, *args, **kwargs):
        """Proxy para console.print."""
        self.console.print(*args, **kwargs)

    def show_goodbye(self):
        """Mostrar mensaje de despedida."""
        self.console.print()
        goodbye = Panel(
            "[cyan]Gracias por usar el Cliente Macro MCP!\n"
            "[dim]Hasta pronto[/dim]",
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(goodbye)

    # ==================== DEBUG Y VERBOSE ====================

    def show_debug(self, message: str, data: any = None):
        """Mostrar mensaje de debug."""
        self.console.print(f"[dim cyan]DEBUG:[/dim cyan] {message}")
        if data:
            from rich.pretty import pprint
            pprint(data, console=self.console)

    def show_json(self, data: dict, title: str = "JSON Data"):
        """Mostrar datos JSON con syntax highlighting."""
        import json
        json_str = json.dumps(data, indent=2)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)

        self.console.print(Panel(
            syntax,
            title=title,
            border_style="blue"
        ))

    # ==================== COMANDOS (FASE 2) ====================

    def show_commands_help(self, commands: list):
        """Mostrar tabla de ayuda de comandos."""
        table = Table(
            title="Comandos Disponibles",
            border_style="cyan",
            show_lines=False
        )

        table.add_column("Comando", style="cyan", no_wrap=True)
        table.add_column("Aliases", style="dim", no_wrap=True)
        table.add_column("Descripcion", style="white")

        for cmd in commands:
            # Formatear comando con /
            cmd_name = f"/{cmd.name}"

            # Formatear aliases
            aliases = ", ".join([f"/{a}" for a in cmd.aliases]) if cmd.aliases else "-"

            table.add_row(
                cmd_name,
                aliases,
                cmd.description
            )

        self.console.print()
        self.console.print(table)
        self.console.print()

    def show_conversation_history(self, history: list):
        """Mostrar historial de conversacion."""
        self.console.print()
        self.console.print("[bold cyan]Historial de Conversacion[/bold cyan]")
        self.console.print(f"[dim]Total de mensajes: {len(history)}[/dim]")
        self.console.print()

        for i, msg in enumerate(history, 1):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # Determinar estilo segun rol
            if role == "user":
                role_style = "cyan"
                role_label = "Usuario"
            elif role == "assistant":
                role_style = "magenta"
                role_label = "Claude"
            else:
                role_style = "dim"
                role_label = role

            # Formatear contenido
            if isinstance(content, str):
                content_preview = content[:100] + "..." if len(content) > 100 else content
            elif isinstance(content, list):
                # Contenido estructurado (tool_use, tool_result, etc.)
                content_types = [item.get("type", "unknown") for item in content if isinstance(item, dict)]
                content_preview = f"[{', '.join(content_types)}]"
            else:
                content_preview = str(content)[:100]

            self.console.print(f"[{role_style}]{i}. {role_label}:[/{role_style}] [dim]{content_preview}[/dim]")

        self.console.print()

    def show_client_status(self, tools_count: int, resources_count: int, history_count: int):
        """Mostrar estado del cliente."""
        status_text = Text()
        status_text.append("Estado del Cliente MCP\n\n", style="bold cyan")
        status_text.append("Conexion: ", style="white")
        status_text.append("Activa\n", style="bold green")
        status_text.append(f"Herramientas: ", style="white")
        status_text.append(f"{tools_count}\n", style="cyan")
        status_text.append(f"Recursos: ", style="white")
        status_text.append(f"{resources_count}\n", style="cyan")
        status_text.append(f"Mensajes en historial: ", style="white")
        status_text.append(f"{history_count}", style="cyan")

        self.console.print()
        self.console.print(Panel(
            status_text,
            title="[bold cyan]Status[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        ))
        self.console.print()

    def show_stats(self, stats: dict):
        """Mostrar estadisticas de uso y conversaciones."""
        from datetime import datetime

        # Si no hay datos
        if stats['total_conversations'] == 0:
            self.console.print()
            self.show_info("No hay estadisticas disponibles aun. Realiza algunas consultas primero!")
            self.console.print()
            return

        # Crear contenido del panel
        content = []

        # Seccion: Resumen General
        content.append("[bold cyan]Resumen General[/bold cyan]")
        content.append(f"  Total de conversaciones: [cyan]{stats['total_conversations']}[/cyan]")

        # Rango de fechas
        if stats['date_range']:
            try:
                first_date = datetime.fromisoformat(stats['date_range']['first'])
                last_date = datetime.fromisoformat(stats['date_range']['last'])
                content.append(f"  Primer consulta: [dim]{first_date.strftime('%Y-%m-%d %H:%M')}[/dim]")
                content.append(f"  Ultima consulta: [dim]{last_date.strftime('%Y-%m-%d %H:%M')}[/dim]")
            except:
                pass

        content.append("")

        # Seccion: Herramientas Usadas
        tools_usage = stats.get('tools_usage', {})
        if tools_usage:
            content.append("[bold cyan]Herramientas Mas Usadas[/bold cyan]")

            # Ordenar herramientas por uso
            sorted_tools = sorted(tools_usage.items(), key=lambda x: x[1], reverse=True)
            max_count = max(tools_usage.values()) if tools_usage else 1

            # Mostrar top 10 herramientas
            for tool_name, count in sorted_tools[:10]:
                # Crear barra ASCII
                bar_length = int((count / max_count) * 30)
                bar = "[cyan]" + "█" * bar_length + "[/cyan]"

                # Formatear nombre de herramienta
                tool_display = tool_name[:25] + "..." if len(tool_name) > 25 else tool_name

                content.append(f"  {tool_display:30} {bar} [yellow]{count}[/yellow]")

            # Mostrar total de herramientas diferentes
            content.append("")
            content.append(f"  [dim]Total de herramientas diferentes usadas: {len(tools_usage)}[/dim]")

            # Calcular promedio
            avg_tools = sum(tools_usage.values()) / stats['total_conversations']
            content.append(f"  [dim]Promedio de herramientas por consulta: {avg_tools:.1f}[/dim]")
        else:
            content.append("[bold cyan]Herramientas Usadas[/bold cyan]")
            content.append("  [dim]No se han usado herramientas aun[/dim]")

        # Unir todo el contenido
        panel_content = "\n".join(content)

        # Mostrar panel
        self.console.print()
        self.console.print(Panel(
            panel_content,
            title="[bold magenta]Estadisticas de Uso[/bold magenta]",
            border_style="magenta",
            padding=(1, 2)
        ))
        self.console.print()

    def show_examples(self, tools: list):
        """Mostrar ejemplos de consultas basados en herramientas disponibles."""
        import random

        # Mapeo de herramientas a ejemplos (usando nombres REALES del servidor)
        examples_map = {
            "fetch_series_metadata_tool": {
                "title": "Obtener Metadata de Series",
                "queries": [
                    "Muéstrame información sobre UNRATE",
                    "¿Qué es la serie GDP?",
                    "Dame detalles de CPIAUCSL"
                ],
                "description": "Obtiene metadata de una serie económica de FRED"
            },
            "fetch_series_observations_tool": {
                "title": "Descargar Datos Históricos",
                "queries": [
                    "Descarga datos de GDP desde 2020",
                    "Obtén observaciones de UNRATE desde enero 2023",
                    "Dame los datos de CPIAUCSL de los últimos 5 años"
                ],
                "description": "Descarga observaciones históricas de series FRED"
            },
            "plot_fred_series_tool": {
                "title": "Crear Gráficos de Series",
                "queries": [
                    "Grafica CPIAUCSL de los últimos 5 años",
                    "Plotea GDP desde 2020 hasta hoy",
                    "Muéstrame un gráfico de UNRATE desde 2015"
                ],
                "description": "Crea gráficos de series económicas con estilo APA"
            },
            "plot_dual_axis_tool": {
                "title": "Comparar Dos Series",
                "queries": [
                    "Compara UNRATE con CPIAUCSL en un gráfico",
                    "Grafica GDP vs FEDFUNDS con dos ejes",
                    "Muestra UNRATE y PAYEMS juntos desde 2020"
                ],
                "description": "Compara dos series en un gráfico de eje dual"
            },
            "search_fred_series_tool": {
                "title": "Buscar Series en FRED",
                "queries": [
                    "Busca series sobre empleo",
                    "Encuentra datos de inflación disponibles",
                    "¿Qué series hay sobre tasas de interés?"
                ],
                "description": "Busca series disponibles en FRED por palabra clave"
            },
            "build_fred_dataset_tool": {
                "title": "Construir Dataset Multi-Series",
                "queries": [
                    "Construye un dataset con UNRATE, GDP y CPIAUCSL",
                    "Crea un dataset con inflación YoY y unemployment desde 2010",
                    "Construye dataset con GDP (QoQ) y FEDFUNDS desde 2000"
                ],
                "description": "Construye dataset unificado con múltiples series y transformaciones"
            },
            "analyze_differencing_tool": {
                "title": "Análisis de Diferenciación",
                "queries": [
                    "Analiza la estacionariedad de GDP",
                    "Muestra diferenciación de CPIAUCSL",
                    "Aplica test ADF a UNRATE"
                ],
                "description": "Analiza diferenciación y estacionariedad con test ADF"
            },
            "plot_from_dataset_tool": {
                "title": "Graficar desde Dataset",
                "queries": [
                    "Grafica UNRATE vs CPIAUCSL_YoY del último dataset",
                    "Plotea GDP_QoQ con FEDFUNDS desde el dataset",
                    "Muestra columnas del dataset más reciente"
                ],
                "description": "Crea gráficos usando datasets previamente construidos"
            },
            "fetch_fred_releases_tool": {
                "title": "Listar Releases de FRED",
                "queries": [
                    "Muéstrame los releases disponibles en FRED",
                    "Lista los comunicados económicos de FRED",
                    "¿Qué releases hay en FRED?"
                ],
                "description": "Obtiene lista de releases económicos de FRED"
            }
        }

        # Obtener nombres de herramientas disponibles
        available_tool_names = [tool.name for tool in tools]

        # Filtrar ejemplos basados en herramientas disponibles
        available_examples = []
        for tool_name, example_data in examples_map.items():
            if tool_name in available_tool_names:
                available_examples.append((tool_name, example_data))

        # Si no hay suficientes coincidencias, agregar ejemplos genéricos útiles
        if len(available_examples) < 3:
            generic_examples = [
                ("general_metadata", {
                    "title": "Explorar Series Económicas",
                    "queries": [
                        "¿Qué series económicas están disponibles?",
                        "Busca series sobre desempleo",
                        "Muéstrame información sobre la serie GDP"
                    ],
                    "description": "Explora y descubre series económicas en FRED"
                }),
                ("general_viz", {
                    "title": "Crear Visualizaciones",
                    "queries": [
                        "Grafica la tasa de desempleo de los últimos años",
                        "Compara inflación con tasas de interés",
                        "Muéstrame un gráfico de GDP desde 2015"
                    ],
                    "description": "Crea gráficos profesionales de datos económicos"
                }),
                ("general_analysis", {
                    "title": "Análisis de Datos",
                    "queries": [
                        "Analiza la tendencia de UNRATE",
                        "Construye un dataset con múltiples indicadores",
                        "Descarga datos históricos de inflación"
                    ],
                    "description": "Analiza y procesa datos macroeconómicos"
                })
            ]
            # Agregar ejemplos genéricos hasta tener al menos 4
            for generic in generic_examples:
                if generic[0] not in [ex[0] for ex in available_examples]:
                    available_examples.append(generic)
                if len(available_examples) >= 5:
                    break

        # Seleccionar hasta 4 ejemplos aleatorios
        num_to_show = min(4, len(available_examples))
        selected_examples = random.sample(available_examples, num_to_show)

        # Construir contenido del panel
        content = []
        content.append("[bold cyan]Ejemplos de Consultas Interactivas[/bold cyan]")
        content.append("[dim]Basados en tus herramientas MCP disponibles[/dim]")
        content.append("")

        for i, (tool_name, example_data) in enumerate(selected_examples, 1):
            content.append(f"[bold yellow][{i}] {example_data['title']}[/bold yellow]")

            # Seleccionar un ejemplo aleatorio de los disponibles
            example_query = random.choice(example_data['queries'])
            content.append(f"    [cyan]\"{example_query}\"[/cyan]")

            # Mostrar descripción
            content.append(f"    [dim]{example_data['description']}[/dim]")

            # Mostrar herramienta solo si no es genérica
            if not tool_name.startswith("general"):
                content.append(f"    [dim]Usa: {tool_name}[/dim]")

            content.append("")

        # Agregar tips adicionales
        content.append("[bold green]Tips Adicionales:[/bold green]")
        content.append("  - Copia y pega estos ejemplos para probarlos")
        content.append("  - Usa /tools para ver todas las herramientas")
        content.append("  - Usa /resources para ver recursos MCP disponibles")
        content.append("  - Escribe /help para ver todos los comandos")

        panel_content = "\n".join(content)

        # Mostrar panel
        self.console.print()
        self.console.print(Panel(
            panel_content,
            title="[bold magenta]Guía de Ejemplos[/bold magenta]",
            border_style="magenta",
            padding=(1, 2)
        ))
        self.console.print()

    # ==================== FILE DETECTION & HANDLING ====================

    def extract_file_paths(self, text: str) -> list:
        """Extrae rutas de archivos del texto usando regex."""
        # Patrón para rutas de Windows (C:\...) y Unix (/...)
        pattern = r'(?:^|[\s•])((?:[A-Za-z]:[\\\/]|\/)[^\s:*?"<>|\n]+\.(?:png|jpg|jpeg|gif|csv|xlsx?|json|txt|pdf))'
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)

        # Validar que los archivos existan
        valid_files = []
        for path in matches:
            if os.path.exists(path):
                valid_files.append(path)

        return valid_files

    def show_file_attachments(self, file_paths: list):
        """Muestra archivos detectados con opción de abrir."""
        if not file_paths:
            return

        self.console.print()
        self.console.print("[bold cyan]Archivos generados:[/bold cyan]")

        for i, file_path in enumerate(file_paths, 1):
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1].upper()
            file_size = os.path.getsize(file_path)

            # Formatear tamaño
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"

            # Determinar ícono según extensión
            if file_ext in ['.PNG', '.JPG', '.JPEG', '.GIF']:
                icon = "[cyan][IMG][/cyan]"
            elif file_ext in ['.CSV', '.XLSX', '.XLS']:
                icon = "[green][DATA][/green]"
            elif file_ext in ['.JSON', '.TXT']:
                icon = "[yellow][TEXT][/yellow]"
            else:
                icon = "[blue][FILE][/blue]"

            self.console.print(
                f"  {icon} {file_name} [dim]({size_str})[/dim]\n"
                f"    [dim]{file_path}[/dim]"
            )

        self.console.print()
        self.console.print("[dim]Tip: Puedes abrir los archivos desde tu explorador de archivos[/dim]")
        self.console.print()

    # ==================== FETCH TOOLS VISUALIZATION ====================

    def show_series_metadata(self, metadata_json: dict):
        """Mostrar metadata de series FRED de forma visual."""
        data = metadata_json.get("data", {})

        # Construir panel con información clave
        content = []
        content.append(f"[bold cyan]{data.get('title', 'N/A')}[/bold cyan]")
        content.append(f"[dim]ID: {data.get('id', 'N/A')}[/dim]")
        content.append("")

        # Información principal
        info_table = Table(show_header=False, box=None, padding=(0, 1))
        info_table.add_column("Label", style="yellow", width=20)
        info_table.add_column("Value", style="white")

        info_table.add_row("Frecuencia", data.get('frequency', 'N/A'))
        info_table.add_row("Unidades", data.get('units', 'N/A'))
        info_table.add_row("Ajuste estacional", data.get('seasonal_adjustment', 'N/A'))
        info_table.add_row("Popularidad", data.get('popularity', 'N/A'))
        info_table.add_row("Período", f"{data.get('observation_start', 'N/A')} a {data.get('observation_end', 'N/A')}")
        info_table.add_row("Última actualización", data.get('last_updated', 'N/A'))

        self.console.print()
        self.console.print(Panel(
            info_table,
            title=f"[bold cyan]Serie: {data.get('id', 'N/A')}[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        ))

        # Notas (si existen y no están vacías)
        notes = data.get('notes', '')
        if notes and notes.strip() and notes != 'nan':
            notes_truncated = notes[:500] + "..." if len(notes) > 500 else notes
            self.console.print()
            self.console.print(Panel(
                notes_truncated,
                title="[dim]Notas[/dim]",
                border_style="dim",
                padding=(1, 2)
            ))

        self.console.print()

    def show_series_observations(self, observations_json: dict):
        """Mostrar observaciones de series FRED con estadísticas y guardar archivos."""
        import pandas as pd
        from datetime import datetime

        data = observations_json.get("data", [])
        metadata = observations_json.get("metadata", {})
        series_id = observations_json.get("series_id", "N/A")

        total_count = metadata.get("total_count", len(data))
        date_range = metadata.get("date_range", {})

        # Guardar datos en archivos CSV y Excel si hay más de 20 observaciones
        saved_files = []
        if len(data) > 20:
            try:
                # Crear directorio para datos
                os.makedirs("fred_data", exist_ok=True)

                # Crear DataFrame
                df = pd.DataFrame(data)

                # Limpiar fechas si tienen timestamp
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

                # Generar nombre de archivo con timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                base_filename = f"fred_data/{series_id}_observations_{timestamp}"

                # Guardar CSV
                csv_path = f"{base_filename}.csv"
                df.to_csv(csv_path, index=False)
                saved_files.append(csv_path)

                # Guardar Excel
                excel_path = f"{base_filename}.xlsx"
                df.to_excel(excel_path, index=False, sheet_name=series_id[:31])  # Excel sheet name max 31 chars
                saved_files.append(excel_path)

            except Exception as e:
                self.show_warning(f"No se pudieron guardar archivos: {e}")

        # Crear tabla con preview de datos (primeros y últimos registros)
        table = Table(
            title=f"Observaciones: {series_id} (Total: {total_count})",
            border_style="green",
            show_lines=False
        )

        table.add_column("Fecha", style="cyan", no_wrap=True)
        table.add_column("Valor", style="yellow", justify="right")

        # Mostrar primeros 5 y últimos 5
        preview_count = 5
        if len(data) <= preview_count * 2:
            # Si hay pocos datos, mostrar todos
            for obs in data:
                date = obs.get('date', 'N/A')
                if 'T' in str(date):
                    date = date.split('T')[0]
                value = obs.get('value', 'N/A')
                table.add_row(str(date), f"{float(value):.2f}" if value != 'N/A' else 'N/A')
        else:
            # Mostrar primeros 5
            for obs in data[:preview_count]:
                date = obs.get('date', 'N/A')
                if 'T' in str(date):
                    date = date.split('T')[0]
                value = obs.get('value', 'N/A')
                table.add_row(str(date), f"{float(value):.2f}" if value != 'N/A' else 'N/A')

            table.add_row("[dim]...[/dim]", "[dim]...[/dim]")

            # Mostrar últimos 5
            for obs in data[-preview_count:]:
                date = obs.get('date', 'N/A')
                if 'T' in str(date):
                    date = date.split('T')[0]
                value = obs.get('value', 'N/A')
                table.add_row(str(date), f"{float(value):.2f}" if value != 'N/A' else 'N/A')

        self.console.print()
        self.console.print(table)

        # Mostrar estadísticas
        if data:
            values = [float(obs.get('value', 0)) for obs in data if obs.get('value') not in ['N/A', None, 'nan']]
            if values:
                stats_text = Text()
                stats_text.append("Estadísticas: ", style="bold white")
                stats_text.append(f"Mín: {min(values):.2f}  ", style="cyan")
                stats_text.append(f"Máx: {max(values):.2f}  ", style="cyan")
                stats_text.append(f"Promedio: {sum(values)/len(values):.2f}", style="cyan")

                self.console.print()
                self.console.print(stats_text)

        # Mostrar archivos guardados
        if saved_files:
            self.console.print()
            self.console.print("[bold green]Datos completos guardados:[/bold green]")
            for file_path in saved_files:
                file_abs_path = os.path.abspath(file_path)
                file_size = os.path.getsize(file_path)
                size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024 * 1024):.1f} MB"

                file_ext = os.path.splitext(file_path)[1].upper()
                icon = "[green][DATA][/green]" if file_ext in ['.CSV', '.XLSX'] else "[blue][FILE][/blue]"

                self.console.print(f"  {icon} {os.path.basename(file_path)} [dim]({size_str})[/dim]")
                self.console.print(f"    [dim]{file_abs_path}[/dim]")

        self.console.print()

    def show_search_results(self, search_json: dict):
        """Mostrar resultados de búsqueda de series FRED."""
        data = search_json.get("data", [])
        metadata = search_json.get("metadata", {})
        search_text = search_json.get("search_text", "N/A")

        total_count = metadata.get("total_count", len(data))
        returned_count = metadata.get("returned_count", len(data))

        if not data:
            self.console.print()
            self.show_warning(f"No se encontraron resultados para '{search_text}'")
            self.console.print()
            return

        # Crear tabla con resultados
        table = Table(
            title=f"Búsqueda: '{search_text}' ({returned_count} de {total_count} resultados)",
            border_style="magenta",
            show_lines=True
        )

        table.add_column("#", style="dim", width=3)
        table.add_column("ID", style="cyan", no_wrap=True, width=12)
        table.add_column("Título", style="white", no_wrap=False)
        table.add_column("Popularidad", style="yellow", justify="right", width=10)
        table.add_column("Frecuencia", style="green", width=10)

        # Mostrar hasta 15 resultados
        for i, result in enumerate(data[:15], 1):
            series_id = result.get('id', 'N/A')
            title = result.get('title', 'N/A')
            popularity = result.get('popularity', 'N/A')
            frequency = result.get('frequency_short', result.get('frequency', 'N/A'))

            # Truncar título si es muy largo
            if len(title) > 60:
                title = title[:57] + "..."

            table.add_row(
                str(i),
                series_id,
                title,
                str(popularity),
                frequency
            )

        self.console.print()
        self.console.print(table)

        # Tip
        if returned_count > 15:
            self.console.print()
            self.console.print(f"[dim]Mostrando primeras 15 de {returned_count} series. Refina tu búsqueda para mejores resultados.[/dim]")

        self.console.print()
        self.console.print("[dim cyan]Tip: Usa /tools fetch_series_metadata_tool para ver detalles de una serie específica[/dim]")
        self.console.print()

    def show_fred_releases(self, releases_json: dict):
        """Mostrar lista de releases (comunicados) de FRED."""
        data = releases_json.get("data", [])
        metadata = releases_json.get("metadata", {})
        total_count = metadata.get("total_count", len(data))

        if not data:
            self.console.print()
            self.show_warning("No se encontraron releases de FRED")
            self.console.print()
            return

        # Crear tabla con releases
        table = Table(
            title=f"Releases de FRED (Total: {total_count})",
            border_style="blue",
            show_lines=True
        )

        table.add_column("#", style="dim", width=3)
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Nombre", style="white", no_wrap=False)
        table.add_column("Link", style="blue", no_wrap=False, overflow="fold")

        # Mostrar primeros 20 releases
        for i, release in enumerate(data[:20], 1):
            release_id = str(release.get('id', 'N/A'))
            name = release.get('name', 'N/A')
            link = release.get('link', 'N/A')

            # Truncar nombre si es muy largo
            if len(name) > 50:
                name = name[:47] + "..."

            # Truncar link
            if len(link) > 40:
                link = link[:37] + "..."

            table.add_row(str(i), release_id, name, link)

        self.console.print()
        self.console.print(table)

        if total_count > 20:
            self.console.print()
            self.console.print(f"[dim]Mostrando primeros 20 de {total_count} releases.[/dim]")

        self.console.print()
        self.console.print("[dim cyan]Tip: Usa fetch_release_details_tool con un ID para ver detalles de un release[/dim]")
        self.console.print()

    def show_release_details(self, release_json: dict):
        """Mostrar detalles de un release específico de FRED."""
        data = release_json.get("data", {})
        release_id = release_json.get("release_id", "N/A")

        # Panel con información del release
        info_table = Table(show_header=False, box=None, padding=(0, 1))
        info_table.add_column("Label", style="yellow", width=20)
        info_table.add_column("Value", style="white")

        info_table.add_row("ID", str(data.get('id', 'N/A')))
        info_table.add_row("Nombre", data.get('name', 'N/A'))
        info_table.add_row("Enlace", data.get('link', 'N/A'))

        # Agregar press release si existe
        if 'press_release' in data and data['press_release']:
            info_table.add_row("Press Release", "Sí")

        # Agregar fechas si existen
        if 'realtime_start' in data:
            info_table.add_row("Realtime Start", data.get('realtime_start', 'N/A'))
        if 'realtime_end' in data:
            info_table.add_row("Realtime End", data.get('realtime_end', 'N/A'))

        self.console.print()
        self.console.print(Panel(
            info_table,
            title=f"[bold blue]Release: {data.get('name', release_id)}[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        ))

        # Notas si existen
        notes = data.get('notes', '')
        if notes and notes.strip():
            notes_truncated = notes[:400] + "..." if len(notes) > 400 else notes
            self.console.print()
            self.console.print(Panel(
                notes_truncated,
                title="[dim]Notas[/dim]",
                border_style="dim",
                padding=(1, 2)
            ))

        self.console.print()

    def show_category_details(self, category_json: dict):
        """Mostrar detalles de una categoría de FRED."""
        data = category_json.get("data", {})
        category_id = category_json.get("category_id", "N/A")

        # Panel con información de la categoría
        info_table = Table(show_header=False, box=None, padding=(0, 1))
        info_table.add_column("Label", style="yellow", width=20)
        info_table.add_column("Value", style="white")

        info_table.add_row("ID", str(data.get('id', 'N/A')))
        info_table.add_row("Nombre", data.get('name', 'N/A'))

        # Parent category si existe
        if 'parent_id' in data and data['parent_id']:
            info_table.add_row("Parent ID", str(data.get('parent_id', 'N/A')))

        self.console.print()
        self.console.print(Panel(
            info_table,
            title=f"[bold green]Categoría: {data.get('name', category_id)}[/bold green]",
            border_style="green",
            padding=(1, 2)
        ))

        # Notas si existen
        notes = data.get('notes', '')
        if notes and notes.strip():
            notes_truncated = notes[:400] + "..." if len(notes) > 400 else notes
            self.console.print()
            self.console.print(Panel(
                notes_truncated,
                title="[dim]Descripción[/dim]",
                border_style="dim",
                padding=(1, 2)
            ))

        self.console.print()

    def show_fred_sources(self, sources_json: dict):
        """Mostrar lista de fuentes de datos de FRED."""
        data = sources_json.get("data", [])
        metadata = sources_json.get("metadata", {})
        total_count = metadata.get("total_count", len(data))

        if not data:
            self.console.print()
            self.show_warning("No se encontraron fuentes de datos en FRED")
            self.console.print()
            return

        # Crear tabla con fuentes
        table = Table(
            title=f"Fuentes de Datos FRED (Total: {total_count})",
            border_style="yellow",
            show_lines=True
        )

        table.add_column("#", style="dim", width=3)
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Nombre", style="white", no_wrap=False)
        table.add_column("Link", style="blue", no_wrap=False, overflow="fold")

        # Mostrar primeras 15 fuentes
        for i, source in enumerate(data[:15], 1):
            source_id = str(source.get('id', 'N/A'))
            name = source.get('name', 'N/A')
            link = source.get('link', 'N/A')

            # Truncar nombre si es muy largo
            if len(name) > 45:
                name = name[:42] + "..."

            # Truncar link
            if len(link) > 35:
                link = link[:32] + "..."

            table.add_row(str(i), source_id, name, link)

        self.console.print()
        self.console.print(table)

        if total_count > 15:
            self.console.print()
            self.console.print(f"[dim]Mostrando primeras 15 de {total_count} fuentes.[/dim]")

        self.console.print()
        self.console.print("[dim cyan]Tip: Cada fuente representa una organización que provee datos a FRED[/dim]")
        self.console.print()

    def open_file(self, file_path: str) -> bool:
        """Abre un archivo con el visor predeterminado del sistema."""
        try:
            if not os.path.exists(file_path):
                self.show_error(FileNotFoundError(f"Archivo no encontrado: {file_path}"), "")
                return False

            # Windows
            if os.name == 'nt':
                os.startfile(file_path)
            # macOS
            elif os.name == 'posix' and os.uname().sysname == 'Darwin':
                subprocess.run(['open', file_path], check=True)
            # Linux/Unix
            else:
                subprocess.run(['xdg-open', file_path], check=True)

            self.show_success(f"Archivo abierto: {os.path.basename(file_path)}")
            return True

        except Exception as e:
            self.show_error(e, f"Al abrir archivo: {file_path}")
            return False
