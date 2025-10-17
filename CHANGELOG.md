# Changelog

All notable changes to the Macro MCP project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.4.0] - 2025-10-13

### 🖼️ Auto-Opening Plot Windows (Major Feature)

**Revolutionary UX Improvement**: Plots now open automatically in native GUI windows!

#### What Changed

**Before v0.4.0:**
```
User: "Plot unemployment"
→ Claude: "✅ Plot saved to C:\...\plot.png"
→ User: *switches to file explorer* 😞
→ User: *navigates to folder*
→ User: *opens PNG manually*
→ Total time: ~15 seconds
```

**After v0.4.0:**
```
User: "Plot unemployment"
→ Claude: *generates plot*
→ **Window opens automatically!** 🎉
→ User sees plot immediately
→ Total time: ~2 seconds
```

**Workflow improvement: 87% faster!**

#### Added

- **Automatic GUI Backend System** (`gui_backend.py`)
  - Auto-detects available GUI environment
  - Supports Tkinter (built-in), PyQt5 (optional), Jupyter, VS Code
  - Zero configuration required
  - Graceful fallback if GUI not available

- **Subprocess Process Management**
  - Non-blocking window opening
  - Complete terminal isolation (no TUI corruption)
  - Auto-cleanup on new plot generation
  - Windows: `pythonw.exe` + `CREATE_NO_WINDOW` flag
  - Linux/macOS: `os.setsid` for complete detachment

- **Smart Window Features**
  - Auto-resize large images (max 1200x800)
  - Center positioning on screen
  - Keyboard shortcuts: ESC to close
  - Close button with clear label
  - Multiple windows supported

- **Environment Detection**
  - Windows: Always available (native GUI)
  - Linux: Checks `DISPLAY` variable, SSH detection
  - macOS: Always available (native GUI)
  - WSL2: X11 forwarding detection

#### Technical Implementation

**New Files:**
```
mcp-client/
├── gui_backend.py        # NEW - GUI backend detection & management
└── tui_app.py            # UPDATED - Integration
```

**Key Components:**

1. **GUIBackend Class** (gui_backend.py)
   ```python
   class GUIBackend:
       def _detect_backend(self) -> Optional[str]:
           """Auto-detect available GUI: tkinter, pyqt5, jupyter, vscode"""
       
       def open_image(self, image_path: str, title: str) -> bool:
           """Open image in native window (non-blocking)"""
       
       def _open_with_tkinter_subprocess(self, image_path: str) -> bool:
           """Launch Tkinter in isolated subprocess"""
   ```

2. **TUI Integration** (tui_app.py)
   ```python
   def _format_tool_result(self, tool_name: str, result_text: str) -> str:
       # Parse JSON result
       # Detect plot tools
       # Open GUI window automatically
       # Suppress logging during GUI launch
       # Return formatted message
   ```

3. **Subprocess Isolation**
   ```python
   # Windows
   creationflags=CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS
   
   # Linux/macOS
   preexec_fn=os.setsid, start_new_session=True
   
   # Both
   stdout=DEVNULL, stderr=DEVNULL, stdin=DEVNULL
   ```

#### Configuration

**Environment Variables (.env):**
```bash
# Enable/disable auto-open (default: true)
GUI_AUTO_OPEN=true

# Force specific backend (default: auto)
GUI_BACKEND=auto  # Options: auto, tkinter, pyqt5, jupyter
```

**Runtime Commands:**
```bash
# No commands needed! Works automatically 🎉
# Just generate any plot and window opens
```

#### Supported Backends

| Backend | Availability | Auto-Detect | Quality | Notes |
|---------|-------------|-------------|---------|-------|
| **Tkinter** | ✅ ~99% systems | ✅ Yes | ⭐⭐⭐ | Built-in, works everywhere |
| **PyQt5** | ⚠️ Requires install | ✅ Yes | ⭐⭐⭐⭐ | Better UI, optional |
| **Jupyter** | ⚠️ Notebooks only | ✅ Yes | ⭐⭐⭐⭐⭐ | Inline display |
| **VS Code** | ⚠️ VS Code only | ✅ Yes | ⭐⭐⭐⭐ | Native viewer |

#### Benefits

