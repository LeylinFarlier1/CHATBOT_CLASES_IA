# Application Layer - Use Cases & Commands

This layer contains **application-specific logic** - use cases (workflows) and commands (user actions). It orchestrates the domain services to fulfill user requests.

## Structure

```
application/
├── use_cases/              # Use cases (business workflows)
│   ├── process_query.py   # Process user query with LLM
│   ├── connect_mcp.py     # Connect to MCP server
│   └── execute_tool.py    # Execute MCP tool
└── commands/              # Command system
    ├── command_registry.py    # Command registration
    ├── base_command.py        # Abstract command base
    └── impl/                  # Command implementations
        ├── help_command.py
        ├── tools_command.py
        ├── resources_command.py
        ├── history_command.py
        ├── model_command.py
        └── ...
```

## Use Cases

**Use cases** encapsulate complete business workflows:

```python
from application.use_cases.process_query import ProcessQueryUseCase

class ProcessQueryUseCase:
    """
    Use Case: Process user query with LLM

    Steps:
    1. Get current conversation
    2. Add user message
    3. Call LLM service (handles tool execution)
    4. Save updated conversation
    5. Return response
    """

    def __init__(self, llm_service, conversation_service):
        self.llm_service = llm_service
        self.conversation_service = conversation_service

    async def execute(self, query: str) -> LLMResponse:
        conversation = self.conversation_service.get_current()
        response = await self.llm_service.process_query(query, conversation)
        self.conversation_service.save(conversation)
        return response
```

**Why Use Cases?**
- ✅ **Single responsibility**: One workflow per class
- ✅ **Testable**: Easy to mock dependencies
- ✅ **Reusable**: Same use case for CLI, TUI, API
- ✅ **Clear intent**: Name describes what it does

## Commands

**Commands** are user actions triggered by slash commands (`/help`, `/tools`, etc.):

```python
from application.commands.base_command import BaseCommand, CommandResult

class HelpCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "help"

    @property
    def description(self) -> str:
        return "Show available commands"

    @property
    def aliases(self) -> list:
        return ["h", "?"]

    async def execute(self, args: str) -> CommandResult:
        help_text = self._generate_help()
        return CommandResult(success=True, output=help_text)
```

**Command Registry:**
```python
from application.commands.command_registry import CommandRegistry

# Register commands
registry = CommandRegistry(
    mcp_service=mcp_service,
    llm_service=llm_service,
    conversation_service=conversation_service
)

# Execute command
result = await registry.execute("/help")
```

## Architecture Benefits

**Before (commands.py):**
- ❌ Tightly coupled to client
- ❌ Hard to test (needs full client)
- ❌ Hard to extend (modify class)

**After (application/commands/):**
- ✅ Loosely coupled (dependency injection)
- ✅ Easy to test (mock services)
- ✅ Easy to extend (add new command file)

**Adding New Command:**
```python
# 1. Create file: application/commands/impl/export_command.py
class ExportCommand(BaseCommand):
    def __init__(self, conversation_service):
        self.conversation_service = conversation_service

    async def execute(self, args: str) -> CommandResult:
        # Implementation
        pass

# 2. Register in command_registry.py
self.register(ExportCommand(self.conversation_service))

# Done! No modifications to existing code
```

## Use Case vs Command

**Use Case:** Internal workflow
- Called by UI
- Returns structured data
- Example: `ProcessQueryUseCase`

**Command:** User action
- Called by `/command`
- Returns formatted output
- Example: `HelpCommand`

**Example:**
```python
# UI uses use case directly
response = await process_query_uc.execute("Show GDP")

# UI uses command through registry
result = await command_registry.execute("/help")
```

## Testing

```bash
# Test use cases
pytest tests/unit/application/use_cases/

# Test commands
pytest tests/unit/application/commands/
```

---

**Status:** 🚧 Under construction (Phase 6, 9)
