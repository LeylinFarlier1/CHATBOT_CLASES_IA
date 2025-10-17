# Claude AI Integration Guide

> Documentation for integrating Macro MCP with Claude AI and understanding the MCP protocol implementation

---

## Table of Contents
1. [Overview](#overview)
2. [MCP Architecture](#mcp-architecture)
3. [Tool Descriptions for Claude](#tool-descriptions-for-claude)
4. [Resource System](#resource-system)
5. [Conversation Flow](#conversation-flow)
6. [Best Practices](#best-practices)
7. [Common Patterns](#common-patterns)
8. [Advanced Usage](#advanced-usage)

---

## Overview

The Macro MCP system implements the **Model Context Protocol (MCP)** to enable Claude AI to interact with macroeconomic data through a standardized interface. This document explains how Claude interprets and uses the available tools and resources.

### Key Concepts

**MCP Tools**: Functions Claude can call to perform actions
- `fetch_*`: Read-only data retrieval
- `plot_*`: Visualization generation
- `build_*`: Data transformation and dataset construction

**MCP Resources**: Read-only data Claude can access automatically
- `fred://datasets/recent`: Lists available datasets with metadata

**Client Session**: Maintains conversation context and history
- Conversation history preserved across queries
- Tool results cached for 5 minutes
- Automatic resource discovery

---

## MCP Architecture

### Server Component (`macro/app/server_mcp.py`)

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("macro-chatbot")

@mcp.tool()
def fetch_series_metadata_tool(series_id: str) -> str:
    """Fetches metadata for a FRED series."""
    return fetch_series_metadata(series_id)

@mcp.resource("fred://datasets/recent")
def get_recent_datasets_resource() -> str:
    """Lists recent FRED datasets."""
    return list_recent_datasets(limit=10)
```

### Client Component (`mcp-client/client.py`)

```python
from anthropic import Anthropic
from mcp import ClientSession

# Initialize Claude with MCP tools
claude_response = anthropic.messages.create(
    model="claude-3-5-haiku-20241022",
    max_tokens=4096,
    messages=messages,
    tools=available_tools,  # MCP tools exposed to Claude
)
```

### Communication Flow

```
User Query → Claude AI → MCP Tool Selection → Tool Execution → Result Processing → Claude Response
     ↑                                                                                    ↓
     └─────────────────────────── Conversation History ──────────────────────────────────┘
```

---

## Tool Descriptions for Claude

### Understanding Tool Schemas

Each MCP tool has a schema that Claude uses to understand:
1. **Purpose**: What the tool does
2. **Parameters**: What inputs it needs
3. **Returns**: What output to expect

**Example Tool Schema:**

```json
{
  "name": "fetch_series_metadata_tool",
  "description": "Fetches metadata for a FRED series",
  "input_schema": {
    "type": "object",
    "properties": {
      "series_id": {
        "type": "string",
        "description": "FRED series ID (e.g., 'GDP', 'UNRATE', 'CPIAUCSL')"
      }
    },
    "required": ["series_id"]
  }
}
```

### How Claude Interprets Tools

**User Query:** "Show me information about the GDP series"

**Claude's Reasoning:**
1. Identifies need for metadata about a FRED series
2. Recognizes "GDP" as a series identifier
3. Selects `fetch_series_metadata_tool`
4. Constructs tool call: `{"series_id": "GDP"}`
5. Receives JSON result with metadata
6. Formats result for user

### Tool Categories for Claude

#### 1. Fetch Tools (Information Retrieval)

**When to Use:**
- User asks for information about a series
- User wants to search for economic indicators
- User needs historical data

**Examples:**
```
User: "What is the UNRATE series?"
→ fetch_series_metadata_tool(series_id="UNRATE")

User: "Search for inflation indicators"
→ search_fred_series_tool(search_text="inflation", limit=50)

User: "Get unemployment data from 2020 to 2024"
→ fetch_series_observations_tool(series_id="UNRATE",
                                  observation_start="2020-01-01",
                                  observation_end="2024-12-31")
```

#### 2. Plot Tools (Visualization)

**When to Use:**
- User requests a chart/graph/plot
- User wants to compare series visually
- User asks for trend analysis

**Examples:**
```
User: "Plot GDP from 2000 to 2024"
→ plot_fred_series_tool(series_id="GDP",
                        observation_start="2000-01-01",
                        observation_end="2024-12-31")

User: "Compare unemployment and inflation"
→ plot_dual_axis_tool(series_id_left="UNRATE",
                      series_id_right="CPIAUCSL",
                      observation_start="2015-01-01")

User: "Test if GDP is stationary"
→ analyze_differencing_tool(series_id="GDP")
```

#### 3. Build Tools (Data Construction)

**When to Use:**
- User wants to create a dataset with multiple series
- User requests transformations (YoY, QoQ, etc.)
- User needs data for external analysis

**Examples:**
```
User: "Build a dataset with unemployment, inflation (YoY), and GDP (QoQ)"
→ build_fred_dataset_tool(
    series_list=["UNRATE", "CPIAUCSL", "GDP"],
    transformations={"CPIAUCSL": "YoY", "GDP": "QoQ"},
    observation_start="2000-01-01"
  )

User: "Create a dataset with 5 monetary policy indicators"
→ build_fred_dataset_tool(
    series_list=["FEDFUNDS", "M2SL", "DGS10", "T10Y2Y", "WALCL"],
    transformations={}
  )
```

#### 4. Dataset Tools (Working with Saved Data)

**When to Use:**
- User references previously built datasets
- User mentions column names with transformation suffixes (e.g., "CPIAUCSL_YoY")
- User says "from the dataset" or "use the dataset"

**Examples:**
```
User: "Plot UNRATE vs CPIAUCSL_YoY from the dataset"
→ plot_from_dataset_tool(column_left="UNRATE",
                         column_right="CPIAUCSL_YoY")

User: "Show me what datasets are available"
→ Read resource: fred://datasets/recent
```

---

## Resource System

### Understanding MCP Resources

**Resources vs Tools:**
- **Tools**: Claude must explicitly call them (actions)
- **Resources**: Claude can read automatically (data)

### The `fred://datasets/recent` Resource

**Purpose:** Solves the context limitation problem

**Problem:**
```
User: "Build a dataset with UNRATE and CPIAUCSL (YoY)"
Claude: *builds dataset* ✅
[NEW SESSION - CONTEXT LOST]
User: "Plot UNRATE vs CPIAUCSL_YoY"
Claude: ??? (doesn't know dataset exists)
```

**Solution with Resources:**
```
User: "Build a dataset with UNRATE and CPIAUCSL (YoY)"
Claude: *builds dataset* ✅

[NEW SESSION]
User: "Plot UNRATE vs CPIAUCSL_YoY"
Claude: *checks fred://datasets/recent resource*
        *finds dataset with those exact columns*
        *uses plot_from_dataset_tool correctly* ✅
```

### How Claude Uses Resources

**Automatic Discovery:**
1. Client exposes resource as a "synthetic tool"
2. Claude sees `read_mcp_resource` in tool list
3. Claude reads resource when relevant to query
4. Resource provides dataset inventory

**Resource Output Example:**
```
📂 DATASETS RECIENTES (últimos 10)

1. FRED_dataset_UNRATE_CPIAUCSL
   📅 Creado: 2025-10-11 19:30:15
   📊 Período: 1948-01-01 a 2025-08-01
   🔹 Columnas: UNRATE, CPIAUCSL_YoY
   🔄 Transformaciones: CPIAUCSL → YoY
   📍 Path: C:/Users/.../dataset.csv
```

**Claude's Decision Making:**
```
Query: "Plot unemployment vs inflation YoY"

Claude reasoning:
1. User mentions "inflation YoY" → likely refers to transformed column
2. Check fred://datasets/recent resource
3. Find dataset with columns: UNRATE, CPIAUCSL_YoY
4. Use plot_from_dataset_tool with those exact column names
```

---

## Conversation Flow

### Multi-Turn Conversations

**Turn 1: User Query**
```json
{
  "role": "user",
  "content": "Show me GDP data from 2020 to 2024"
}
```

**Turn 2: Claude Response with Tool Use**
```json
{
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "I'll fetch the GDP data for you."
    },
    {
      "type": "tool_use",
      "id": "toolu_123",
      "name": "fetch_series_observations_tool",
      "input": {
        "series_id": "GDP",
        "observation_start": "2020-01-01",
        "observation_end": "2024-12-31"
      }
    }
  ]
}
```

**Turn 3: Tool Result**
```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_123",
      "content": "{\"tool\": \"fetch_series_observations\", \"series_id\": \"GDP\", ...}"
    }
  ]
}
```

**Turn 4: Claude Final Response**
```json
{
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Here is the GDP data from 2020 to 2024:\n\n[Analysis of data]..."
    }
  ]
}
```

### Conversation History Management

**Client-Side History:**
```python
# Stored in client.conversation_history
self.conversation_history = [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": [...]},
    {"role": "user", "content": [...]},  # tool results
    {"role": "assistant", "content": [...]}
]
```

**History Manager (Fase 3):**
```python
# Stored in client.history_manager
self.history_manager.add(
    query="Show me GDP data from 2020 to 2024",
    response="Here is the GDP data...",
    tools_used=["fetch_series_observations_tool"]
)
```

---

## Best Practices

### For Claude's Tool Selection

**1. Series ID Detection**

✅ **Good:**
```
User: "Plot unemployment rate"
Claude: Recognizes "unemployment rate" → series_id="UNRATE"
```

❌ **Avoid:**
```
User: "Plot unemployment rate"
Claude: Passes series_id="unemployment rate" (invalid)
```

**2. Date Format Handling**

✅ **Good:**
```
User: "GDP from 2020 to 2024"
Claude: observation_start="2020-01-01", observation_end="2024-12-31"
```

❌ **Avoid:**
```
User: "GDP from 2020 to 2024"
Claude: observation_start="2020", observation_end="2024" (wrong format)
```

**3. Transformation Understanding**

✅ **Good:**
```
User: "I want year-over-year inflation"
Claude: transformations={"CPIAUCSL": "YoY"}
```

✅ **Also Good:**
```
User: "Quarter-over-quarter GDP growth"
Claude: transformations={"GDP": "QoQ"}
```

**4. Dataset Workflow**

✅ **Good:**
```
User: "Build dataset with UNRATE and CPIAUCSL with YoY transformation"
Claude: *builds dataset*
User: "Now plot UNRATE vs CPIAUCSL_YoY"
Claude: *uses plot_from_dataset_tool* (no recalculation)
```

❌ **Avoid:**
```
User: "Build dataset with UNRATE and CPIAUCSL with YoY transformation"
Claude: *builds dataset*
User: "Now plot UNRATE vs CPIAUCSL_YoY"
Claude: *uses plot_dual_axis_tool* (downloads data again unnecessarily)
```

### For Error Handling

**1. Invalid Series ID**

```python
try:
    result = fetch_series_metadata_tool(series_id="INVALID_ID")
except Exception as e:
    # Claude should:
    # 1. Acknowledge the error
    # 2. Suggest using search_fred_series_tool
    # 3. Ask user for clarification
```

**2. No Data Available**

```python
# If observation range returns empty
→ Claude should explain and suggest broader date range
```

**3. Tool Execution Failure**

```python
# If tool returns error
→ Claude should:
  1. Parse error message
  2. Explain issue to user
  3. Suggest alternatives
```

---

## Common Patterns

### Pattern 1: Search → Metadata → Observations → Plot

```
User: "I need data on consumer prices"

Step 1: Search
→ search_fred_series_tool(search_text="consumer prices")

Step 2: Identify Series
→ Claude presents options, user selects "CPIAUCSL"

Step 3: Get Metadata
→ fetch_series_metadata_tool(series_id="CPIAUCSL")

Step 4: Fetch Data
→ fetch_series_observations_tool(series_id="CPIAUCSL")

Step 5: Visualize
→ plot_fred_series_tool(series_id="CPIAUCSL")
```

### Pattern 2: Build → Plot → Export

```
User: "Create a monetary policy analysis dataset"

Step 1: Build Dataset
→ build_fred_dataset_tool(
    series_list=["FEDFUNDS", "DGS10", "T10Y2Y"],
    transformations={}
  )

Step 2: Plot Comparisons
→ plot_from_dataset_tool(
    column_left="FEDFUNDS",
    column_right="DGS10"
  )

Step 3: Save Conversation
→ User uses /save command
```

### Pattern 3: Stationarity Testing

```
User: "Test if GDP is stationary"

Step 1: Analyze Differencing
→ analyze_differencing_tool(series_id="GDP")

Step 2: Interpret Results
→ Claude explains ADF test results:
  - Original series: p-value > 0.05 → non-stationary
  - First difference: p-value < 0.05 → stationary
  - Recommendation: Use first difference for modeling
```

---

## Advanced Usage

### Multi-Series Analysis

**Scenario:** User wants to analyze relationships between multiple series

```python
# Step 1: Build comprehensive dataset
build_fred_dataset_tool(
    series_list=["UNRATE", "CPIAUCSL", "GDP", "FEDFUNDS", "DGS10"],
    transformations={
        "CPIAUCSL": "YoY",
        "GDP": "QoQ"
    },
    observation_start="2000-01-01"
)

# Step 2: Create multiple visualizations
plot_from_dataset_tool(column_left="UNRATE", column_right="CPIAUCSL_YoY")
plot_from_dataset_tool(column_left="FEDFUNDS", column_right="DGS10")
plot_from_dataset_tool(column_left="UNRATE", column_right="GDP_QoQ")

# Step 3: Claude interprets patterns
# - Phillips curve relationship (UNRATE vs CPIAUCSL_YoY)
# - Yield curve dynamics (FEDFUNDS vs DGS10)
# - Okun's law (UNRATE vs GDP_QoQ)
```

### Custom Transformation Workflows

**Available Transformations:**

1. **none**: Raw data (no transformation)
2. **YoY**: Year-over-Year percentage change (12 periods)
   - Use for: Inflation, wage growth, monetary aggregates
3. **QoQ**: Quarter-over-Quarter percentage change (3 periods)
   - Use for: GDP growth, quarterly indicators
4. **MoM**: Month-over-Month percentage change (1 period)
   - Use for: High-frequency data, retail sales
5. **diff**: First difference
   - Use for: Detrending, stationarity
6. **pct_change**: Simple percentage change
   - Use for: General growth rates
7. **log**: Natural logarithm
   - Use for: Normalizing distributions
8. **log_diff**: Log difference (approximate % change)
   - Use for: Growth rates with properties of logs

**Example Workflow:**
```python
# Inflation analysis with multiple perspectives
build_fred_dataset_tool(
    series_list=["CPIAUCSL", "PCEPI", "CPILFESL"],
    transformations={
        "CPIAUCSL": "YoY",    # Headline CPI YoY
        "PCEPI": "YoY",       # Core PCE YoY
        "CPILFESL": "MoM"     # Core CPI MoM
    }
)
```

### Resource-Aware Queries

**Claude's Resource Checking Logic:**

```python
# Pseudo-code for Claude's decision making
def handle_plot_request(column_left, column_right):
    # Check if columns have transformation suffixes
    if has_transformation_suffix(column_left) or has_transformation_suffix(column_right):
        # Read resource to find matching dataset
        datasets = read_resource("fred://datasets/recent")
        matching_dataset = find_dataset_with_columns(datasets, [column_left, column_right])

        if matching_dataset:
            # Use dataset tool (efficient)
            return plot_from_dataset_tool(column_left, column_right)
        else:
            # Inform user dataset not found
            return "Dataset not found. Please build dataset first."
    else:
        # Use direct plot tool (downloads data)
        return plot_dual_axis_tool(series_id_left=column_left, series_id_right=column_right)
```

### Caching Strategy

**Client-Side Cache (5 min TTL):**

```python
# First query
response = await session.list_tools()
cache.set("tools_list", response.tools)

# Subsequent queries within 5 min
tools = cache.get("tools_list")  # Returns cached version
```

**Benefits for Claude:**
- Faster tool discovery
- Reduced latency
- Consistent tool schemas during conversation

---

## Integration Examples

### Example 1: Embedding in Custom Application

```python
from mcp import ClientSession
from anthropic import Anthropic

# Custom application
class EconomicAnalysisBot:
    def __init__(self):
        self.mcp_session = ClientSession(...)
        self.anthropic = Anthropic(api_key="...")

    async def analyze_indicator(self, indicator_name: str):
        # Get MCP tools
        tools_response = await self.mcp_session.list_tools()

        # Query Claude with MCP tools
        response = self.anthropic.messages.create(
            model="claude-3-5-haiku-20241022",
            messages=[{
                "role": "user",
                "content": f"Analyze the {indicator_name} indicator"
            }],
            tools=tools_response.tools
        )

        # Process tool calls
        for content in response.content:
            if content.type == "tool_use":
                result = await self.mcp_session.call_tool(
                    content.name,
                    content.input
                )
                # Handle result...
```

### Example 2: Batch Processing

```python
# Process multiple series in batch
async def batch_analysis(series_ids: list):
    for series_id in series_ids:
        # Fetch metadata
        metadata = await call_tool("fetch_series_metadata_tool",
                                   {"series_id": series_id})

        # Plot series
        plot = await call_tool("plot_fred_series_tool",
                              {"series_id": series_id})

        # Analyze stationarity
        analysis = await call_tool("analyze_differencing_tool",
                                   {"series_id": series_id})

        # Claude interprets results
        summary = await claude_summarize(metadata, plot, analysis)

        yield summary
```

---

## Debugging Guide

### Tool Call Inspection

**Enable Logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Inspect Tool Calls:**
```python
# In client.py
for content in claude_response.content:
    if content.type == "tool_use":
        logger.debug(f"Tool: {content.name}")
        logger.debug(f"Args: {content.input}")
```

### Common Issues

**1. Claude Not Using Tools**
- Check tool schemas are valid
- Verify tools are in available_tools list
- Ensure query is clear and actionable

**2. Wrong Tool Selection**
- Review tool descriptions for clarity
- Check if multiple tools overlap in purpose
- Improve parameter descriptions

**3. Invalid Parameters**
- Validate input schemas
- Add examples to parameter descriptions
- Use enums for fixed options

---

## Performance Optimization

### Tips for Efficient Tool Use

1. **Batch Operations**: Build datasets with multiple series at once
2. **Use Resources**: Check available datasets before downloading
3. **Cache Results**: Let TTL cache reduce redundant calls
4. **Reuse Datasets**: Use `plot_from_dataset_tool` instead of re-downloading
5. **Async Operations**: Client handles tool calls asynchronously

### Monitoring

```python
# Track tool usage
stats = history_manager.get_stats()
print(f"Tools used: {stats['tools_usage']}")

# Cache statistics
cache_stats = cache.get_stats()
print(f"Cache hit rate: {cache_stats['valid_entries'] / cache_stats['total_entries']}")
```

---

## Version Compatibility

**Current Version:** 0.2.6

**Claude Models Tested:**
- ✅ claude-3-5-haiku-20241022 (fast, default)
- ✅ claude-3-7-sonnet-20250219 (balanced, recommended)
- ✅ claude-3-5-sonnet-20241022 (balanced)
- ✅ claude-sonnet-4-5-20250929 (most capable)
- ⚠️ claude-3-opus (not tested)

**Gemini Models:**
- ⚠️ gemini-2.0-flash-exp (NO tool support)
- ⚠️ gemini-1.5-pro (NO tool support)
- ⚠️ gemini-1.5-flash (NO tool support)

**MCP Protocol Version:** 1.17.0

**API Requirements:**
- FRED API: Any version
- Anthropic API: SDK version 0.69.0+
- Google Gemini API: SDK version 0.8.0+ (limited functionality)

---

## Multi-LLM Support (v0.3.0)

### Provider Comparison

| Feature | Claude | OpenAI | Gemini |
|---------|--------|--------|--------|
| **MCP Tool Calling** | ✅ Full support | ✅ Full support | ❌ Not supported |
| **FRED Data Access** | ✅ All 14 tools | ✅ All 14 tools | ❌ None |
| **Conversational** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Plot Generation** | ✅ Yes | ✅ Yes | ❌ No |
| **Dataset Building** | ✅ Yes | ✅ Yes | ❌ No |
| **Cost (cheapest)** | $0.80/M (Haiku) | $0.50/M (GPT-3.5) | $0.075/M (no tools) |
| **Speed** | Fast | Fast | Very Fast |
| **Best For** | Balanced | Cheap or Powerful | Theory only |

### Cost Analysis

| Provider | Model | Per 1M Tokens | Tool Support | Recommendation |
|----------|-------|---------------|--------------|----------------|
| **OpenAI** | GPT-3.5 Turbo | $1.00 | ✅ Yes | ⭐ **Best value** |
| **Claude** | Haiku 3.5 | $2.40 | ✅ Yes | Fast |
| **Claude** | Sonnet 3.7 | $9.00 | ✅ Yes | ⭐ **Best balance** |
| **OpenAI** | GPT-4o | $6.25 | ✅ Yes | Good balance |
| **OpenAI** | GPT-4 Turbo | $20.00 | ✅ Yes | High capability |
| **Claude** | Opus 4.1 | $45.00 | ✅ Yes | Maximum intelligence |

### Why OpenAI Works (Unlike Gemini)

**OpenAI Function Calling:**
```python
# OpenAI uses "function" format (compatible with MCP)
{
  "type": "function",
  "function": {
    "name": "plot_fred_series_tool",
    "parameters": {...}
  }
}

# We convert MCP tools to this format automatically ✅
```

**Gemini Problem:**
```python
# Gemini uses incompatible format
{
  "function_declaration": {
    "name": "plot_fred_series_tool",
    "parameters": {...}  # Different schema
  }
}

# Cannot convert easily ❌
```

### Recommended Usage by Provider

**✅ Use Claude for:**
- Best overall quality
- Most reliable tool calling
- Balanced cost/performance
- Default recommendation

**✅ Use OpenAI for:**
- Cost-sensitive workflows (GPT-3.5 Turbo)
- Latest technology (GPT-4o)
- High capability at lower cost than Claude Opus
- Experimentation

**⚠️ Use Gemini for:**
- Pure theory (no data)
- Ultra-low-cost conversation
- Last resort only

**Example Workflows:**
```bash
# Cost-optimized
/model openai:gpt-3.5-turbo
"Build dataset with 20 series" → $0.02

# Quality-optimized
/model claude:sonnet-3.7
"Complex analysis" → $0.50

# Maximum capability
/model claude:opus-4.1
"Research-grade analysis" → $2.00
```

---

## Future Enhancements

### Planned Features (v0.4.0)

1. **Automatic GUI Windows**: Native plot windows open automatically
2. **Cost Tracking**: Per-provider usage monitoring
3. **Auto-Selection**: Choose provider based on query complexity
4. **Model Comparison**: Side-by-side responses
5. **Ollama Support**: Local models integration

### Planned Features (v0.5.0+)

1. **Streaming Responses**: Real-time feedback
2. **Interactive Plots**: Zoom, pan, annotate
3. **Multi-plot Comparison**: Side-by-side windows
4. **Advanced Caching**: Persistent cache across sessions

---

**Document Version:** 1.2
**Last Updated:** October 2024 (v0.3.0)
**Maintainer:** Macro MCP Team