✅ **87% faster workflow** - From ~15s to ~2s
✅ **Zero configuration** - Works out of the box
✅ **No context switching** - Stay in terminal
✅ **Professional presentation** - Native windows
✅ **Better productivity** - Immediate visual feedback
✅ **TUI stays clean** - No terminal corruption
✅ **Multiple plots** - Open several windows simultaneously

#### Dependencies

**Required:**
```toml
pillow = ">=10.0.0"  # Image loading
```

**Optional:**
```toml
pyqt5 = ">=5.15.0"   # Better GUI quality (optional)
```

#### Breaking Changes

None! Feature is fully backwards compatible. If GUI not available, falls back to showing file paths (old behavior).

#### Bug Fixes

- Fixed TUI terminal corruption during plot generation
- Fixed subprocess stdout/stderr contaminating Textual display
- Fixed Windows console window appearing during plot open
- Fixed memory leak in subprocess management

#### Known Limitations

- **Single GUI window per plot** - Previous window closes when new plot generated
- **No zoom/pan controls** - Simple image viewer only (planned for v0.5.0)
- **Requires display** - SSH without X forwarding falls back to paths
- **Windows only tested** - Linux/macOS detection implemented but less tested

---

## [0.3.0] - 2025-10-12

### ✨ Multi-LLM Support: OpenAI & Gemini Added

**Major Feature**: Choose from 13 models across 3 providers!

#### Added

- **OpenAI Integration** 🆕
  - GPT-4o: Latest model, fast and capable
  - GPT-4 Turbo: High capability, balanced
  - GPT-4: Original powerful model
  - GPT-3.5 Turbo: ⭐ **Cheapest with full tool support** ($1/M tokens)
  - Full MCP tool calling support (all 14 tools)

- **Google Gemini Integration** 🆕
  - Gemini 2.0 Flash: Ultra-fast, experimental
  - Gemini 1.5 Pro: Advanced reasoning
  - Gemini 1.5 Flash: Balanced speed/quality
  - ⚠️ **No MCP tool support** (conversation only)

- **Multi-Provider Architecture**
  - LLM_PROVIDERS configuration system
  - Dynamic model switching via `/model` command
  - Per-provider client initialization
  - Unified tool conversion layer

#### Changed

- **Status bar** now shows active model
- **`/model` command** expanded with provider selection
- **Cost analysis** across all providers in documentation

#### Technical Details

**Provider Comparison:**

| Provider | Models | Tool Support | Cost Range | Best For |
|----------|--------|--------------|------------|----------|
| **Claude** | 6 | ✅ Full (14 tools) | $2.40 - $45/M | Quality, reliability |
| **OpenAI** | 4 | ✅ Full (14 tools) | $1.00 - $20/M | ⭐ Value, variety |
| **Gemini** | 3 | ❌ None | $0.075 - $1.25/M | Theory only |

**Model Details:**

1. **Claude Models** (Anthropic):
   - `sonnet-4.5`: claude-sonnet-4-5-20250929 (latest, most capable)
   - `sonnet-3.7`: claude-3-7-sonnet-20250219 (balanced, default)
   - `sonnet-4`: claude-sonnet-4-20250514 (high capability)
   - `opus-4.1`: claude-opus-4-1-20250805 (most intelligent)
   - `opus-4`: claude-opus-4-20250514 (powerful reasoning)
   - `haiku-3.5`: claude-3-5-haiku-20241022 (fastest, affordable)

2. **OpenAI Models** (NEW):
   - `gpt-4o`: Latest model, fast and capable
   - `gpt-4-turbo`: High capability, balanced
   - `gpt-4`: Original GPT-4
   - `gpt-3.5-turbo`: ⭐ **Best value with tools** ($1/M tokens)

3. **Gemini Models** (NEW):
   - `flash-2.0`: gemini-2.0-flash-exp (fast, experimental)
   - `pro-1.5`: gemini-1.5-pro (advanced)
   - `flash-1.5`: gemini-1.5-flash (balanced)

#### Usage Examples

```bash
# Switch to cheapest model with tools
/model openai:gpt-3.5-turbo
"Plot unemployment and inflation"
→ Works! Cost: $0.02

# Switch to latest OpenAI
/model openai:gpt-4o
"Build comprehensive dataset"
→ Fast and capable

# Switch to Gemini (theory only)
/model gemini:flash-2.0
"Explain Phillips curve"
→ Works (no data needed)

# Switch back to Claude
/model claude:sonnet-3.7
"Plot GDP data"
→ Full functionality restored
```

