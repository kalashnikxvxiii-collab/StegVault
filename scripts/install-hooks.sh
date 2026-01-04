#!/bin/bash
# Install git hooks for StegVault
# Run this once after cloning the repository

echo "=========================================="
echo "StegVault Git Hooks Installer"
echo "=========================================="
echo ""

# Check if we're in a git repository
if [ ! -d .git ]; then
    echo "❌ Error: Not a git repository"
    echo "   Run this script from the repository root"
    exit 1
fi

echo "Installing pre-commit hook..."

# Copy pre-commit hook
cp -f .git/hooks/pre-commit.sample .git/hooks/pre-commit 2>/dev/null || true
cat > .git/hooks/pre-commit << 'EOF'
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
EOF

# Make hook executable
chmod +x .git/hooks/pre-commit

echo "✅ Pre-commit hook installed successfully!"
echo ""
echo "The hook will automatically run before each commit."
echo "It will block commits that would fail CI."
echo ""
echo "To manually run validation:"
echo "  ./scripts/pre-commit.sh     (Linux/Mac)"
echo "  ./scripts/pre-commit.ps1    (Windows)"
echo ""
echo "To skip validation (NOT RECOMMENDED):"
echo "  git commit --no-verify"
echo ""
