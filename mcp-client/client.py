import asyncio
import os
import sys
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

# Importar la nueva UI
from ui import ConsoleUI
# Importar sistema de comandos
from commands import CommandHandler
# Importar utilidades de Fase 3
from utils import ConversationHistory, ResourceCache
from utils.input_handler import InputHandler

load_dotenv()  # load environment variables from .env


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        # Initialize UI
        self.ui = ConsoleUI()

        # Initialize conversation history (for Claude API)
        self.conversation_history = []

        # Initialize history manager (Fase 3)
        self.history_manager = ConversationHistory(max_items=100)

        # Initialize resource cache (Fase 3)
        self.cache = ResourceCache(ttl=300)  # 5 minutes TTL

        # Initialize input handler with autocompletion (Fase 3)
        self.input_handler = InputHandler(history_file=".mcp_history")


    async def connect(self, server_script_path: str = "server_mcp.py:server"):
        """Conectar a el MCP server python."""

        # Mostrar banner
        self.ui.show_banner()
        self.ui.print()

        # Mostrar mensaje de conexión
        self.ui.show_info("Conectando al servidor MCP...")

        # Configurar parámetros de servidor
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

        try:
            # Crear transporte y sesión
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            self.stdio, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

            # Inicializar sesión
            await self.session.initialize()

            # Listar herramientas disponibles
            response = await self.session.list_tools()
            tools = response.tools

            # Listar recursos disponibles
            resources_count = 0
            try:
                resources_response = await self.session.list_resources()
                resources = resources_response.resources
                resources_count = len(resources)
            except Exception as e:
                self.ui.show_warning(f"No se pudieron listar recursos: {e}")

            # Mostrar mensaje de conexión exitosa
            self.ui.show_connection_success(len(tools), resources_count)
            self.ui.print()

            # Inicializar command handler
            self.command_handler = CommandHandler(self)

            # Mostrar herramientas en formato tabla (opcional, comentado por defecto)
            # self.ui.show_tools_list(tools)

        except Exception as e:
            self.ui.show_error(e, "Durante la conexión al servidor MCP")
            raise


    async def process_query(self, query: str) -> str:
        """Process a user query using Claude + Macro MCP tools."""

        # Paso 1: Agregar mensaje del usuario al historial
        self.conversation_history.append({
            "role": "user",
            "content": query
        })

        # Usar el historial completo para mantener contexto
        messages = self.conversation_history.copy()

        # Paso 2: Obtener herramientas disponibles del servidor MCP (con caché)
        cached_tools = self.cache.get("tools_list")
        if cached_tools:
            # IMPORTANTE: Hacer copia para no modificar el caché
            available_tools = cached_tools.copy()
        else:
            response = await self.session.list_tools()
            available_tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                }
                for tool in response.tools
            ]
            self.cache.set("tools_list", available_tools)

        # Paso 2b: Agregar herramienta sintética para leer recursos MCP
        try:
            resources_response = await self.session.list_resources()
            if resources_response.resources:
                resource_uris = [str(r.uri) for r in resources_response.resources]

                # Verificar que no esté ya en la lista (por si acaso)
                if not any(t.get("name") == "read_mcp_resource" for t in available_tools):
                    available_tools.append({
                        "name": "read_mcp_resource",
                        "description": f"Lee un recurso MCP del servidor. Recursos disponibles: {', '.join(resource_uris)}",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "uri": {
                                    "type": "string",
                                    "description": f"URI del recurso a leer. Opciones: {', '.join(resource_uris)}"
                                }
                            },
                            "required": ["uri"]
                        }
                    })
        except Exception as e:
            self.ui.show_warning(f"No se pudieron obtener recursos: {e}")

        # Paso 3: Primer razonamiento de Claude con las herramientas disponibles
        # Crear progreso en vivo
        progress = self.ui.create_live_progress()

        with progress:
            # Iniciar tarea de progreso
            task = progress.add_task("[cyan]Enviando consulta a Claude AI...", total=None)

            claude_response = self.anthropic.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=4096,
                messages=messages,
                tools=available_tools,
            )

            # Actualizar estado: Claude ha respondido
            self.ui.update_progress_status(progress, task, "Claude ha procesado la consulta", "green")

        # Paso 4: Guardar la respuesta de Claude en el historial
        # Convertir content blocks a formato de diccionario
        assistant_content = []
        for content in claude_response.content:
            if content.type == "text":
                assistant_content.append({"type": "text", "text": content.text})
            elif content.type == "tool_use":
                assistant_content.append({
                    "type": "tool_use",
                    "id": content.id,
                    "name": content.name,
                    "input": content.input
                })

        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_content
        })

        # Paso 5: Procesar el contenido generado por Claude
        final_output = []
        tool_results = []
        tools_used = []  # Rastrear herramientas usadas

        # Crear progreso para ejecución de herramientas si es necesario
        has_tool_use = any(content.type == "tool_use" for content in claude_response.content)

        if has_tool_use:
            progress = self.ui.create_live_progress()
            with progress:
                task = progress.add_task("[cyan]Preparando ejecucion de herramientas...", total=None)

                for content in claude_response.content:
                    # Si Claude responde directamente con texto
                    if content.type == "text":
                        final_output.append(content.text)

                    # Si Claude decide usar una herramienta del MCP
                    elif content.type == "tool_use":
                        tool_name = content.name
                        tool_args = content.input or {}
                        tool_use_id = content.id

                        # Rastrear herramienta usada
                        tools_used.append(tool_name)

                        # Actualizar progreso con nombre de herramienta
                        args_preview = ", ".join([f"{k}={str(v)[:20]}..." if len(str(v)) > 20 else f"{k}={v}" for k, v in list(tool_args.items())[:2]])
                        self.ui.update_progress_status(progress, task, f"Ejecutando: {tool_name}({args_preview})", "yellow")

                        try:
                            # Manejar lectura de recursos MCP
                            if tool_name == "read_mcp_resource":
                                resource_uri = tool_args.get("uri")
                                resource_result = await self.session.read_resource(resource_uri)
                                result_text = (
                                    resource_result.contents[0].text
                                    if resource_result.contents and hasattr(resource_result.contents[0], "text")
                                    else str(resource_result.contents)
                                )
                            else:
                                # Ejecutar la herramienta MCP normal
                                tool_result = await self.session.call_tool(tool_name, tool_args)
                                result_text = (
                                    tool_result.content[0].text
                                    if tool_result.content and hasattr(tool_result.content[0], "text")
                                    else str(tool_result.content)
                                )

                            # Detectar y mostrar visualización mejorada para fetch tools
                            self._show_enhanced_fetch_result(tool_name, result_text)

                            # Agregar resultado a la lista de tool_results
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": result_text
                            })

                        except Exception as e:
                            error_msg = f"Error: {str(e)}"
                            self.ui.show_error(e, f"Al ejecutar herramienta '{tool_name}'")
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": error_msg,
                                "is_error": True
                            })

                # Finalizar progreso de herramientas
                self.ui.update_progress_status(progress, task, f"Herramientas ejecutadas ({len(tools_used)} total)", "green")
        else:
            # Sin herramientas, solo procesar texto
            for content in claude_response.content:
                if content.type == "text":
                    final_output.append(content.text)

        # Paso 6: Si hubo tool use, procesar resultados y obtener respuesta final
        if tool_results:
            # Agregar tool results al historial como mensaje del usuario
            self.conversation_history.append({
                "role": "user",
                "content": tool_results
            })

            # Crear progreso para interpretación
            progress = self.ui.create_live_progress()
            with progress:
                task = progress.add_task("[cyan]Interpretando resultados...", total=None)

                # Obtener respuesta final de Claude
                followup = self.anthropic.messages.create(
                    model="claude-3-5-haiku-20241022",
                    max_tokens=4096,
                    messages=self.conversation_history,
                )

                # Actualizar estado
                self.ui.update_progress_status(progress, task, "Respuesta generada exitosamente", "green")

            # Guardar respuesta final en el historial
            followup_content = []
            for content in followup.content:
                if content.type == "text":
                    followup_content.append({"type": "text", "text": content.text})
                    final_output.append(content.text)

            self.conversation_history.append({
                "role": "assistant",
                "content": followup_content
            })

        # Guardar en history_manager (Fase 3)
        final_response = "\n".join(final_output) if final_output else "No response generated."
        self.history_manager.add(
            query=query,
            response=final_response,
            tools_used=tools_used
        )

        # Agregar espacio después del progreso
        self.ui.print()

        return final_response

    def _show_enhanced_fetch_result(self, tool_name: str, result_text: str):
        """Detectar y mostrar visualización mejorada para herramientas de fetch."""
        import json

        # Lista de herramientas de fetch que tienen visualización mejorada
        fetch_tools = {
            "fetch_series_metadata_tool": "metadata",
            "fetch_series_observations_tool": "observations",
            "search_fred_series_tool": "search",
            "fetch_fred_releases_tool": "releases",
            "fetch_release_details_tool": "release_details",
            "fetch_category_details_tool": "category_details",
            "fetch_fred_sources_tool": "sources"
        }

        # Verificar si es una herramienta de fetch
        if tool_name not in fetch_tools:
            return

        try:
            # Intentar parsear el JSON
            result_json = json.loads(result_text)

            # Verificar que tiene la estructura esperada
            if "tool" not in result_json:
                return

            # Mostrar visualización según el tipo
            viz_type = fetch_tools[tool_name]

            if viz_type == "metadata":
                self.ui.show_series_metadata(result_json)
            elif viz_type == "observations":
                self.ui.show_series_observations(result_json)
            elif viz_type == "search":
                self.ui.show_search_results(result_json)
            elif viz_type == "releases":
                self.ui.show_fred_releases(result_json)
            elif viz_type == "release_details":
                self.ui.show_release_details(result_json)
            elif viz_type == "category_details":
                self.ui.show_category_details(result_json)
            elif viz_type == "sources":
                self.ui.show_fred_sources(result_json)

        except (json.JSONDecodeError, KeyError, Exception):
            # Si falla el parsing o no es el formato esperado, no hacer nada
            # Claude mostrará el resultado en texto normal
            pass

    async def chat_loop(self):
        """Inicia un bucle de chat interactivo para el cliente Macro MCP."""

        # Mostrar mensaje de bienvenida
        self.ui.show_welcome_message()

        while True:
            try:
                # Usar input handler con autocompletado (Fase 3)
                consulta = await self.input_handler.get_input("Consulta: ")

                if consulta.lower() in {"salir", "exit", "quit"}:
                    break

                if not consulta:
                    continue

                # Detectar si es un comando
                if consulta.startswith("/"):
                    result = await self.command_handler.execute(consulta)
                    if result == "EXIT_REQUESTED":
                        break
                    self.ui.print()
                    continue

                # Mostrar la consulta del usuario con formato
                self.ui.print()
                self.ui.show_user_query(consulta)
                self.ui.print()

                # Procesar la consulta con Claude + herramientas MCP
                respuesta = await self.process_query(consulta)

                # Mostrar la respuesta con markdown rendering
                self.ui.show_response(respuesta, render_markdown=True)

                # Detectar y mostrar archivos generados
                file_paths = self.ui.extract_file_paths(respuesta)
                if file_paths:
                    self.ui.show_file_attachments(file_paths)

            except KeyboardInterrupt:
                self.ui.print()
                self.ui.show_warning("Chat interrumpido por el usuario")
                break
            except Exception as e:
                self.ui.show_error(e, "Durante el procesamiento de la consulta")

        # Mostrar mensaje de despedida
        self.ui.show_goodbye()

    async def cleanup(self):
        """Limpia los recursos y cierra la sesión MCP."""
        self.ui.show_info("Cerrando la sesión y liberando recursos...")

        try:
            await self.exit_stack.aclose()
            self.ui.show_success("Recursos liberados correctamente")
        except Exception as e:
            self.ui.show_error(e, "Al cerrar el contexto asíncrono")

        self.ui.print()


async def main():
    """Punto de entrada principal del cliente Macro MCP."""
    if len(sys.argv) < 2:
        print("Uso: python client.py <ruta_al_script_del_servidor>")
        sys.exit(1)

    client = MCPClient()
    try:
        # Conectar al servidor MCP usando el script especificado
        await client.connect(sys.argv[1])
        await client.chat_loop()
    except KeyboardInterrupt:
        client.ui.print()
        client.ui.show_warning("Ejecución interrumpida por el usuario")
    except Exception as e:
        if hasattr(client, 'ui'):
            client.ui.show_error(e, "Error crítico en la aplicación")
        else:
            print(f"Error crítico: {e}")
    finally:
        # Cerrar y limpiar recursos
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
