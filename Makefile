.PHONY: help check test build install clean lint format pre-commit

# Colors for output
GREEN  := \033[0;32m
YELLOW := \033[1;33m
BLUE   := \033[0;34m
NC     := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)PyRust Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

check: ## Run all checks (lint + compile check)
	@echo "$(YELLOW)Running Rust checks...$(NC)"
	@cargo fmt -- --check
	@cargo clippy --all-targets --all-features -- -D warnings
	@echo "$(YELLOW)Running Python checks...$(NC)"
	@ruff check python/
	@ruff format --check python/
	@echo "$(GREEN)✓ All checks passed!$(NC)"

lint: check ## Alias for check

format: ## Auto-format all code
	@echo "$(YELLOW)Formatting Rust code...$(NC)"
	@cargo fmt
	@echo "$(YELLOW)Formatting Python code...$(NC)"
	@ruff format python/
	@echo "$(GREEN)✓ Code formatted!$(NC)"

compile: ## Check that code compiles
	@echo "$(YELLOW)Checking Rust compilation...$(NC)"
	@cargo check --all-targets --all-features
	@echo "$(GREEN)✓ Compilation successful!$(NC)"

test: ## Run all tests
	@echo "$(YELLOW)Running Rust tests...$(NC)"
	@cargo test
	@echo "$(YELLOW)Running Python tests...$(NC)"
	@pytest python/tests/ -v
	@echo "$(GREEN)✓ All tests passed!$(NC)"

build: ## Build release wheel
	@echo "$(YELLOW)Building PyRust wheel...$(NC)"
	@maturin build --release --out dist
	@echo "$(GREEN)✓ Wheel built in dist/$(NC)"

build-dev: ## Build development version (faster)
	@echo "$(YELLOW)Building development version...$(NC)"
	@maturin develop
	@echo "$(GREEN)✓ Development build installed$(NC)"

install: build ## Build and install wheel
	@echo "$(YELLOW)Installing PyRust...$(NC)"
	@pip install dist/*.whl --force-reinstall
	@echo "$(GREEN)✓ PyRust installed!$(NC)"

clean: ## Clean build artifacts
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	@cargo clean
	@rm -rf target/ dist/ build/ *.egg-info
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)✓ Clean complete!$(NC)"

pre-commit: ## Install pre-commit hooks
	@echo "$(YELLOW)Installing pre-commit hooks...$(NC)"
	@pip install pre-commit
	@pre-commit install
	@echo "$(GREEN)✓ Pre-commit hooks installed!$(NC)"
	@echo "$(BLUE)Hooks will run automatically on git commit$(NC)"

pre-commit-run: ## Run pre-commit on all files
	@echo "$(YELLOW)Running pre-commit checks...$(NC)"
	@pre-commit run --all-files

ci-local: check compile test ## Run all CI checks locally (before push)
	@echo ""
	@echo "$(GREEN)╔════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║  ✓ All CI checks passed locally!      ║$(NC)"
	@echo "$(GREEN)║  Ready to push to GitHub              ║$(NC)"
	@echo "$(GREEN)╔════════════════════════════════════════╗$(NC)"
	@echo ""

setup: ## Initial project setup
	@echo "$(YELLOW)Setting up development environment...$(NC)"
	@pip install -U pip
	@pip install maturin pytest ruff pre-commit
	@pre-commit install
	@echo "$(GREEN)✓ Setup complete!$(NC)"
	@echo "$(BLUE)Run 'make build-dev' to build and install PyRust$(NC)"

example: ## Run the example
	@python examples/basic_operations.py
