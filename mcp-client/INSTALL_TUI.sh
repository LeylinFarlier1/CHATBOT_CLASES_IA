#!/bin/bash

# Macro MCP TUI - Installation Script
# This script installs dependencies and verifies the setup

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║     Macro MCP TUI - Installation & Setup Script       ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: 'uv' package manager not found"
    echo ""
    echo "Please install uv first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    exit 1
fi

echo "✅ Found uv package manager"
echo ""

# Navigate to mcp-client directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📦 Installing dependencies..."
echo ""

# Sync dependencies
uv sync

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Dependencies installed successfully!"
    echo ""
else
    echo ""
    echo "❌ Error installing dependencies"
    exit 1
fi

# Check for .env file
if [ ! -f "../macro/app/.env" ]; then
    echo "⚠️  Warning: No .env file found in macro/app/"
    echo ""
    echo "Please create .env file with:"
    echo "  FRED_API_KEY=your_key_here"
    echo ""
fi

if [ ! -f ".env" ]; then
    echo "⚠️  Warning: No .env file found in mcp-client/"
    echo ""
    echo "Please create .env file with:"
    echo "  ANTHROPIC_API_KEY=your_key_here"
    echo ""
fi

echo "╔════════════════════════════════════════════════════════╗"
echo "║                 Installation Complete!                 ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 To start the TUI application:"
echo "   uv run python tui_app.py"
echo ""
echo "Or use the launcher:"
echo "   uv run python run_tui.py"
echo ""
echo "📚 For help, see TUI_GUIDE.md"
echo ""
