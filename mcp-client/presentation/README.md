# Presentation Layer - User Interfaces

This layer contains **all UI implementations** (CLI, TUI, presenters). It's responsible for displaying data to users and capturing their input.

## Structure

```
presentation/
├── cli/                    # Command-Line Interface
│   ├── cli_app.py         # CLI application (refactored from client.py)
│   ├── console_renderer.py # Rich-based rendering
│   └── input_handler.py   # Input with autocompletion
├── tui/                   # Text User Interface (Textual)
│   ├── tui_app.py         # TUI application (refactored ~300 lines)
│   ├── panels/            # UI components
│   │   ├── chat_panel.py
│   │   ├── dataset_panel.py
│   │   ├── history_panel.py
│   │   └── status_bar.py
│   └── formatters/        # Result formatters
│       ├── tool_result_formatter.py
│       └── plot_formatter.py
└── presenters/            # Presentation logic
    ├── fred_data_presenter.py  # Format FRED data for display
    └── file_presenter.py       # Format file information
```

## Principles

- **UI-only**: No business logic (delegated to `application/` and `core/`)
- **Framework-specific**: Can use Textual, Rich, or any UI library
- **Thin layer**: Orchestrates use cases, doesn't implement them
- **Testable**: UI logic separated from display rendering

## CLI vs TUI

Both CLI and TUI share the same **core services** but have different UIs:

**CLI (console_renderer.py):**
- Linear output with Rich panels
- Simple prompt-based input
- Lightweight and fast

**TUI (tui_app.py):**
- Interactive panels with Textual
- Real-time updates
- Rich visual interface

**Shared Logic:**
```python
# Both use the same services!
from core.services.llm_service import LLMService
from core.services.mcp_service import MCPService
from application.use_cases.process_query import ProcessQueryUseCase

# CLI
class CLIApp:
    def __init__(self):
        self.llm_service = LLMService(...)  # Same service
        self.process_query_uc = ProcessQueryUseCase(self.llm_service)

# TUI
class MacroMCPApp(App):
    def __init__(self):
        self.llm_service = LLMService(...)  # Same service
        self.process_query_uc = ProcessQueryUseCase(self.llm_service)
```

## Presenters

**Presenters** format data for display (not business logic):

```python
from presentation.presenters.fred_data_presenter import FredDataPresenter

# Convert FRED data to markdown/rich format
formatted = FredDataPresenter.format_series_metadata(metadata)

# Display with renderer
renderer.show_markdown(formatted)
```

**Separation:**
- ❌ **Old:** `console_ui.py` mixed formatting + rendering + file saving
- ✅ **New:** `fred_data_presenter.py` (formatting) + `console_renderer.py` (rendering)

## Refactoring Summary

**Before:**
- `tui_app.py`: 1907 lines (UI + business logic + MCP + LLM)
- `client.py`: 464 lines (duplicate logic)

**After:**
- `tui_app.py`: ~300 lines (UI only)
- `cli_app.py`: ~200 lines (UI only)
- **No duplication**: Shared services in `core/`

## Testing

```bash
# Unit tests (mocked services)
pytest tests/unit/presentation/

# Integration tests (requires UI)
pytest tests/integration/test_tui_app.py
```

---

**Status:** 🚧 Under construction (Phase 7-8)
