# Macro MCP - Macroeconomic Analysis System

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.17.0-green)](https://github.com/anthropics/model-context-protocol)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> An advanced Model Context Protocol (MCP) server and client for macroeconomic data analysis powered by FRED (Federal Reserve Economic Data) and Claude AI.

## Overview

**Macro MCP** is a comprehensive system that combines the power of:
- **FRED API**: Access to 800,000+ economic time series
- **Claude AI**: Intelligent query processing and natural language interaction
- **MCP Protocol**: Seamless tool and resource integration
- **Modern UI**: Beautiful terminal (CLI) and full-screen (TUI) interfaces with visualizations

The system consists of two main components:
1. **MCP Server** (`macro/`): Exposes FRED data tools and resources
2. **MCP Client** (`mcp-client/`): Interactive CLI and TUI with Claude integration

---

## Key Features

### Data Acquisition (Fetch Tools)
- **Search FRED Series**: Intelligent search across 800,000+ series
- **Fetch Series Metadata**: Get detailed information about economic indicators
- **Fetch Observations**: Download historical data with date filtering
- **Explore Categories & Releases**: Navigate FRED's data taxonomy
- **Source Information**: Access data provenance

### Data Transformation (Build Tools)
- **ETL Pipeline**: Extract, Transform, Load workflow for multiple series
- **Transformations**: YoY, QoQ, MoM, differences, logs, percentage changes
- **Dataset Builder**: Unified datasets with synchronized dates
- **Export Formats**: CSV, Excel with complete metadata

### Visualization (Plot Tools)
- **Time Series Plots**: APA-style publication-ready charts
- **Dual-Axis Comparison**: Compare series with different units
- **Differencing Analysis**: ADF tests for stationarity
- **Plot from Dataset**: Visualize pre-built datasets without recalculation

### Client Features (Fase 3)
- **Two Interface Options**: 
  - CLI: Classic line-by-line interface with Rich formatting
  - TUI: Modern full-screen interface with Textual (v0.2.0+)
- **Conversation History**: Persistent storage with search capabilities
- **Resource Cache**: TTL-based caching (5 min default)
- **Autocompletion**: Smart input with economic keywords (CLI only)
- **Slash Commands**: 13+ commands for workflow management
- **Export Options**: Markdown and JSON formats
- **Rich UI**: Tables, progress bars, syntax highlighting

---

## Architecture

```
macro/
├── macro/                          # MCP Server
│   ├── app/
│   │   ├── server_mcp.py          # FastMCP server with 15+ tools
│   │   └── pyproject.toml         # Server dependencies
│   ├── tools/
│   │   ├── fetch/                 # Data acquisition tools (7 tools)
│   │   │   ├── fetch_series_observations.py
│   │   │   ├── fetch_series_metadata.py
│   │   │   ├── search_fred_series.py
│   │   │   ├── fetch_fred_releases.py
│   │   │   ├── fetch_release_details.py
│   │   │   ├── fetch_category_details.py
│   │   │   └── fetch_fred_sources.py
│   │   ├── plot/                  # Visualization tools (4 tools)
│   │   │   ├── plot_fred_series.py
│   │   │   ├── plot_dual_axis.py
│   │   │   ├── analyze_differencing.py
│   │   │   └── plot_from_dataset.py
│   │   └── build/                 # ETL pipeline (1 tool)
│   │       └── build_fred_dataset.py
│   └── resources/
│       ├── datasets.py            # MCP resource for dataset discovery
│       └── fred_endpoints.json    # FRED API endpoint configurations
│
├── mcp-client/                     # MCP Client
│   ├── tui_app.py                 # Main TUI application (v0.4.0)
│   ├── run_tui.py                 # TUI launcher script
│   ├── client.py                  # CLI client with Claude integration
│   ├── commands.py                # Slash command system
│   ├── gui_backend.py             # Auto-opening plot windows (v0.4.0)
│   ├── config/                    # Configuration management
│   ├── ui/
│   │   └── console_ui.py          # Rich-based UI components
│   ├── utils/                     # Client utilities
│   │   ├── history.py             # Conversation history manager
│   │   ├── cache.py               # TTL-based resource cache
│   │   └── input_handler.py      # Autocompletion with prompt-toolkit
│   ├── .env.example               # Environment variables template
│   ├── INSTALL_TUI.bat            # Windows installer
│   ├── INSTALL_TUI.sh             # Linux/macOS installer
│   └── pyproject.toml             # Client dependencies
│
├── init_db.py                      # Database initialization script
└── README.md                       # This file
```

> **Note:** Files like `nutrition.db`, `conversations/`, and `.env` are created automatically at runtime and are not included in the repository.

---

## Installation

### Prerequisites
- **Python 3.10 or higher**
- **[uv](https://github.com/astral-sh/uv) package manager** - Install with:
  ```bash
  # Windows (PowerShell)
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  
  # Linux/macOS
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **FRED API key** - [Get one free here](https://fred.stlouisfed.org/docs/api/api_key.html) (required for data access)
- **Anthropic API key** - [Get one here](https://console.anthropic.com/) (required for Claude AI)
- **Optional:** OpenAI or Gemini API keys for alternative LLM providers

### Step 1: Clone Repository
```bash
git clone https://github.com/LeylinFarlier1/CHATBOT_CLASES_IA.git
cd CHATBOT_CLASES_IA
```

### Step 2: Configure API Keys

You need to create **TWO separate `.env` files** in different directories:

#### 📁 File 1: `macro/.env` (For FRED API)

```bash
# Navigate from repository root
cd macro

# Create .env file with your FRED API key
```

**Content of `macro/.env`:**
```env
FRED_API_KEY=your_fred_api_key_here
```

> Get your free FRED API key at: https://fred.stlouisfed.org/docs/api/api_key.html

---

#### 📁 File 2: `mcp-client/.env` (For LLM APIs)

```bash
# Navigate from repository root
cd mcp-client

# Create .env file with your LLM API keys
```

**Content of `mcp-client/.env`:**
```env
# Required: At least one LLM API key
ANTHROPIC_API_KEY=your_anthropic_key_here

# Optional: Additional LLM providers
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here

# Optional: Default LLM configuration
DEFAULT_LLM_PROVIDER=claude
DEFAULT_MODEL=claude-3-7-sonnet-20250219

# Optional: GUI settings (v0.4.0+)
GUI_AUTO_OPEN=true
GUI_BACKEND=auto
```

> **Get API keys:**
> - Anthropic (Claude): https://console.anthropic.com/
> - OpenAI (GPT): https://platform.openai.com/api-keys
> - Google (Gemini): https://ai.google.dev/

**Final structure should look like:**
```
CHATBOT_CLASES_IA/
├── macro/
│   ├── .env              ← FRED_API_KEY here (read by server_mcp.py)
│   └── app/
│       └── server_mcp.py
└── mcp-client/
    ├── .env              ← ANTHROPIC_API_KEY here
    └── tui_app.py
```

### Step 3: Install Dependencies

**Install Server Dependencies:**
```bash
# From repository root (CHATBOT_CLASES_IA/)
cd macro/app
uv sync
```

**Install Client Dependencies:**
```bash
# From repository root (CHATBOT_CLASES_IA/)
cd mcp-client
uv sync
```

> **Note:** The TUI client automatically starts the MCP server when launched. You don't need to run the server separately!

**Verify installation:**
```bash
# Check both environments are ready
cd macro/app && uv run python --version
cd ../../mcp-client && uv run python --version
```

---

## Quick Start

### Option 1: TUI Interface (Recommended for v0.2.5+)

```bash
cd mcp-client
uv run python tui_app.py
```

**Features:**
- Full-screen interface with 3-panel layout
- Real-time dataset browser
- Conversation history panel
- Keyboard shortcuts (Q to quit, Ctrl+D toggle sidebar, etc.)
- Clean message display without boxes (v0.2.5)

### Option 2: CLI Interface (Classic)

```bash
cd mcp-client
uv run python client.py server_mcp.py:server
```

**Features:**
- Line-by-line interaction
- Autocompletion support
- Command history with Ctrl+R
- Rich formatting

### 2. Example Interactions

**Search for Economic Indicators:**
```
Consulta: Search for GDP series
```

**Plot Time Series:**
```
Consulta: Plot unemployment rate from 2020 to 2024
```

**Build Custom Dataset:**
```
Consulta: Build a dataset with UNRATE, CPIAUCSL (YoY), and GDP (QoQ)
```

**Compare Two Series:**
```
Consulta: Compare unemployment vs inflation on dual axis
```

**Analyze Stationarity:**
```
Consulta: Analyze differencing for GDP series
```

### 3. Use Slash Commands

```bash
/help              # Show all available commands
/tools             # List MCP tools
/resources         # Show available resources
/save my_analysis  # Save current conversation
/export md report  # Export conversation to Markdown
/search GDP        # Search conversation history
/stats             # Show usage statistics
/examples          # See example queries
```

---

## MCP Tools Reference

### Fetch Tools (Data Acquisition)

#### `search_fred_series_tool(search_text, limit)`
Search FRED series by keyword.
- **Args**: `search_text` (str), `limit` (int, default: 50)
- **Returns**: JSON with search results ordered by popularity
- **Example**: Search for "unemployment rate"

#### `fetch_series_metadata_tool(series_id)`
Get metadata for a FRED series.
- **Args**: `series_id` (str, e.g., "GDP", "UNRATE")
- **Returns**: JSON with title, units, frequency, seasonal adjustment
- **Example**: Get info for GDP series

#### `fetch_series_observations_tool(series_id, observation_start, observation_end)`
Fetch historical observations.
- **Args**: `series_id` (str), `observation_start` (str, optional), `observation_end` (str, optional)
- **Returns**: JSON with date-value pairs
- **Example**: Get unemployment data from 2020-01-01 to 2024-12-31

#### `fetch_fred_releases_tool()`
List all FRED releases.
- **Returns**: JSON with available data releases

#### `fetch_release_details_tool(release_id)`
Get details for a specific release.
- **Args**: `release_id` (str)
- **Returns**: JSON with release information

#### `fetch_category_details_tool(category_id)`
Get details for a FRED category.
- **Args**: `category_id` (str)
- **Returns**: JSON with category information

#### `fetch_fred_sources_tool()`
List all FRED data sources.
- **Returns**: JSON with data sources

### Build Tools (ETL Pipeline)

#### `build_fred_dataset_tool(series_list, transformations, observation_start, observation_end, merge_strategy)`
Build unified macroeconomic dataset with transformations.

**Args:**
- `series_list` (list): FRED series IDs (e.g., ['UNRATE', 'CPIAUCSL', 'GDP'])
- `transformations` (dict, optional): Transformation mappings
  - Available: 'none', 'YoY', 'QoQ', 'MoM', 'diff', 'pct_change', 'log', 'log_diff'
  - Example: `{'CPIAUCSL': 'YoY', 'GDP': 'QoQ'}`
- `observation_start` (str, optional): Start date 'YYYY-MM-DD'
- `observation_end` (str, optional): End date 'YYYY-MM-DD'
- `merge_strategy` (str, default: 'inner'): Merge strategy ('inner', 'outer', 'left', 'right')

**Returns:** Summary with file paths (CSV, Excel, metadata JSON)

**Example:**
```python
build_fred_dataset_tool(
    series_list=['UNRATE', 'CPIAUCSL', 'GDP'],
    transformations={'CPIAUCSL': 'YoY', 'GDP': 'QoQ'},
    observation_start='2000-01-01'
)
```

### Plot Tools (Visualization)

#### `plot_fred_series_tool(series_id, observation_start, observation_end)`
Create APA-style time series plot.
- **Args**: `series_id` (str), optional date range
- **Returns**: Path to saved plot, CSV, and Excel files
- **Example**: Plot GDP from 2015 to 2024

#### `plot_dual_axis_tool(series_id_left, series_id_right, observation_start, observation_end, left_color, right_color)`
Compare two series on dual-axis plot.
- **Args**: Two series IDs, optional dates and colors
- **Returns**: Path to saved plot and data files
- **Example**: Compare UNRATE (left) vs CPIAUCSL (right)

#### `analyze_differencing_tool(series_id, observation_start, observation_end)`
Analyze differencing with ADF stationarity tests.
- **Args**: `series_id` (str), optional date range
- **Returns**: Paths to plots and ADF test results
- **Example**: Test stationarity of GDP series

#### `plot_from_dataset_tool(column_left, column_right, dataset_path, left_color, right_color)`
Plot from pre-built dataset (no recalculation).
- **Args**: Column names, optional dataset path and colors
- **Returns**: Path to saved plot
- **Example**: Plot 'UNRATE' vs 'CPIAUCSL_YoY' from latest dataset

---

## MCP Resources

### `fred://datasets/recent`
Lists 10 most recently created FRED datasets with full metadata.

**Information Provided:**
- Dataset names and creation dates
- Date ranges (observation periods)
- Available columns (including transformation suffixes)
- Applied transformations
- Full file paths

**Purpose:** Solves MCP client's limited context issue by providing automatic visibility of available datasets.

**Example Output:**
```
📂 DATASETS RECIENTES (últimos 10)

1. FRED_dataset_UNRATE_CPIAUCSL
   📅 Creado: 2025-10-11 19:30:15
   📊 Período: 1948-01-01 a 2025-08-01
   🔹 Columnas: UNRATE, CPIAUCSL_YoY
   🔄 Transformaciones: CPIAUCSL → YoY
   📍 Path: C:/Users/.../dataset.csv
```

---

## Slash Commands

### Basic Commands
- `/help` or `/h` or `/?` - Show all available commands
- `/tools [tool_name]` or `/t` - List tools or show tool details
- `/resources [uri]` or `/r` - List resources or read specific resource
- `/clear` or `/cls` - Clear console screen
- `/status` or `/info` - Show client status
- `/examples` or `/ex` - Show example queries
- `/exit` or `/quit` or `/q` - Exit client

### Conversation Management
- `/history` or `/hist` - Show current conversation history
- `/new` or `/reset` - Start new conversation (clear history)

### Persistence Commands (Fase 3)
- `/save [name]` - Save conversation to JSON file
- `/load <name>` - Load conversation from JSON file
- `/export <format> [name]` - Export conversation (md or json)
- `/search <keyword>` - Search conversation history
- `/stats` - Show usage statistics

---

## Workflow Examples

### Example 1: Build and Visualize Custom Dataset
```bash
# Step 1: Build dataset with transformations
Consulta: Build a dataset with UNRATE, CPIAUCSL (YoY), and GDP (QoQ) from 2000 to 2024

# Step 2: Plot from dataset
Consulta: Plot UNRATE vs CPIAUCSL_YoY from the dataset

# Step 3: Save conversation
/save unemployment_inflation_analysis

# Step 4: Export report
/export md unemployment_report_2024
```

### Example 2: Stationarity Analysis
```bash
# Step 1: Analyze differencing
Consulta: Analyze differencing for GDP series from 1950 to 2024

# Step 2: Review ADF test results
# Claude will show:
# - Original series ADF test
# - First difference ADF test
# - Second difference ADF test
# - Plots for each

# Step 3: Export findings
/export md gdp_stationarity_analysis
```

### Example 3: Economic Research Workflow
```bash
# Step 1: Search for relevant series
Consulta: Search for inflation series

# Step 2: Get metadata
Consulta: Show me metadata for CPIAUCSL

# Step 3: Build comprehensive dataset
Consulta: Build dataset with CPIAUCSL, UNRATE, FEDFUNDS, and GDP with YoY transformations

# Step 4: Create visualizations
Consulta: Compare inflation vs unemployment
Consulta: Compare Fed Funds rate vs GDP growth

# Step 5: Save and export
/save macro_analysis_q4_2024
/export md final_report
```

---

## Advanced Features

### Conversation History Management

**Save conversations:**
```bash
/save my_analysis              # Save with custom name
/save                          # Auto-generate name with timestamp
```

**Load conversations:**
```bash
/load my_analysis             # Load by name
/load conversation_20241012   # Load by timestamp
```

**Search history:**
```bash
/search GDP                   # Find all conversations about GDP
/search inflation             # Find inflation-related conversations
```

**Export conversations:**
```bash
/export md report            # Export to Markdown
/export json backup          # Export to JSON
```

### Resource Cache System

The client caches MCP tools and resources with a 5-minute TTL to improve performance:
- Automatic caching of tool lists
- Transparent cache invalidation
- Configurable TTL (default: 300 seconds)

**Configuration:**
```python
# In client.py
self.cache = ResourceCache(ttl=600)  # 10 minutes
```

### Autocompletion System

The client features intelligent autocompletion for:
- **Commands**: `/help`, `/tools`, `/resources`, etc.
- **Economic Keywords**: `GDP`, `inflation`, `unemployment`, `CPI`, etc.
- **Series IDs**: `UNRATE`, `CPIAUCSL`, `FEDFUNDS`, etc.
- **Actions**: `plot`, `compare`, `analyze`, `download`, `show`

**Usage:**
- Press `Tab` to autocomplete
- Type `/` + `Tab` to see all commands
- Use arrow keys to navigate history
- Press `Ctrl+R` for reverse search

---

## Configuration

### Server Configuration

**Location:** `macro/app/server_mcp.py`

**API Keys:**
```python
# Required environment variable
FRED_API_KEY=your_fred_api_key
```

**Data Storage:**
```python
# Default data directory (can be changed)
base_dir = r"C:\Users\agust\Downloads\FRED_Data"
```

### Client Configuration

**Location:** `mcp-client/client.py`

**API Keys:**
```python
# Required environment variable
ANTHROPIC_API_KEY=your_anthropic_api_key
```

**History Settings:**
```python
# Maximum conversation items to store
self.history_manager = ConversationHistory(max_items=100)
```

**Cache Settings:**
```python
# Cache TTL in seconds
self.cache = ResourceCache(ttl=300)  # 5 minutes
```

**Claude Model:**
```python
# Current model
model="claude-3-5-haiku-20241022"
```

---

## File Structure & Data Organization

### Server Data Directory
```
C:/Users/agust/Downloads/FRED_Data/
├── FRED_dataset_UNRATE_CPIAUCSL_GDP/
│   ├── FRED_dataset_UNRATE_CPIAUCSL_GDP_2000-01-01_to_2024-12-31_built_20241012.csv
│   ├── FRED_dataset_UNRATE_CPIAUCSL_GDP_2000-01-01_to_2024-12-31_built_20241012.xlsx
│   ├── FRED_dataset_UNRATE_CPIAUCSL_GDP_metadata_20241012.json
│   └── plots/
│       └── UNRATE_vs_CPIAUCSL_YoY_plot_20241012.png
├── GDP/
│   ├── series/
│   │   ├── GDP_1950-01-01_to_2024-12-31_downloaded_20241012.csv
│   │   └── GDP_1950-01-01_to_2024-12-31_downloaded_20241012.xlsx
│   └── grafico/
│       └── GDP_1950-01-01_to_2024-12-31_plot_20241012.png
└── ...
```

### Client Data Directory
```
mcp-client/
├── conversations/
│   ├── my_analysis.json
│   ├── my_report.md
│   └── conversation_20241012_143022.json
└── .mcp_history                # Command history file
```

---

## Troubleshooting

### Common Issues

**1. API Key Errors**
```
Error: FRED_API_KEY environment variable is missing
```
**Solution:** Create `.env` file in `macro/app/` with your FRED API key

**2. Connection Errors**
```
Error: Durante la conexión al servidor MCP
```
**Solution:** Ensure server path is correct and dependencies are installed

**3. Import Errors**
```
ModuleNotFoundError: No module named 'prompt_toolkit'
```
**Solution:** Run `uv sync` in the mcp-client directory

**4. History Not Saving**
```
Error: History manager not initialized
```
**Solution:** Check that client initialized correctly with `/status` command

**5. Cache Issues**
```
Tools list not updating
```
**Solution:** Wait for TTL expiration (5 min) or restart client

### Debug Mode

Enable logging in server:
```python
# In server_mcp.py
logging.basicConfig(level=logging.DEBUG)
```

Enable logging in client:
```python
# In client.py
logging.basicConfig(level=logging.DEBUG)
```

---

## Performance Tips

1. **Use Resource Cache**: Let the 5-min cache reduce API calls
2. **Build Datasets Once**: Use `plot_from_dataset_tool` to avoid re-downloading
3. **Use `/resources`**: Check existing datasets before building new ones
4. **Batch Operations**: Build datasets with multiple series at once
5. **Save Frequently**: Use `/save` to preserve work
6. **Use Autocompletion**: Tab completion saves typing time

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Install development dependencies
uv sync --dev

# Run tests (if available)
pytest

# Format code
black .

# Lint code
ruff check .
```

---

## Technologies Used

### Core Technologies
- **Python 3.10+**: Main programming language
- **MCP (Model Context Protocol)**: Tool and resource protocol
- **FastMCP**: Rapid MCP server development
- **Anthropic Claude**: AI model for natural language processing

### Data & APIs
- **FRED API** (fredapi): Federal Reserve Economic Data access
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing

### Visualization
- **matplotlib**: Publication-quality charts
- **statsmodels**: Econometric analysis (ADF tests)

### UI/UX
- **Rich**: Terminal formatting and progress bars
- **prompt-toolkit**: Advanced input with autocompletion

### Storage & Export
- **openpyxl**: Excel file generation
- **json**: Metadata and conversation storage

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Federal Reserve Economic Data (FRED)**: For providing comprehensive economic data
- **Anthropic**: For the Claude AI model and MCP protocol
- **Contributors**: Thanks to all contributors who have helped improve this project

---

## Troubleshooting

### ❌ "FRED_API_KEY environment variable is missing"

**Problem:** MCP server can't access FRED API.

**Solution:** 
1. Verify `.env` file exists in `macro/.env` (NOT in `macro/app/`)
2. Ensure it contains: `FRED_API_KEY=your_actual_key`
3. Restart the TUI application

### ❌ "Connection failed" or "Server not responding"

**Problem:** TUI can't connect to MCP server.

**Solution:**
1. Check that `uv` is installed: `uv --version`
2. Verify server dependencies: `cd macro/app && uv sync`
3. Check server path in error message matches your installation

### ❌ "No LLM API key found"

**Problem:** No Anthropic/OpenAI/Gemini key configured.

**Solution:**
1. Verify `.env` file exists in `mcp-client/.env`
2. Ensure at least ONE of these keys is set:
   - `ANTHROPIC_API_KEY=sk-ant-...`
   - `OPENAI_API_KEY=sk-...`
   - `GEMINI_API_KEY=...`

### ❌ Plots not opening automatically (v0.4.0+)

**Problem:** Plot windows don't open, only file paths shown.

**Solution:**
1. Check if running in SSH/remote without X11 forwarding
2. Verify `GUI_AUTO_OPEN=true` in `mcp-client/.env`
3. Windows/macOS: Should work automatically
4. Linux: Ensure X11 server is running

### ❌ "Module not found" errors

**Problem:** Missing dependencies.

**Solution:**
```bash
# Reinstall dependencies
cd macro/app && uv sync
cd ../../mcp-client && uv sync
```

### 📝 Still having issues?

1. Check logs in terminal output
2. Verify all `.env` files are in correct locations
3. Ensure API keys are valid and have quota
4. Open an issue on GitHub with error details

---

## Contact & Support

For questions, issues, or feature requests:
- 🐛 **Report bugs:** Open an issue on GitHub
- 📖 **Documentation:** Check files in repository root
- 💬 **Discussions:** Use GitHub Discussions

---

## Roadmap

### Upcoming Features (v0.3.0)
- [ ] ASCII plot previews using plotext (TUI)
- [ ] Copy message to clipboard (TUI)
- [ ] Export conversation from UI (TUI)
- [ ] Theme selector (TUI)
- [ ] Command palette Ctrl+P (TUI)
- [ ] Autocompletion in TUI
- [ ] Database integration for local caching
- [ ] Additional transformation types
- [ ] Multi-series correlation analysis
- [ ] Automated report generation
- [ ] Web-based UI option
- [ ] Docker containerization
- [ ] API endpoint exposure

### Recent Changes (v0.2.5)
- ✅ Simplified TUI message layout (removed container boxes)
- ✅ Direct widget mounting for cleaner interface
- ✅ Improved visual hierarchy with indentation
- ✅ Better performance (fewer widgets per message)

### Future Enhancements
- [ ] Integration with other data sources (World Bank, IMF, etc.)
- [ ] Machine learning models for forecasting
- [ ] Real-time data streaming
- [ ] Collaborative analysis features
- [ ] Custom plugin system

---

**Version:** 0.2.5
**Last Updated:** October 2024
**Status:** Active Development
