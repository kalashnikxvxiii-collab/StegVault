@echo off
REM StegVault Portable Setup Script
REM Creates virtual environment and installs StegVault with all dependencies

title StegVault Portable Setup

echo ================================================================================
echo   StegVault v0.7.5 - Portable Setup
echo ================================================================================
echo.
echo This script will:
echo   1. Create a Python virtual environment (.venv)
echo   2. Install StegVault and all dependencies
echo   3. Verify installation
echo.
echo This may take 2-3 minutes. Please wait...
echo.
pause

REM Check if Python is available
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)
python --version
echo [OK] Python found
echo.

REM Create virtual environment
echo [2/4] Creating virtual environment (.venv)...
if exist ".venv" (
    echo [!] Virtual environment already exists
    echo [*] Removing old environment...
    rmdir /s /q .venv
)
python -m venv .venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    echo.
    echo Try running as Administrator or check Python installation
    pause
    exit /b 1
)
echo [OK] Virtual environment created
echo.

REM Activate virtual environment
echo [3/4] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo [*] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo.

REM Install StegVault
echo [4/4] Installing StegVault and dependencies...
echo [*] This may take 2-3 minutes, please wait...
pip install stegvault
if errorlevel 1 (
    echo [ERROR] Failed to install StegVault
    echo.
    echo Try:
    echo   1. Check internet connection
    echo   2. Run as Administrator
    echo   3. Manually install: .venv\Scripts\activate ^&^& pip install stegvault
    pause
    exit /b 1
)
echo [OK] StegVault installed successfully
echo.

REM Verify installation
echo [*] Verifying installation...
python -m stegvault --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Installation verification failed
    echo [*] StegVault may still work, try launching the TUI
) else (
    python -m stegvault --version
    echo [OK] Installation verified
)
echo.

echo ================================================================================
echo   Setup Complete!
echo ================================================================================
echo.
echo Next steps:
echo   1. Double-click "scripts\launch_tui.bat" to start StegVault TUI
echo   2. Press 'h' in TUI for keyboard shortcuts
echo   3. Read README.md for full documentation
echo.
echo Enjoy StegVault!
echo.
pause
