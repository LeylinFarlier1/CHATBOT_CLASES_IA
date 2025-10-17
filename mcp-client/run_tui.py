#!/usr/bin/env python3
"""
Launcher script for Macro MCP TUI
Simple wrapper to start the Textual application
"""
import sys
from tui_app import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for using Macro MCP!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("\nMake sure you've installed dependencies:")
        print("  cd mcp-client")
        print("  uv sync")
        sys.exit(1)
