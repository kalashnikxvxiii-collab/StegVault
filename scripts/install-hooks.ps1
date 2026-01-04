# Install git hooks for StegVault (Windows PowerShell)
# Run this once after cloning the repository

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "StegVault Git Hooks Installer" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in a git repository
if (-not (Test-Path .git)) {
    Write-Host "❌ Error: Not a git repository" -ForegroundColor Red
    Write-Host "   Run this script from the repository root" -ForegroundColor Red
    exit 1
}

Write-Host "Installing pre-commit hook..." -ForegroundColor Yellow

# Create hook content
$hookContent = @'
#!/bin/bash
# Git pre-commit hook for StegVault
# Automatically runs validation before each commit
# This prevents CI failures by catching issues locally

# Determine OS and run appropriate script
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash)
    echo "Running pre-commit validation on Windows..."
    powershell.exe -ExecutionPolicy Bypass -File ./scripts/pre-commit.ps1
else
    # Linux/Mac
    echo "Running pre-commit validation on Unix..."
    bash ./scripts/pre-commit.sh
fi

# Capture exit code
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "=========================================="
    echo "⚠️  COMMIT BLOCKED BY PRE-COMMIT HOOK"
    echo "=========================================="
    echo ""
    echo "Pre-commit validation failed. Fix the issues above."
    echo ""
    echo "If you absolutely need to skip validation (NOT RECOMMENDED):"
    echo "  git commit --no-verify"
    echo ""
    echo "But note: CI will still fail on push!"
    echo ""
    exit 1
fi

exit 0
'@

# Write hook file
$hookPath = ".git\hooks\pre-commit"
$hookContent | Out-File -FilePath $hookPath -Encoding ASCII -NoNewline

Write-Host "✅ Pre-commit hook installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "The hook will automatically run before each commit." -ForegroundColor White
Write-Host "It will block commits that would fail CI." -ForegroundColor White
Write-Host ""
Write-Host "To manually run validation:" -ForegroundColor White
Write-Host "  .\scripts\pre-commit.ps1    (Windows)" -ForegroundColor Gray
Write-Host "  ./scripts/pre-commit.sh     (Linux/Mac in Git Bash)" -ForegroundColor Gray
Write-Host ""
Write-Host "To skip validation (NOT RECOMMENDED):" -ForegroundColor White
Write-Host "  git commit --no-verify" -ForegroundColor Gray
Write-Host ""