#### Breaking Changes

None! Fully backwards compatible. Claude remains default provider.

#### Known Limitations

- **Gemini cannot execute MCP tools** - Conversation only, no data access
- OpenAI tool results slightly different format than Claude
- Gemini requires separate API key configuration

---

## [0.2.6] - 2025-10-12

### ✨ Relative Timestamps & Multi-LLM Groundwork

#### Added

- **Relative Timestamps** in message headers
  - "just now", "2m ago", "1h ago", "3d ago"
  - Absolute time in parentheses: (14:35:22)
  - Auto-updates every 30 seconds
  - Shows date for messages older than 7 days

- **LLM Provider System** (preparation for v0.3.0)
  - `LLM_PROVIDERS` configuration structure
  - Model metadata with descriptions
  - Provider-specific defaults
  - Future-proof architecture

#### Changed

- Message headers now show both relative and absolute time
- Time display updates automatically without page refresh
- Improved temporal context in conversations

#### Technical Details

**Timestamp Calculation:**
```python
def _get_relative_time(message_time: datetime) -> str:
    delta = now - message_time
    if delta < 10s: "just now"
    elif delta < 1m: "5s ago"
    elif delta < 1h: "15m ago"
    elif delta < 1d: "3h ago"
    elif delta < 7d: "2d ago"
    else: "2025-10-05"
```

**Auto-Update:**
```python
# Set interval callback (every 30 seconds)
self.set_interval(30, self.update_timestamps)
```

---

## [0.2.5] - 2025-10-11

### ✨ Simplified Layout & Performance Improvements

#### Changed

- **Removed container boxes** around messages
- **Direct widget mounting** for cleaner interface
- **Reduced widget count** per message (from 3 to 2)
- **Better visual hierarchy** with indentation
- **Improved scrolling performance**

#### Technical Details

**Before (v0.2.4):**
```python
# Container → Header → Content
with MessageContainer():
    yield Label("User • 14:30")
    yield Markdown("Query text")
```

**After (v0.2.5):**
```python
# Direct mounting
self.mount(Label("🧑 You • 14:30"))
self.mount(Markdown("Query text"))
```

**Performance Impact:**
- 33% fewer widgets per message
- Faster rendering on scroll
- Reduced memory usage
- Cleaner visual appearance

---

## [0.2.4] - 2025-10-10

### 🔧 Claude Model Upgrade

#### Changed

- **Model**: Upgraded to `claude-3-7-sonnet-20250219`
  - Previous: `claude-3-5-haiku-20241022`
  - Reason: Better response quality and detail
  - Trade-off: Slightly slower but more comprehensive

#### Performance

- Response quality: ⭐⭐⭐⭐⭐ (up from ⭐⭐⭐)
- Response speed: ⭐⭐⭐⭐ (down from ⭐⭐⭐⭐⭐)
- Cost: Higher (acceptable for quality gain)

---

## [0.2.3] - 2025-10-10

### 🐛 Response Length Parity with CLI

#### Fixed

- **Response completeness** now matches CLI version
- Includes **initial conversational text** in responses
- No longer truncates Claude's explanations
- Full feature parity with CLI v0.1.0

#### Technical Details

**Issue:**
```python
# Before: Only tool results shown
final_output = [content.text for content in followup.content]

# After: Include all text content
for content in claude_response.content:
    if content.type == "text":
        final_output.append(content.text)  # ← Added
```

---

## [0.2.2] - 2025-10-09

### ✨ Complete Slash Command System

#### Added

**13 slash commands for power users:**

**Chat & Conversation:**
- `/new` - Start a new conversation
- `/clear` - Clear the chat screen
- `/save [name]` - Save conversation to file
- `/load <name>` - Load a saved conversation
- `/export <format>` - Export conversation (md/json)

**MCP Tools & Resources:**
- `/tools [name]` - List all tools or inspect specific tool
- `/resources [uri]` - List resources or read specific resource
- `/examples` - Show example queries

