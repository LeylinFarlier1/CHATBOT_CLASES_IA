# Infrastructure Layer - External Integrations

This layer contains **implementations of external services and APIs**. It provides concrete implementations of interfaces defined in `core/interfaces/`.

## Structure

```
infrastructure/
├── llm/             # LLM provider implementations
│   ├── base_provider.py      # Abstract base class
│   ├── claude_provider.py    # Anthropic Claude
│   ├── openai_provider.py    # OpenAI GPT
│   ├── gemini_provider.py    # Google Gemini
│   └── provider_factory.py   # Factory pattern
├── mcp/             # MCP client wrapper
│   ├── mcp_client.py         # Wrapper over mcp.ClientSession
│   └── mcp_config.py         # MCP configuration
└── gui/             # GUI backend management
    ├── gui_backend.py        # Main GUI backend (refactored)
    └── backends/             # Platform-specific backends
```

## Principles

- **Implements interfaces**: Concrete implementations of `core/interfaces/`
- **Dependency Inversion**: Depends on abstractions, not on core business logic
- **Swappable**: Easy to replace (e.g., Claude → OpenAI, Tkinter → PyQt)
- **Isolated**: Failures in one provider don't affect others

## LLM Providers

All providers implement `ILLMProvider`:

```python
from core.interfaces.llm_provider import ILLMProvider

class ClaudeProvider(ILLMProvider):
    def process_messages(self, messages, tools, max_tokens):
        # Call Anthropic API
        pass

    def supports_tools(self) -> bool:
        return True  # Claude supports MCP tools
```

## Factory Pattern

Use `LLMProviderFactory` to create providers:

```python
from infrastructure.llm.provider_factory import LLMProviderFactory

# Create Claude provider
provider = LLMProviderFactory.create_provider("claude", model_key="sonnet-3.7")

# Switch to OpenAI
provider = LLMProviderFactory.create_provider("openai", model_key="gpt-4o")
```

## Adding New Provider

1. Create `infrastructure/llm/mistral_provider.py`
2. Implement `ILLMProvider` interface
3. Register in `provider_factory.py`
4. Add config to `config/llm_config.py`

**No changes to core logic required!** ✅

## Testing

```bash
# Unit tests (with mocked APIs)
pytest tests/unit/infrastructure/

# Integration tests (requires API keys)
pytest tests/integration/ --run-integration
```

---

**Status:** 🚧 Under construction (Phase 4)
