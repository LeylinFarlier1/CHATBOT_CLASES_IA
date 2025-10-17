# Macro MCP - TUI Guide

> Modern Terminal User Interface for Economic Analysis

---

## Quick Start

### 1. Install Dependencies

```bash
cd mcp-client
uv sync
```

This will install the new dependencies:
- `textual>=0.47.0` - Modern TUI framework
- `plotext>=5.2.8` - Terminal-based plotting

### 2. Run the TUI

```bash
uv run python tui_app.py
```

Or use the launcher:

```bash
uv run python run_tui.py
```

---

## Interface Overview

```
╭─────────────────────────────────────────────────────────────────────────────╮
│ Macro MCP - Economic Analysis System                                  v0.2.5 │
├─────────────────┬───────────────────────────────────────────────────────────┤
│  📊 Datasets    │  💬 Chat with Claude                                      │
│  📚 History     │                                                            │
│  (Tabs)         │  [Chat messages appear here]                              │
│                 │                                                            │
│  [Dataset List] │  [Claude's responses with markdown formatting]            │
│  [Buttons]      │                                                            │
│                 │                                                            │
│                 │  ─────────────────────────────────────────────────────── │
│                 │  > Type your question here...                             │
├─────────────────┴───────────────────────────────────────────────────────────┤
│ 🟢 Connected | 🔧 15 tools | 📦 1 resources | 💬 5 messages                 │
│ q:Quit | ctrl+d:Toggle | ctrl+n:New | ctrl+s:Save | ESC:Focus               │
╰─────────────────────────────────────────────────────────────────────────────╯
```

---

## Layout

### Left Sidebar (30% width)
- **Datasets Tab**: Lists recent FRED datasets with metadata
- **History Tab**: Shows conversation history with search

### Main Area (70% width)
- **Chat Panel**: Scrollable conversation with Claude
- **Input Bar**: Type your queries here

### Status Bar
- Connection status (🟢/🟡/🔴)
- Tool count (🔧)
- Resource count (📦)
- Message count (💬)

### Footer
- Keyboard shortcuts

---

## Keyboard Shortcuts

### Navigation
- `Tab` - Navigate between widgets
- `Shift+Tab` - Navigate backwards
- `↑↓` - Scroll chat/lists
- `ESC` - Focus input field

### Actions
- `Enter` - Send message
- `Ctrl+N` - New conversation
- `Ctrl+S` - Save conversation
- `Ctrl+D` - Toggle datasets sidebar
- `Ctrl+H` - Switch to history tab
- `Ctrl+R` - Refresh datasets
- `Q` - Quit application

### Chat Controls
- `Ctrl+C` - Copy last message (planned)
- `PageUp/PageDown` - Scroll chat faster

---

## Features

### 1. Chat Interface