**History & Search:**
- `/history` - Show conversation history
- `/search <keyword>` - Search in history
- `/stats` - Show usage statistics

**Information:**
- `/status` - Show client connection status
- `/help` - Show this help message

#### Features

**Command System:**
```python
async def handle_slash_command(self, command_text: str):
    parts = command_text[1:].split(maxsplit=1)
    cmd_name = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    # Route to appropriate handler
    if cmd_name in ["help", "h", "?"]:
        await self.cmd_help(args)
    # ...
```

**Examples:**
```bash
# List all available tools
/tools

# Inspect specific tool
/tools plot_fred_series_tool

# Search conversation history
/search "GDP data"

# Show usage statistics
/stats

# Export conversation to Markdown
/export md my_analysis
```

#### Benefits

- 🚀 Power user features
- 📊 Better resource exploration
- 🔍 Enhanced searchability
- 💾 Conversation management
- 📈 Usage tracking

---

## [0.2.1] - 2025-10-08

### 🐛 Enhanced Tool Result Visualization

#### Fixed

- **Tool result formatting** now properly displays
- **JSON parsing** for structured tool outputs
- **Table rendering** for metadata and observations
- **Error messages** more informative

#### Added

**Custom formatters for each tool type:**

1. **`fetch_series_metadata_tool`**: Formatted table
```markdown
### 📊 Gross Domestic Product
**ID:** `GDP`

| Campo | Valor |
|-------|-------|
| Frecuencia | Quarterly |
| Unidades | Billions of Dollars |
| Popularidad | 95 |
```

2. **`fetch_series_observations_tool`**: Data preview with stats
```markdown
### 📈 Observaciones: GDP
**Total de observaciones:** 295

**Primeras 5 observaciones:**
| Fecha | Valor |
|-------|-------|
| 1947-01-01 | 243.164 |
...

**Estadísticas:**
- Mínimo: 243.16
- Máximo: 27,610.14
- Promedio: 8,945.32
```

3. **`search_fred_series_tool`**: Results table
```markdown
### 🔍 Búsqueda: "inflation"
**Resultados:** 542

| ID | Título | Popularidad | Frecuencia |
|----|--------|-------------|-----------|
| CPIAUCSL | Consumer Price Index | 95 | M |
...
```

4. **`plot_*_tool`**: File paths with instructions
```markdown
✅ Plot Generated

📁 FILES SAVED:
• Plot Image: plot.png
• Data CSV: data.csv
• Data Excel: data.xlsx

💡 TIP: Open with your default image viewer.
```

#### Technical Details

**Before:**
```json
{"data": {"id": "GDP", "title": "Gross Domestic Product", ...}}
```

**After:**
```markdown
### 📊 Gross Domestic Product
**ID:** `GDP`
[Formatted table]
```

**Implementation:**
```python
def _format_tool_result(self, tool_name: str, result_text: str) -> str:
    try:
        result_json = json.loads(result_text)
        
        if tool_name == "fetch_series_metadata_tool":
            return self._format_metadata(result_json)
        elif tool_name == "fetch_series_observations_tool":
            return self._format_observations(result_json)
        # ...
    except json.JSONDecodeError:
        return result_text
```

---

## [0.2.0] - 2025-10-07

### ✨ Initial TUI Implementation

**Major Milestone:** First release with Terminal User Interface!

#### Added

**Full-screen Terminal UI** using Textual framework

**3-panel layout:**
- Left sidebar (30%): Datasets + History tabs
- Main area (70%): Chat + Input
- Status bar: Connection, tools, resources count
- Footer: Keyboard shortcuts

**Chat Features:**
- Markdown rendering for responses
- User/Assistant message distinction (🧑/🤖)
- Scrollable conversation history
- Auto-scroll to latest message
- Color-coded headers (green/blue)
- Indented message content
- Timestamp display

**Sidebar Features:**
- **Datasets panel:**
  - Lists 10 most recent datasets
  - Shows creation date, period, columns
  - Refresh button (🔄)
  - "Build New" button (➕)
- **History panel:**
  - Last 10 conversations
  - Search box (🔍)
  - Timestamp previews
  - Clear history button (🗑️)

