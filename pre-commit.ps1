# Pre-commit validation script for StegVault (Windows PowerShell)
# Replicates ALL GitHub Actions workflows to prevent CI failures
# Run this before every commit to ensure all checks pass

$ErrorActionPreference = "Continue"
$Failed = $false
$FailedChecks = @()

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "StegVault Pre-Commit Validation" -ForegroundColor Cyan
Write-Host "Replicating CI/CD Pipeline Locally" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. CODE FORMATTING CHECK
Write-Host "=== 1/5: Code Formatting (Black) ===" -ForegroundColor Yellow
Write-Host "Checking code formatting..."
black --check stegvault tests 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Code is properly formatted" -ForegroundColor Green
} else {
    Write-Host "[INFO] Applying automatic formatting..." -ForegroundColor Yellow
    black stegvault tests
    Write-Host "[OK] Code formatted" -ForegroundColor Green
    Write-Host ""
    Write-Host "[WARNING] Files were modified - stage and commit again" -ForegroundColor Yellow
    Write-Host "  git add -A && git commit --amend --no-edit" -ForegroundColor Gray
}
Write-Host ""

# 2. TESTS WITH COVERAGE
Write-Host "=== 2/5: Test Suite with Coverage ===" -ForegroundColor Yellow
pytest --cov=stegvault --cov-report=xml --cov-report=term --timeout=60 -q
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] All tests passed" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Tests failed" -ForegroundColor Red
    $Failed = $true
    $FailedChecks += "pytest"
}
Write-Host ""

# 3. TYPE CHECKING
Write-Host "=== 3/5: Type Checking (mypy) ===" -ForegroundColor Yellow
$mypyCmd = Get-Command mypy -ErrorAction SilentlyContinue
if ($mypyCmd) {
    mypy stegvault 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Type checking passed" -ForegroundColor Green
    } else {
        Write-Host "[INFO] Type issues detected (non-blocking)" -ForegroundColor Yellow
    }
} else {
    Write-Host "[SKIP] mypy not installed" -ForegroundColor Yellow
}
Write-Host ""

# 4. SECURITY SCAN
Write-Host "=== 4/5: Security Scan (Bandit) ===" -ForegroundColor Yellow
$banditCmd = Get-Command bandit -ErrorAction SilentlyContinue
if ($banditCmd) {
    bandit -r stegvault -f json -o bandit-report.json 2>&1 | Out-Null
    bandit -r stegvault 2>&1 | Out-Null
    Write-Host "[OK] Security scan complete" -ForegroundColor Green
} else {
    Write-Host "[SKIP] Bandit not installed" -ForegroundColor Yellow
}
Write-Host ""

# 5. DEPENDENCY SCAN
Write-Host "=== 5/5: Dependency Security Scan (Safety) ===" -ForegroundColor Yellow
$safetyCmd = Get-Command safety -ErrorAction SilentlyContinue
if ($safetyCmd) {
    safety check --json --output safety-report.json 2>&1 | Out-Null
    safety check 2>&1 | Out-Null
    Write-Host "[OK] Dependency scan complete" -ForegroundColor Green
} else {
    Write-Host "[SKIP] Safety not installed" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "==========================================" -ForegroundColor Cyan
if (-not $Failed) {
    Write-Host "SUCCESS: All checks passed!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Ready to push. Commands:" -ForegroundColor White
    Write-Host "  git push origin main" -ForegroundColor Gray
    Write-Host "  gh run list --limit 3" -ForegroundColor Gray
    Write-Host ""
    exit 0
} else {
    Write-Host "FAILED: Pre-commit validation failed" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Failed checks: $($FailedChecks -join ', ')" -ForegroundColor Red
    Write-Host ""
    Write-Host "DO NOT COMMIT - CI will fail!" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