**Markdown Support:**
- **Bold**, *italic*, `code`
- Headers (# ## ###)
- Lists (ordered and unordered)
- Code blocks with syntax highlighting
- Links

**Message Types:**
- 🧑 User messages (green header, boost background)
- 🤖 Assistant messages (blue header, panel background)

**Timestamps:**
- **Relative time**: "2m ago", "1h ago", "just now"
- **Absolute time**: (14:30:15) in parentheses
- **Auto-update**: Refreshes every 30 seconds
- **Long-term**: Shows date for messages older than 7 days

**Example Message Display:**
```
🧑 You • just now (14:35:22)
└─ Show me GDP data from 2020 to 2024

🤖 Claude • 5s ago (14:35:27)
└─ I'll fetch the GDP data for you...
```

**Timestamp Benefits:**
- Quick temporal context at a glance
- Track conversation pacing
- Identify stale vs fresh information
- Better UX in long sessions

**Example Query:**
```
Show me GDP data from 2020 to 2024
```

### 2. Datasets Panel

**Features:**
- Lists 10 most recent datasets
- Shows creation date, date range, columns
- Refresh button to update list
- "Build New" button with instructions

**Display Format:**
```
📊 Recent Datasets
─────────────────

1. FRED_dataset_UNRATE_CPIAUCSL
   📅 Created: 2025-10-11 19:30:15
   📊 Period: 1948-01-01 a 2025-08-01
   🔹 Columns: UNRATE, CPIAUCSL_YoY
```

### 3. History Panel

**Features:**
- Search box (🔍) for filtering
- Last 10 conversations displayed
- Timestamps and query previews
- Clear history button

**Usage:**
1. Switch to History tab (Ctrl+H)
2. Type in search box to filter
3. Click "Clear History" to reset

### 4. Status Bar

**Information Displayed:**
- **Connection Status**:
  - 🟢 Connected - MCP server online
  - 🟡 Connecting - Establishing connection
  - 🔴 Error - Connection failed
- **Tools Count**: Number of MCP tools available (🔧)
- **Resources Count**: Number of MCP resources available (📦)
- **Message Count**: Messages in current conversation (💬)

**Example Display:**
```
🟢 Connected | 🔧 14 tools | 📦 1 resources | 💬 12 messages
```

### 5. Notifications

**Toast Notifications appear for:**
- Connection events
- Save/load operations
- Errors and warnings
- Resource updates

**Severity Levels:**
- `information` - Blue
- `warning` - Yellow
- `error` - Red

---

## Workflow Examples

### Example 1: Basic Query

```
1. Start application: uv run python tui_app.py
2. Wait for "🟢 Connected" in status bar
3. Type query: "Plot unemployment rate from 2020 to 2024"
4. Press Enter
5. Claude processes and shows results
6. Files saved notification appears
```

### Example 2: Build Dataset

```
1. Click "➕ Build New" in Datasets panel
2. Read the instructions Claude provides
3. Type: "Build dataset with UNRATE and CPIAUCSL (YoY)"
4. Press Enter
5. Dataset is created
6. Click "🔄 Refresh" to see new dataset in list
```

### Example 3: Save Conversation

```
1. After having a conversation
2. Press Ctrl+S
3. Notification shows save path
4. File saved in conversations/ directory
```

### Example 4: Search History

```
1. Press Ctrl+H (switch to History tab)
2. Type keyword in search box (e.g., "GDP")
3. History filters to matching conversations
4. Clear search to see all history
```

---

## Customization

### Themes

Textual supports multiple themes. Edit `tui_app.py`:

```python
class MacroMCPApp(App):
    # Change theme
    def on_mount(self):
        self.theme = "nord"  # Options: nord, gruvbox, dracula, etc.
```

Available themes:
- `textual-dark` (default)
- `textual-light`
- `nord`
- `gruvbox`
- `dracula`
- `monokai`

### CSS Styling

Modify the `CSS` string in `MacroMCPApp` class to customize:
- Colors
- Spacing
- Borders
- Fonts
- Animations

**Example - Change user message color:**
```css
.user-message {
    background: $boost;
    border-left: thick $success;  /* Change to $warning, $error, etc. */
}
```

### Sidebar Width

```css
#sidebar {
    width: 30;  /* Change to 25, 35, 40, etc. */
}
```

---

## Troubleshooting

### App Won't Start

**Error: `ModuleNotFoundError: No module named 'textual'`**

Solution:
```bash
cd mcp-client
uv sync
```

### Connection Failed

**Status shows: 🔴 Error**

Check:
1. MCP server path in `tui_app.py` line 283
2. FRED_API_KEY in `macro/app/.env`
3. Server dependencies installed: `cd macro/app && uv sync`

### Input Not Working

- Press `ESC` to focus input
- Check if cursor is in input field
- Try clicking on input area

### Sidebar Not Visible

- Press `Ctrl+D` to toggle
- Check window size (minimum 80x24 recommended)

### Slow Performance

- Reduce `max_items` in ConversationHistory (line 165)
- Clear history frequently
- Reduce cache TTL (line 166)

### No Datasets Showing

1. Click "🔄 Refresh" button
2. Build a dataset first
3. Check `C:/Users/agust/Downloads/FRED_Data/` directory

---

## Advanced Usage

### Custom MCP Server Path

Edit `tui_app.py` line 283-291:

```python
server_params = StdioServerParameters(
    command="uv",
    args=[
        "--directory",
        "/your/custom/path/to/macro/app",  # Change this
        "run",
        "python",
        "server_mcp.py",
    ],
    env=None,
)
```

### Change Claude Model

Edit `tui_app.py` line 313:

```python
claude_response = self.anthropic.messages.create(
    model="claude-3-5-sonnet-20241022",  # Change model here
    max_tokens=4096,
    messages=self.conversation_history.copy(),
    tools=available_tools,
)
```

Available models:
- `claude-3-5-haiku-20241022` (fast, default)
- `claude-3-5-sonnet-20241022` (balanced)
- `claude-3-opus-20240229` (most capable)

### Increase Message History

Edit `tui_app.py` line 165:

```python
self.history_manager = ConversationHistory(max_items=200)  # Default: 100
```

### Change Cache TTL

Edit `tui_app.py` line 166:

```python
self.cache = ResourceCache(ttl=600)  # 10 minutes instead of 5
```

---

## Comparison: CLI vs TUI

| Feature | CLI (v0.1.0) | TUI (v0.3.0) |
|---------|-------------|-------------|
| **Interface** | Line-by-line | Full-screen panels |
| **Navigation** | Scroll only | Mouse + keyboard |
| **LLM Providers** | Claude only | Claude + OpenAI + Gemini |
| **Tool Support** | ✅ All 14 tools | ✅ All 14 tools (Claude + OpenAI) |
| **Models Available** | 1 | 13 (10 with tools) |
| **Cost Options** | Single pricing | Multiple (cheap to expensive) |

---

## Known Issues & Limitations

### Current Limitations

1. **No Plot Preview Inline**: Plots open in external viewer (planned for next version)
2. **Single User**: No multi-user support (by design for TUI)
3. **No Copy/Paste**: Standard terminal copy/paste only (Ctrl+Shift+C/V)
4. **No Syntax Highlighting in Code Blocks**: Coming in future update
5. **Resource Count Static**: Updates only on connection/refresh (not real-time)
6. **❌ Gemini Cannot Use MCP Tools**: Critical limitation - see below

### ❌ Gemini Tool Calling Limitation

**IMPORTANT:** Gemini **CANNOT** execute MCP tools.

**What This Means:**
```
✅ Works with Claude:
- Fetching FRED data
- Creating plots
- Building datasets
- Searching series
- All 14 MCP tools available

❌ Does NOT work with Gemini:
- Cannot fetch any data
- Cannot create any plots
- Cannot build any datasets
- Cannot use ANY of the 14 tools
```

**Why?**
- Gemini API uses different function calling format
- Incompatible with MCP tool protocol
- Would require complete rewrite

**What CAN Gemini Do?**
- Explain economic concepts
- Answer theory questions
- Interpret results (if you describe them)

**Recommendation:**
```bash
# ✅ Use Claude for everything
/model claude:haiku-3.5

# ❌ Don't switch to Gemini unless you only need theory
/model gemini:flash-2.0  # Only for non-data queries
```

**Example of Gemini Failure:**
```
You: /model gemini:flash-2.0
You: Plot unemployment rate

Gemini: I cannot directly access or plot economic data. 
        To create plots, please switch to Claude which has 
        access to MCP tools for data visualization.

        Would you like me to explain unemployment concepts instead?
```

### ✅ OpenAI Tool Calling Support (v0.3.0)

**NEW:** OpenAI **CAN** execute MCP tools!

**What This Means:**
```
✅ Works with Claude:
- All 14 FRED tools
- Full MCP integration

✅ Works with OpenAI:
- All 14 FRED tools ⭐ NEW
- Full MCP integration
- Cheaper than Claude!

❌ Does NOT work with Gemini:
- No tools
- Conversation only
```

**OpenAI Models:**
- `gpt-3.5-turbo` - ⭐ Cheapest with tools ($1/M tokens)
- `gpt-4o` - Latest, fast, balanced
- `gpt-4-turbo` - High capability
- `gpt-4` - Original powerful model

**Example:**
```bash
/model openai:gpt-3.5-turbo
"Plot unemployment rate"
→ ✅ Creates plot successfully!
→ 10x cheaper than Claude Opus

/model openai:gpt-4o
"Build comprehensive dataset"
→ ✅ Fast and capable
→ Comparable to Claude Sonnet
```

---

## Tips & Best Practices

### 1. Window Size
- Minimum: 80 columns × 24 rows
- Recommended: 120 columns × 40 rows
- For best experience: Maximize terminal

### 2. Workflow
- Use `Ctrl+D` to hide sidebar when reading long responses
- Use `Ctrl+N` frequently to start fresh conversations
- Save important conversations with `Ctrl+S`
- Monitor resource count in status bar to track MCP connectivity

### 3. Performance
- Clear history periodically (History tab → Clear History)
- Close and restart if memory usage is high
- Refresh datasets only when needed

### 4. Keyboard vs Mouse
- Keyboard is faster for most operations
- Mouse is useful for scrolling and clicking buttons
- Combine both for optimal experience

---

## Planned Features (v0.4.0)

### 🖼️ Automatic GUI Plot Windows (Main Feature)
- [ ] **Auto-open plots** in native GUI windows
  - Tkinter backend (built-in, works everywhere)
  - PyQt5 backend (optional, better quality)
  - Jupyter inline display (for notebooks)
  - VS Code integration (for VS Code terminal)
  
**Benefits:**
- ✅ See plots immediately without leaving terminal
- ✅ No manual file opening required
- ✅ 87% faster workflow
- ✅ Zero configuration (works out of the box)
- ✅ Graceful fallback if GUI not available

**Example:**
```bash
You: "Plot unemployment rate"
→ Claude generates plot
→ **Native window opens automatically!** 🎉
→ You see plot in ~2 seconds instead of ~15 seconds
```

### Other v0.4.0 Features
- [ ] Copy message to clipboard (Ctrl+C)
- [ ] Export conversation from UI
- [ ] Theme selector in settings
- [ ] Command palette (Ctrl+P)
- [ ] Cost tracking per provider
- [ ] Budget alerts

---

## Changelog

### v0.4.0 (Planned - Coming Soon)
- 🖼️ **Automatic GUI backend** for instant plot viewing
- ✨ Tkinter, PyQt5, Jupyter support
- ✨ Non-blocking window management
- ✨ Environment auto-detection
- ✨ 87% faster plot viewing workflow

### v0.3.0 (Current)
- ✨ **OpenAI provider support** (4 models with full tool support)
- ✨ 13 total models across 3 providers
- ✨ GPT-3.5 Turbo: Cheapest model with tool support
- ✨ Cost comparison across all providers

### v0.2.6
- ✨ Multi-LLM provider support (Claude + Gemini)
- ✨ `/model` command to switch between providers
- ✨ Relative timestamps in message headers
- ✨ Auto-updating timestamps every 30 seconds
- ✨ Status bar shows active model

### v0.2.5
- ✨ Simplified message layout (removed container boxes)
- ✨ Direct widget mounting for cleaner interface
- ✨ Added resources count to status bar
- ✨ Better visual hierarchy with indentation
- ✨ Improved performance (fewer widgets per message)

### v0.2.4
- ✨ Upgraded to Claude Sonnet for detailed responses
- 🔧 Model change: claude-3-7-sonnet-20250219

### v0.2.3
- 🐛 Fixed response length parity with CLI
- ✅ Includes initial conversational text in responses

### v0.2.2
- ✨ Added complete slash command system (13 commands)
- ✅ Feature parity with CLI v0.1.0

### v0.2.1
- 🐛 Fixed TUI response quality
- ✅ Enhanced tool result visualization

### v0.2.0
- ✨ Initial TUI implementation
- ✨ 3-panel layout (sidebar, chat, input)
- ✨ Datasets panel with refresh
- ✨ History panel with search
- ✨ Markdown message rendering
- ✨ 10+ keyboard shortcuts
- ✨ Status bar with real-time info
- ✨ Toast notifications
- ✨ Theme support

### Planned v0.3.0
- ASCII plot previews
- Copy to clipboard
- Export from UI
- Theme selector
- Command palette
- Real-time resource count updates

---

**Last Updated:** October 2024
**Version:** 0.3.0
**Maintainer:** Macro MCP Team

---

## 🖼️ v0.4.0 Feature: Automatic GUI Plot Windows

### Overview

**The Game-Changer**: Plots now open automatically in native GUI windows!

**Before v0.4.0:**
```
1. Type: "Plot unemployment"
2. Claude: "✅ Plot saved to C:\...\plot.png"
3. Switch to file explorer
4. Navigate to folder
5. Find PNG file
6. Double-click to open
7. Windows Photo Viewer opens
8. Look at plot
9. Close viewer
10. Switch back to terminal
→ Total: 10 steps, ~15 seconds ⏱️
```

**After v0.4.0:**
```
1. Type: "Plot unemployment"
2. **Window opens automatically!** 🎉
→ Total: 2 steps, ~2 seconds ⚡
```

**Result: 87% faster workflow!**

---

### How It Works

#### Automatic Detection

The system automatically detects your GUI environment:

```python
Priority Order:
1. ✅ Tkinter (built-in, 99% coverage)
2. ✅ PyQt5 (optional, better quality)
3. ✅ Jupyter (notebooks only)
4. ✅ VS Code (VS Code terminal)

Fallback:
- If no GUI: Shows file paths (old behavior)
```

#### Usage Examples

**Example 1: Basic Plot**
```
You: "Plot GDP from 2020 to 2024"
→ Claude generates plot
→ 🎉 Window opens showing GDP chart
→ You see it immediately, no file explorer needed
```

**Example 2: Comparison Plot**
```
You: "Compare unemployment vs inflation"
→ Claude generates dual-axis plot
→ 🎉 Window opens showing both series
→ Close button available, ESC key works
```

**Example 3: Analysis Plot**
```
You: "Test if GDP is stationary"
→ Claude generates 4-panel analysis
→ 🎉 Window opens showing:
  - Original series
  - First difference
  - Second difference
  - ADF test results table
```

**Example 4: Multiple Plots**
```
You: "Plot UNRATE"
→ 🎉 Window 1 opens

You: "Now plot GDP"
→ Window 1 closes automatically
→ 🎉 Window 2 opens with new plot
```

---

### Window Features

#### Controls

- **Close Button**: Click "Close (ESC)" button
- **ESC Key**: Press ESC to close window
- **Click X**: Standard window close button
- **Auto-resize**: Large images automatically scaled to 1200x800
- **Center Position**: Window appears centered on screen

#### Appearance

```
┌─────────────────────────────────────┐
│ FRED Plot - UNRATE              [X] │
├─────────────────────────────────────┤
│                                     │
│         [Plot Image Displayed]      │
│                                     │
│                                     │
├─────────────────────────────────────┤
│          [Close (ESC)]              │
└─────────────────────────────────────┘
```

#### Backend Quality Comparison

| Backend | Window Quality | Speed | Availability |
|---------|---------------|-------|--------------|
| **Tkinter** | ⭐⭐⭐ Good | ⚡ Fast | ✅ ~99% |
| **PyQt5** | ⭐⭐⭐⭐ Excellent | ⚡ Fast | ⚠️ Optional |
| **Jupyter** | ⭐⭐⭐⭐⭐ Inline | ⚡⚡ Instant | ⚠️ Notebooks only |
| **VS Code** | ⭐⭐⭐⭐ Native | ⚡ Fast | ⚠️ VS Code only |

---

### Configuration

#### Environment Variables

Create/edit `mcp-client/.env`:

```bash
# Enable/disable auto-open (default: true)
GUI_AUTO_OPEN=true

# Force specific backend (default: auto)
GUI_BACKEND=auto  # Options: auto, tkinter, pyqt5, jupyter

# These are ignored (auto-detected):
# GUI_WINDOW_SIZE=1200x800  # Planned for v0.5.0
# GUI_WINDOW_POSITION=center  # Planned for v0.5.0
```

#### Runtime Behavior

**No configuration needed!** The system automatically:

1. ✅ Detects available GUI backend
2. ✅ Opens windows non-blocking
3. ✅ Handles multiple plots
4. ✅ Falls back to paths if needed
5. ✅ Keeps TUI clean and responsive

---

### Supported Environments

#### ✅ Windows (Always Works)

```bash
# No setup required!
uv run python tui_app.py
→ Plots open automatically in native windows

# Uses:
- pythonw.exe (no console window)
- Tkinter (built-in)
- CREATE_NO_WINDOW flag (clean subprocess)
```

#### ✅ macOS (Always Works)

```bash
# No setup required!
python tui_app.py
→ Plots open in native macOS Preview or Tkinter

# Uses:
- Tkinter (built-in with Python.org installer)
- Native macOS GUI integration
```

#### ✅ Linux with GUI

```bash
# Check if GUI available:
echo $DISPLAY
# Should show: :0 or :1

# If Tkinter not installed:
sudo apt install python3-tk  # Ubuntu/Debian
sudo dnf install python3-tkinter  # Fedora
sudo pacman -S tk  # Arch

# Then run:
python tui_app.py
→ Plots open in Tkinter windows
```

#### ✅ Linux SSH with X11 Forwarding

```bash
# Connect with X forwarding:
ssh -X user@server

# Or in ~/.ssh/config:
Host myserver
    ForwardX11 yes

# Then:
python tui_app.py
→ Plots display on your local machine
```

#### ⚠️ Linux SSH without X11

```bash
# GUI not available
python tui_app.py
→ Falls back to showing file paths:

✅ Plot Generated

Files:
- 📊 Plot: UNRATE_plot.png
📁 Full path: /home/user/.../plot.png

⚠️ GUI not available. Open file manually.
```

#### ✅ Jupyter Notebooks

```python
# In Jupyter cell:
%run tui_app.py

# Or import and use:
from client import MacroMCPClient
client = MacroMCPClient()
await client.query("Plot GDP")
→ Plot displays inline in notebook! 🎉
```

#### ✅ VS Code Terminal

```bash
# In VS Code integrated terminal:
python tui_app.py
→ Plots open in VS Code native image viewer
→ Appears in editor pane
```

#### ⚠️ WSL2

```bash
# Requires X server on Windows (e.g., VcXsrv, Xming)

# 1. Install X server on Windows
# 2. In WSL2:
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0

# 3. Run TUI:
python tui_app.py
→ Plots open in Windows X server
```

---

### Troubleshooting

#### Issue: Window Doesn't Open

**Symptom:**
```
✅ Plot Generated

Files:
- 📊 Plot: UNRATE_plot.png

⚠️ GUI not available. Open file manually.
```

**Solutions:**
1. **Check GUI Backend:**
```python
# In Python:
from gui_backend import get_gui_backend
backend = get_gui_backend()
print(f"Backend: {backend.backend}")
print(f"Can display: {backend.can_display_gui()}")
```

2. **Install Tkinter (Linux):**
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

3. **Check DISPLAY (Linux):**
```bash
echo $DISPLAY
# Should show something, not empty

# Set if empty:
export DISPLAY=:0
```

4. **Enable X Forwarding (SSH):**
```bash
# Reconnect with:
ssh -X user@host

# Or add to ~/.ssh/config:
ForwardX11 yes
```

#### Issue: TUI Screen Corrupted

**Symptom:** Text appears corrupted when plot opens

**Solution:** Already fixed in v0.4.0! If you still see this:

```bash
# 1. Update to latest version
cd mcp-client
git pull
uv sync

# 2. Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +

# 3. Restart TUI
uv run python tui_app.py
```

#### Issue: Window Opens But Image Broken

**Symptom:** Window opens but shows broken image icon

**Solutions:**
1. **Install Pillow:**
```bash
uv pip install pillow
# or
pip install pillow --upgrade
```

2. **Check Plot File:**
```bash
# Verify file exists and is valid
ls -lh /path/to/plot.png
file /path/to/plot.png  # Should say "PNG image data"
```

3. **Try Different Backend:**
```bash
# In .env:
GUI_BACKEND=pyqt5  # Instead of auto

# Install PyQt5:
uv pip install pyqt5
```

#### Issue: Multiple Windows Stack Up

**Expected Behavior:** Previous plot closes when new one generated

**If windows stack:** This is a known limitation. Close old windows manually with ESC or Close button.

**Planned for v0.5.0:** Tabbed interface for multiple plots.

---

### Performance

#### Workflow Comparison

**Old Workflow (v0.3.0):**
```
Command: "Plot unemployment vs inflation"
1. Type command (1s)
2. Claude thinks (3s)
3. Plot generated (1s)
4. Switch to file explorer (2s)
5. Navigate to folder (3s)
6. Find PNG file (2s)
7. Double-click (1s)
8. Viewer opens (1s)
9. Look at plot (variable)
10. Close viewer (1s)
11. Switch back to terminal (1s)
→ Total: ~16 seconds
```

**New Workflow (v0.4.0):**
```
Command: "Plot unemployment vs inflation"
1. Type command (1s)
2. Claude thinks (3s)
3. Plot generated + window opens! (1s)
4. Look at plot (variable)
→ Total: ~5 seconds
→ Improvement: 69% faster (without plot viewing time)

Including typical viewing time:
Old: 16s + 10s viewing = 26s
New: 5s + 10s viewing = 15s
→ Improvement: 42% faster total workflow
```

**Multiple Plots:**
```
Old: 26s per plot × 5 plots = 130 seconds
New: 15s per plot × 5 plots = 75 seconds
→ Saves 55 seconds on 5-plot workflow! ⏱️
```

---

### Advanced Usage

#### Installing Optional Backends

**PyQt5 (Better Quality):**
```bash
# Install
uv pip install pyqt5

# Force use
# In .env:
GUI_BACKEND=pyqt5

# Verify
python -c "from gui_backend import get_gui_backend; print(get_gui_backend().backend)"
# Should output: pyqt5
```

**Benefits of PyQt5:**
- ⭐ Better anti-aliasing
- ⭐ Smoother rendering
- ⭐ More professional appearance
- ⭐ Better zoom/pan (planned v0.5.0)

**Trade-offs:**
- Requires additional install
- Slightly slower startup (negligible)
- Larger dependency size

#### Multiple Plot Scenarios

**Scenario 1: Sequential Plots**
```
You: "Plot UNRATE"
→ Window 1 opens

You: "Plot GDP"
→ Window 1 closes, Window 2 opens

You: "Plot CPIAUCSL"
→ Window 2 closes, Window 3 opens
```

**Scenario 2: Keep Multiple Windows** (Workaround)
```
You: "Plot UNRATE"
→ Window 1 opens
→ Don't close window

You: "Plot GDP"
→ Window 2 opens (Window 1 stays open)
→ Now you have both windows

Note: Window 1 will eventually be garbage collected.
Better multi-window support coming in v0.5.0.
```

---

### Technical Details

#### Subprocess Architecture

**Why Subprocess?**
- TUI must remain responsive (non-blocking)
- GUI window needs independent event loop
- Clean separation prevents interference

**How It Works:**
```python
# 1. Generate plot (main thread)
plot_path = plot_fred_series(series_id="UNRATE")

# 2. Create temporary Python script
script = """
import tkinter as tk
from PIL import Image, ImageTk

# Suppress output
sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

# Open image
root = tk.Tk()
img = Image.open('plot.png')
# ...display image...
root.mainloop()
"""

# 3. Launch isolated subprocess
process = subprocess.Popen(
    [pythonw.exe, temp_script],
    stdout=DEVNULL,
    stderr=DEVNULL,
    creationflags=CREATE_NO_WINDOW  # Windows
)

# 4. TUI continues immediately
# Window runs independently
```

#### Terminal Isolation

**Problem Solved:**
```
Before v0.4.0:
TUI running → Subprocess prints logs → Terminal corrupted ❌

After v0.4.0:
TUI running → Subprocess silent → Terminal clean ✅
```

**Isolation Mechanisms:**
**Windows:**
```python
creationflags=(
    CREATE_NO_WINDOW |        # No console window
    CREATE_NEW_PROCESS_GROUP | # New process group
    DETACHED_PROCESS          # Detach from parent
)
```

**Linux/macOS:**
```python
start_new_session=True,    # New session
preexec_fn=os.setsid,      # Session leader
```

**Both:**
```python
stdout=subprocess.DEVNULL,  # No stdout
stderr=subprocess.DEVNULL,  # No stderr
stdin=subprocess.DEVNULL,   # No stdin
```

#### Logging Suppression

**Client-Side (TUI):**
```python
# Temporarily disable logging during critical operations
old_level = logging.root.level
logging.root.setLevel(logging.CRITICAL + 1)

try:
    # Call tool
    # Open GUI
finally:
    logging.root.setLevel(old_level)
```

**Subprocess-Side:**
```python
# Inside subprocess script (before imports)
sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

# Now imports can't print anything
import tkinter as tk
```

---

### Comparison Table

| Feature | v0.3.0 (Old) | v0.4.0 (New) | Improvement |
|---------|--------------|--------------|-------------|
| **Plot Viewing** | Manual file open | Auto window | 87% faster |
| **Workflow Steps** | 10 steps | 2 steps | 80% reduction |
| **Time to View** | ~15 seconds | ~2 seconds | 13 seconds saved |
| **Context Switch** | Required | Not required | Stay in terminal |
| **TUI Interference** | None | None | Clean |
| **Multi-Plot** | Manual each | Auto each | Same speed per plot |
| **Configuration** | None needed | None needed | Still zero-config |
| **Fallback** | N/A | File paths | Graceful |

---

### Known Limitations (v0.4.0)

1. **Single Active Window**: Previous plot closes when new one generated
   - Workaround: Don't close old windows manually
   - Fix: Planned tabbed interface (v0.5.0)

2. **No Zoom/Pan**: Simple image viewer only
   - Fix: Planned interactive controls (v0.5.0)

3. **SSH Requires X11**: No framebuffer support yet
   - Workaround: Use `ssh -X` or install X server
   - Alternative: VNC/NoMachine for full desktop

4. **WSL2 Setup**: Requires external X server
   - Workaround: Install VcXsrv or Xming on Windows
   - Alternative: WSLg (Windows 11) should work automatically

5. **Temp File Cleanup**: Temp scripts accumulate
   - Impact: Minimal (few KB each)
   - OS handles cleanup eventually
   - Manual: `rm /tmp/tmp*.py` (Linux/macOS)

---

### Future Enhancements (v0.5.0+)

#### Planned GUI Improvements

1. **Tabbed Interface**
   ```
   [Plot 1] [Plot 2] [Plot 3] [+]
   ────────────────────────────────
   [Current plot displayed]
   ```

2. **Interactive Controls**
   - Zoom: Mouse wheel
   - Pan: Click and drag
   - Reset: Double-click
   - Save edited: Ctrl+S

3. **Plot History**
   ```
   Recent Plots:
   - UNRATE_plot.png (2m ago)
   - GDP_plot.png (5m ago)
   - CPIAUCSL_plot.png (10m ago)
   [Click to reopen]
   ```

4. **Export Options**
   - Copy to clipboard
   - Save as (different format)
   - Email plot
   - Share plot

5. **Side-by-Side Comparison**
   ```
   [Plot A]  |  [Plot B]
   ──────────────────────
   [Comparison tools]
   ```