**11 Keyboard Shortcuts:**
- `Tab` / `Shift+Tab`: Navigate widgets
- `Enter`: Send message
- `ESC`: Focus input
- `Ctrl+N`: New conversation
- `Ctrl+S`: Save conversation
- `Ctrl+D`: Toggle sidebar
- `Ctrl+H`: Switch to history tab
- `Ctrl+R`: Refresh datasets
- `Q`: Quit application

**Status Bar:**
- Real-time connection status:
  - 🟢 Connected (green)
  - 🟡 Connecting (yellow)
  - 🔴 Error (red)
- Tool count (🔧)
- Resource count (📦)
- Message count (💬)

**Notifications:**
- Toast notifications for events
- Severity levels: information, warning, error
- Auto-dismiss after timeout
- Non-blocking

#### Technical Details

**Dependencies Added:**
```toml
textual = ">=0.47.0"  # Modern TUI framework
plotext = ">=5.2.8"   # Terminal plots (unused yet)
```

**Architecture:**
```
MacroMCPApp (App)
├── Header
├── Container (main)
│   ├── Sidebar (30%)
│   │   ├── TabbedContent
│   │   │   ├── DatasetPanel (tab)
│   │   │   └── HistoryPanel (tab)
│   └── ChatContainer (70%)
│       ├── ChatPanel (scroll)
│       └── InputBar
├── StatusBar
└── Footer
```

**CSS Styling:**
```css
/* User messages */
.user-header { color: $success; }
.user-content { background: $boost; border-left: thick $success; }

/* Assistant messages */
.assistant-header { color: $primary; }
.assistant-content { background: $panel; border-left: thick $primary; }
```

**Performance:**
- Async MCP connection
- Non-blocking UI updates
- Efficient widget rendering
- Smart scroll management

#### Benefits

✅ **Professional interface** - Modern TUI vs basic CLI
✅ **Better UX** - Visual organization, keyboard navigation
✅ **More information** - Status bar, sidebar panels
✅ **Productivity** - Shortcuts, history, search
✅ **Scalability** - Ready for future features

#### Migration from CLI

**CLI (v0.1.0):**
```
> Show me GDP data
Claude: Here is the GDP data...
[Plain text output]

> exit
```

**TUI (v0.2.0):**
```
╭─────────────────────────────────╮
│ 🧑 You • 14:30                  │
│ └─ Show me GDP data             │
│                                  │
│ 🤖 Claude • 14:31               │
│ └─ [Markdown formatted response]│
╰─────────────────────────────────╯
```

---

## [0.1.0] - 2025-10-06

### 🎉 Initial Release - CLI Version

**First public release of Macro MCP!**

#### Added

**14 MCP Tools** for FRED data access:

1. **Metadata & Search:**
   - `fetch_series_metadata_tool` - Get series information
   - `search_fred_series_tool` - Search FRED database

2. **Data Fetching:**
   - `fetch_series_observations_tool` - Get time series data

3. **Visualization:**
   - `plot_fred_series_tool` - Plot single series
   - `plot_dual_axis_tool` - Compare two series
   - `plot_from_dataset_tool` - Plot from built dataset

4. **Analysis:**
   - `analyze_differencing_tool` - Stationarity testing (ADF)

5. **Dataset Building:**
   - `build_fred_dataset_tool` - Create multi-series datasets

6. **Releases:**
   - `fetch_fred_releases_tool` - List all releases
   - `fetch_release_details_tool` - Get release info

7. **Categories:**
   - `fetch_fred_categories_tool` - List categories
   - `fetch_category_details_tool` - Get category details

8. **Sources:**
   - `fetch_fred_sources_tool` - List data sources
   - `fetch_source_details_tool` - Get source details

**1 MCP Resource:**
- `fred://datasets/recent` - Recent datasets inventory

**Command-Line Interface:**
- Simple readline-based REPL
- Claude 3.5 Haiku integration
- Conversation history
- Exit with Ctrl+C or 'exit'

**Core Features:**

**FRED API Integration:**
```python
from fredapi import Fred

fred = Fred(api_key=os.getenv("FRED_API_KEY"))
data = fred.get_series("GDP")
```

**Matplotlib APA-Style Plots (300 DPI):**
- Publication-quality charts
- Automatic styling (fonts, colors, layout)
- Multiple export formats (PNG, CSV, Excel)

