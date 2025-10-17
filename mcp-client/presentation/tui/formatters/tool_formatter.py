"""
Tool Formatter
Formats tool calls and results for display
"""
from typing import List, Dict, Any


class ToolFormatter:
    """Formats tool calls and results for display"""

    @staticmethod
    def format_tool_call(tool_name: str, args: Dict[str, Any]) -> str:
        """
        Format a tool call for display
        
        Args:
            tool_name: Name of the tool
            args: Tool arguments
            
        Returns:
            Formatted tool call string
        """
        # Show first 2 arguments with truncated values
        args_preview = ", ".join([
            f"{k}={str(v)[:20]}" 
            for k, v in list(args.items())[:2]
        ])
        
        if len(args) > 2:
            args_preview += ", ..."
        
        return f"🔧 **Executing:** `{tool_name}({args_preview})`"

    @staticmethod
    def format_tool_calls_summary(tool_calls: List[Dict[str, Any]]) -> str:
        """
        Format a summary of tool calls
        
        Args:
            tool_calls: List of tool call dictionaries
            
        Returns:
            Formatted summary string
        """
        if not tool_calls:
            return ""
        
        summary = "🔧 **Tools used:**\n"
        for tc in tool_calls:
            tool_name = tc.get("name", "unknown")
            summary += f"- `{tool_name}`\n"
        
        return summary

    @staticmethod
    def format_tool_result(tool_name: str, result: str, success: bool = True) -> str:
        """
        Format a tool result for display
        
        Args:
            tool_name: Name of the tool
            result: Tool result
            success: Whether the tool call was successful
            
        Returns:
            Formatted result string
        """
        if success:
            icon = "✅"
            prefix = "Result"
        else:
            icon = "❌"
            prefix = "Error"
        
        # Truncate long results
        truncated_result = result[:200]
        if len(result) > 200:
            truncated_result += "...\n\n*(Result truncated)*"
        
        return f"{icon} **{prefix} from `{tool_name}`:**\n\n{truncated_result}"

    @staticmethod
    def format_tools_list(tools: List[Dict[str, Any]]) -> str:
        """
        Format a list of available tools
        
        Args:
            tools: List of tool dictionaries
            
        Returns:
            Formatted tools list string
        """
        if not tools:
            return "⚠️ No tools available"
        
        tools_list = f"### 🔧 Available Tools ({len(tools)})\n\n"
        for i, tool in enumerate(tools, 1):
            name = tool.get("name", "unknown")
            desc = tool.get("description", "No description")[:80]
            if len(tool.get("description", "")) > 80:
                desc += "..."
            tools_list += f"{i}. **{name}**\n   {desc}\n\n"
        
        tools_list += "\n💡 Use `/tools <name>` to see details of a specific tool."
        return tools_list

    @staticmethod
    def format_tool_details(tool: Dict[str, Any]) -> str:
        """
        Format detailed information about a tool
        
        Args:
            tool: Tool dictionary
            
        Returns:
            Formatted tool details string
        """
        import json
        
        name = tool.get("name", "unknown")
        description = tool.get("description", "No description")
        schema = tool.get("inputSchema", {})
        
        schema_json = json.dumps(schema, indent=2) if schema else "N/A"
        
        details = f"""### 🔧 {name}

**Description:**
{description}

**Input Schema:**
```json
{schema_json}
```
"""
        return details
