
# Core Layer - Domain & Business Logic

This layer contains the **business logic and domain models** of the application. It's the heart of the system and is **independent of any external frameworks or infrastructure**.

## Structure

```
core/
├── models/          # Domain models (Message, Conversation, ToolResult)
├── services/        # Business services (MCPService, LLMService, ConversationService)
└── interfaces/      # Interfaces/Protocols (ILLMProvider, IUIRenderer, ICommandExecutor)
```

## Principles

- **Framework-independent**: No dependencies on Textual, Rich, or external libraries
- **Testable**: All services can be unit tested with mocks
- **Reusable**: Can be used in CLI, TUI, Web API, or notebooks
- **SOLID**: Follows Single Responsibility, Open/Closed, Dependency Inversion

## Dependencies

**Allowed:**
- Other `core/` modules
- Python standard library
- Type hints and protocols

**NOT Allowed:**
- Direct imports from `infrastructure/`, `presentation/`, or `application/`
- UI frameworks (Textual, Rich)
- External API clients (Anthropic, OpenAI)

## Usage Example

```python
from core.services.mcp_service import MCPService
from core.services.llm_service import LLMService
from infrastructure.llm.claude_provider import ClaudeProvider
from infrastructure.mcp.mcp_client import MCPClientWrapper

# Create infrastructure
mcp_client = MCPClientWrapper()
claude_provider = ClaudeProvider(api_key="...")

# Create services (core)
mcp_service = MCPService(mcp_client)
llm_service = LLMService(claude_provider, mcp_service)

# Use in any context (CLI, TUI, API)
response = await llm_service.process_query("Show me GDP data", conversation)
```

## Testing

Run unit tests:
```bash
pytest tests/unit/core/
```

---

**Status:** 🚧 Under construction (Phase 2-5)
