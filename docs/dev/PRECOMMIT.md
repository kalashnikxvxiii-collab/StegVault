# Pre-Commit Validation System

This document describes StegVault's comprehensive pre-commit validation system that **prevents CI failures** by replicating all GitHub Actions workflows locally.

## Quick Start

### Installation

**Linux/Mac:**
```bash
bash install-hooks.sh
```

**Windows:**
```powershell
.\install-hooks.ps1
```

This installs a git pre-commit hook that automatically validates your changes before each commit.

### Manual Validation

You can also run validation manually:

**Linux/Mac:**
```bash
bash pre-commit.sh
```

**Windows:**
```powershell
.\pre-commit.ps1
```

## What Gets Validated

The pre-commit system replicates **ALL** GitHub Actions workflows:

### 1. Code Formatting (Black) ✅ BLOCKING
- **What**: Checks Python code formatting with Black
- **How**: `black --check stegvault tests`
- **Auto-fix**: Yes - automatically formats if needed
- **Blocks commit**: Only if formatting fails entirely
- **CI equivalent**: Code Quality workflow

### 2. Test Suite with Coverage ✅ BLOCKING
- **What**: Runs all 1070 tests with timeout protection
- **How**: `pytest --cov=stegvault --cov-report=xml --cov-report=term --timeout=60`
- **Auto-fix**: No - you must fix failing tests
- **Blocks commit**: Yes if tests fail
- **CI equivalent**: CI workflow (Python 3.9-3.14)

### 3. Type Checking (mypy) ⚠️ NON-BLOCKING
- **What**: Static type checking with mypy
- **How**: `mypy stegvault`
- **Auto-fix**: No
- **Blocks commit**: No (continue-on-error in CI)
- **CI equivalent**: Code Quality workflow

### 4. Security Scan (Bandit) ⚠️ NON-BLOCKING
- **What**: Security vulnerability scanning
- **How**: `bandit -r stegvault`
- **Auto-fix**: No
- **Blocks commit**: No (warnings only)
- **CI equivalent**: Code Quality workflow

### 5. Dependency Vulnerabilities (Safety) ⚠️ NON-BLOCKING
- **What**: Checks for vulnerable dependencies
- **How**: `safety check`
- **Auto-fix**: No
- **Blocks commit**: No (continue-on-error in CI)
- **CI equivalent**: Security Scan workflow

## Installation Requirements

### Required (must be installed)
```bash
pip install pytest pytest-cov pytest-timeout black
```

### Optional (but recommended)
```bash
pip install mypy bandit safety
```

Missing optional tools will be skipped with a warning.

## Usage Examples

### Normal Workflow
```bash
# 1. Make your changes
vim stegvault/vault/core.py

# 2. Add files
git add .

# 3. Commit (hook runs automatically)
git commit -m "fix: improve vault encryption"

# If validation passes:
# ✅ ALL PRE-COMMIT CHECKS PASSED!
# Commit proceeds normally

# If validation fails:
# ❌ PRE-COMMIT VALIDATION FAILED
# Commit is BLOCKED
```

### Manual Pre-Commit Run
```bash
# Run before committing to catch issues early
./pre-commit.sh

# Fix any issues
black stegvault tests
pytest

# Then commit
git add .
git commit -m "fix: improve vault encryption"
```

### Skipping Validation (NOT RECOMMENDED)
```bash
# Only use in emergencies!
git commit --no-verify -m "emergency hotfix"

# ⚠️ WARNING: CI will still fail on push!
```

## What Happens on Failure

### Black Formatting Failure
```
[!] Code formatting issues detected
    Applying automatic formatting...
[✓] Code formatted successfully

    ⚠️  WARNING: Files were modified by Black formatter
    You need to stage the changes and commit again:
    git add -A
    git commit --amend --no-edit
```

**Action**: Re-stage the formatted files and commit again.

### Test Failure
```
[✗] Tests failed

FAILED tests/unit/test_vault.py::test_vault_encryption - AssertionError
```

**Action**: Fix the failing test, then commit again.

### Security Issues (Non-blocking)
```
[!] Security issues detected (review output above)
Run issued: Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
```

**Action**: Review and fix if necessary. Won't block commit.

## CI/CD Integration

This pre-commit system **exactly replicates** GitHub Actions:

| Check | Pre-Commit | GitHub Actions | Blocking |
|-------|------------|----------------|----------|
| Black formatting | `black --check` | Code Quality workflow | ✅ Yes |
| Tests with coverage | `pytest --timeout=60` | CI workflow | ✅ Yes |
| Type checking | `mypy stegvault` | Code Quality workflow | ⚠️ No |
| Security scan | `bandit -r stegvault` | Code Quality workflow | ⚠️ No |
| Dependency scan | `safety check` | Security workflow | ⚠️ No |

**If pre-commit passes, CI will pass.**

## Troubleshooting

### Hook not running automatically
```bash
# Reinstall hook
bash install-hooks.sh

# Verify hook exists
ls -la .git/hooks/pre-commit
```

### "pytest-timeout not found"
```bash
pip install pytest-timeout
```

### "command not found: black"
```bash
pip install black
```

### Tests taking too long (timeout)
```bash
# Individual test timeout is 60s
# Check for hanging tests:
pytest -v --timeout=10
```

### Permission denied (Linux/Mac)
```bash
chmod +x pre-commit.sh install-hooks.sh
```

## Advanced Configuration

### Disable specific checks

Edit `pre-commit.sh` or `pre-commit.ps1` and comment out unwanted sections:

```bash
# 4. SECURITY SCAN (Code Quality Workflow)
# echo "=== 4/5: Security Scan (Bandit) ==="
# ... (comment out entire section)
```

### Custom pytest arguments

Edit the pytest command in the script:

```bash
# Add -k filter
pytest --cov=stegvault --timeout=60 -k "not slow"

# Add -x (stop on first failure)
pytest --cov=stegvault --timeout=60 -x
```

## Best Practices

1. **Always run pre-commit before pushing**
   ```bash
   ./pre-commit.sh && git push
   ```

2. **Install hooks immediately after cloning**
   ```bash
   git clone <repo>
   cd stegvault
   bash install-hooks.sh
   ```

3. **Never use --no-verify unless absolutely necessary**
   - CI will fail anyway
   - You'll waste time waiting for CI

4. **Fix issues locally, not in CI**
   - CI runs on every push
   - Local validation is instant

5. **Run full validation before creating PRs**
   ```bash
   ./pre-commit.sh
   git push origin feature-branch
   gh pr create
   ```

## CI Workflow Details

### CI Workflow (ci.yml)
- Runs on: push, pull_request (main, beta branches)
- Python versions: 3.9, 3.10, 3.11, 3.12, 3.13, 3.14
- Experimental: 3.13, 3.14 (can fail without blocking)
- Coverage: Uploaded to Codecov on Python 3.11

### Code Quality Workflow (quality.yml)
- Runs on: push, pull_request (main, beta branches)
- Python version: 3.11
- Blocking: Black formatting only
- Non-blocking: mypy, bandit

### Security Workflow (security.yml)
- Runs on: push, pull_request (main), weekly schedule
- CodeQL analysis: Python security patterns
- Safety check: Dependency vulnerabilities
- Non-blocking: All checks

## Summary

- **Pre-commit = Local CI**
- **Prevents wasted time on failing CI**
- **Automatic installation with install-hooks script**
- **Manual validation available anytime**
- **Exact parity with GitHub Actions**
- **Smart auto-formatting for Black**
- **Clear failure messages**

Run `./pre-commit.sh` before every push!
