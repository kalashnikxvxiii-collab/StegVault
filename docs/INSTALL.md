# StegVault - Portable Windows Installation

This portable package allows you to run StegVault TUI without global Python installation. All dependencies are contained in a local virtual environment.

## System Requirements

- **Windows 10/11** (64-bit)
- **Python 3.9 or higher** installed
  - Download from: [python.org/downloads](https://www.python.org/downloads/)

## Quick Start (Automatic Setup)

1. Extract this ZIP to a folder (e.g., `C:\StegVault`)

2. Double-click: `scripts/setup_portable.bat`
   - This will create a virtual environment (`.venv`)
   - Install all StegVault dependencies
   - Takes ~2-3 minutes

3. Double-click: `scripts/launch_tui.bat`
   - Launches StegVault TUI instantly

## Manual Setup (Alternative)

If the automatic setup fails, follow these steps:

1. Open Command Prompt in the StegVault folder
   - **Shift + Right-click** → "Open PowerShell window here"

2. Create virtual environment:
   ```batch
   python -m venv .venv
   ```

3. Activate virtual environment:
   ```batch
   .venv\Scripts\activate.bat
   ```

4. Install StegVault:
   ```batch
   pip install stegvault
   ```

5. Launch TUI:
   ```batch
   python -m stegvault tui
   ```

## Usage

After setup, simply double-click `scripts/launch_tui.bat` to start StegVault TUI.

**First-time users:**
- Press **'h'** for keyboard shortcuts
- Use **arrow keys** to navigate
- Press **'q'** to quit

## Troubleshooting

### Problem: "Python is not recognized"
**Solution:** Install Python from [python.org](https://www.python.org) and check "Add Python to PATH"

### Problem: "pip is not recognized"
**Solution:** Reinstall Python with "pip" component enabled

### Problem: Virtual environment activation fails
**Solution:** Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problem: Dependencies fail to install
**Solution:** Update pip first:
```batch
.venv\Scripts\python.exe -m pip install --upgrade pip
```
Then retry:
```batch
pip install stegvault
```

## Folder Structure

```
StegVault/
├── .venv/                      # Virtual environment (created by setup)
├── scripts/
│   ├── launch_tui.bat          # Quick launcher
│   └── setup_portable.bat      # One-time setup
├── requirements.txt            # Dependency list
├── docs/
│   └── INSTALL.md              # This file
└── README.md                   # Full documentation
```

## Updates

To update StegVault to a newer version:

1. Open Command Prompt in StegVault folder
2. Activate environment:
   ```batch
   .venv\Scripts\activate.bat
   ```
3. Upgrade StegVault:
   ```batch
   pip install --upgrade stegvault
   ```

## Support

- **GitHub:** [github.com/kalashnikxvxiii/StegVault](https://github.com/kalashnikxvxiii/StegVault)
- **Issues:** [github.com/kalashnikxvxiii/StegVault/issues](https://github.com/kalashnikxvxiii/StegVault/issues)