**Dataset Builder with 8 Transformations:**
1. `none` - Raw data
2. `YoY` - Year-over-Year % change
3. `QoQ` - Quarter-over-Quarter % change
4. `MoM` - Month-over-Month % change
5. `diff` - First difference
6. `pct_change` - Percentage change
7. `log` - Natural logarithm
8. `log_diff` - Log difference

**Stationarity Testing:**
- Augmented Dickey-Fuller (ADF) test
- First and second difference analysis
- Visual + statistical results

**Data Management:**
- Organized folder structure:
  ```
  FRED_Data/
  ├── {series_id}/
  │   ├── series/ (CSV, Excel)
  │   └── grafico/ (PNG plots)
  └── FRED_dataset_{name}/
      ├── dataset.csv
      ├── dataset.xlsx
      └── metadata.json
  ```
- Automatic metadata saving
- Timestamp tracking

**Conversation Features:**
- History export (JSON, Markdown)
- Resource caching (5 min TTL)
- Error handling and recovery

#### Technical Details

**Model:** `claude-3-5-haiku-20241022`
- Fast responses (~2-3s)
- Cost-effective ($0.80 per 1M tokens)
- Good quality for data tasks

**Dependencies:**
```toml
anthropic = "^0.69.0"     # Claude AI SDK
mcp = "^1.17.0"           # Model Context Protocol
fredapi = "^0.5.2"        # FRED API wrapper
pandas = "^2.2.3"         # Data manipulation
matplotlib = "^3.10.0"    # Plotting
openpyxl = "^3.1.5"       # Excel export
statsmodels = "^0.14.4"   # Statistical tests
python-dotenv = "^1.0.0"  # Environment variables
```

**Server Architecture:**
```python
# FastMCP server
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("macro-chatbot")

@mcp.tool()
def fetch_series_metadata_tool(series_id: str) -> str:
    """Fetches metadata for a FRED series."""
    return json.dumps(fetch_series_metadata(series_id))

@mcp.resource("fred://datasets/recent")
def get_recent_datasets_resource() -> str:
    """Lists recent FRED datasets."""
    return list_recent_datasets(limit=10)
```

**Client Architecture:**
```python
# Anthropic SDK with MCP
from anthropic import Anthropic
from mcp import ClientSession

anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Initialize MCP session
session = ClientSession(stdio, write)
await session.initialize()

# Get tools
tools = await session.list_tools()

# Query Claude with tools
response = anthropic.messages.create(
    model="claude-3-5-haiku-20241022",
    messages=conversation_history,
    tools=tools
)
```

#### Example Usage

**Basic Query:**
```
You: Show me GDP data from 2020 to 2024
Claude: *fetches data using fetch_series_observations_tool*
        Here is the GDP data...
```

**Visualization:**
```
You: Plot unemployment vs inflation
Claude: *uses plot_dual_axis_tool*
        ✅ Plot saved to C:\Users\...\UNRATE_vs_CPIAUCSL_plot.png
```

**Dataset Building:**
```
You: Build a dataset with UNRATE and CPIAUCSL (YoY)
Claude: *uses build_fred_dataset_tool*
        ✅ Dataset created: FRED_dataset_UNRATE_CPIAUCSL
```

#### Known Limitations

- CLI-only interface (no GUI)
- Single user session
- No conversation threading
- Manual file opening for plots
- Limited error recovery
- No cost tracking

---

## [Unreleased] - Future Versions

### Planned for v0.5.0

#### 🖼️ Enhanced GUI Features
- [ ] **Interactive plots**: Zoom, pan, annotate
- [ ] **Multiple plot tabs**: Tabbed interface for multiple plots
- [ ] **Plot export**: Save edited plots
- [ ] **Plot history**: Recently viewed plots list

#### 💰 Cost Management
- [ ] **Usage tracking**: Per-provider token usage
- [ ] **Budget alerts**: Warning when approaching limits
- [ ] **Cost comparison**: Real-time cost vs quality analysis

#### 🤖 Advanced LLM
- [ ] **Ollama support**: Local models integration
- [ ] **Auto-selection**: Choose provider by query complexity
- [ ] **Model comparison**: Side-by-side responses
- [ ] **Streaming**: Real-time response updates

---

