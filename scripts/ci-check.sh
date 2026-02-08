#!/bin/bash
# Local CI check script - Run this before pushing to avoid CI failures
# Usage: ./scripts/ci-check.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   PyRust Local CI Check                ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo ""

# Track failures
FAILED=0

# Function to run a check
run_check() {
    local name="$1"
    local command="$2"

    echo -e "${YELLOW}➜${NC} $name..."
    if eval "$command" > /tmp/ci-check.log 2>&1; then
        echo -e "${GREEN}  ✓ Passed${NC}"
        return 0
    else
        echo -e "${RED}  ✗ Failed${NC}"
        echo -e "${RED}  Error details:${NC}"
        cat /tmp/ci-check.log | head -20
        FAILED=1
        return 1
    fi
}

# 1. Rust Format Check
run_check "Rust format check" "cargo fmt -- --check"

# 2. Rust Clippy
run_check "Rust clippy (linter)" "cargo clippy --all-targets --all-features -- -D warnings"

# 3. Rust Compilation
run_check "Rust compilation check" "cargo check --all-targets --all-features"

# 4. Python Lint
run_check "Python lint (ruff)" "ruff check python/"

# 5. Python Format Check
run_check "Python format check" "ruff format --check python/"

# 6. Build Wheel
run_check "Build wheel" "maturin build --release --out /tmp/pyrust-wheel"

# 7. Install and Test
echo -e "${YELLOW}➜${NC} Installing wheel and running tests..."
if pip install /tmp/pyrust-wheel/*.whl --force-reinstall --quiet && \
   pytest python/tests/ -v --tb=short > /tmp/ci-test.log 2>&1; then
    echo -e "${GREEN}  ✓ Tests passed${NC}"
else
    echo -e "${RED}  ✗ Tests failed${NC}"
    cat /tmp/ci-test.log | tail -30
    FAILED=1
fi

# Summary
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo -e "${GREEN}✓ Safe to push to GitHub${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "  git push origin main"
    exit 0
else
    echo -e "${RED}✗ Some checks failed${NC}"
    echo -e "${RED}✗ Fix errors before pushing${NC}"
    echo ""
    echo -e "${YELLOW}Run these commands to fix:${NC}"
    echo -e "  cargo fmt              # Auto-format Rust"
    echo -e "  ruff format python/    # Auto-format Python"
    echo -e "  ruff check --fix python/  # Auto-fix Python issues"
    exit 1
fi
