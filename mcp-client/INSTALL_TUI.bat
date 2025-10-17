@echo off
REM Macro MCP TUI - Installation Script for Windows
REM This script installs dependencies and verifies the setup

echo ========================================================
echo      Macro MCP TUI - Installation and Setup Script
echo ========================================================
echo.

REM Check if uv is installed
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: 'uv' package manager not found
    echo.
    echo Please install uv first:
    echo   Visit: https://github.com/astral-sh/uv
    echo.
    pause
    exit /b 1
)

echo Found uv package manager
echo.

REM Navigate to script directory
cd /d "%~dp0"

echo Installing dependencies...
echo.

REM Sync dependencies
call uv sync

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Dependencies installed successfully!
    echo.
) else (
    echo.
    echo Error installing dependencies
    pause
    exit /b 1
)

REM Check for .env files
if not exist "..\macro\app\.env" (
    echo Warning: No .env file found in macro\app\
    echo.
    echo Please create .env file with:
    echo   FRED_API_KEY=your_key_here
    echo.
)

if not exist ".env" (
    echo Warning: No .env file found in mcp-client\
    echo.
    echo Please create .env file with:
    echo   ANTHROPIC_API_KEY=your_key_here
    echo.
)

echo ========================================================
echo              Installation Complete!
echo ========================================================
echo.
echo To start the TUI application:
echo    uv run python tui_app.py
echo.
echo Or use the launcher:
echo    uv run python run_tui.py
echo.
echo For help, see TUI_GUIDE.md
echo.
pause
