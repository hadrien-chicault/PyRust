# Local CI Checks

Run the same checks locally that run in CI/CD.

## Quick Start

```bash
# Install pre-commit hooks
pre-commit install

# Run all checks
pre-commit run --all-files
```

## Individual Checks

### Rust Format

```bash
cargo fmt --check
```

Fix issues:
```bash
cargo fmt
```

### Rust Lint (Clippy)

```bash
cargo clippy -- -D warnings
```

### Rust Compilation

```bash
cargo build --release
```

### Python Format

```bash
ruff format --check python/
```

Fix issues:
```bash
ruff format python/
```

### Python Lint

```bash
ruff check python/
```

### Run Tests

```bash
pytest python/tests/ -v
```

## Pre-commit Hooks

The `.pre-commit-config.yaml` file defines hooks that run automatically.

### What Gets Checked

- ✅ Rust formatting (cargo fmt)
- ✅ Rust linting (clippy)
- ✅ Rust compilation
- ✅ Python formatting (ruff)
- ✅ Python linting (ruff)
- ✅ Trailing whitespace
- ✅ End of file newlines
- ✅ YAML syntax
- ✅ Large files check
- ✅ Mixed line endings
- ✅ Markdown linting

### Manual Run

```bash
# All files
pre-commit run --all-files

# Only staged files
pre-commit run

# Specific hook
pre-commit run cargo-fmt
```

## Full CI Simulation

Run everything CI runs:

```bash
# Format check
cargo fmt --check
ruff format --check python/

# Lint
cargo clippy -- -D warnings
ruff check python/

# Build
cargo build --release

# Test
pytest python/tests/ -v

# Documentation
mkdocs build
```

## Cost Savings

Running checks locally before pushing:
- ✅ Faster feedback (seconds vs minutes)
- ✅ Reduces CI/CD costs
- ✅ Catches issues early

## Troubleshooting

### Pre-commit fails

1. Check error message
2. Fix the issue
3. Run again: `pre-commit run --all-files`

### Hooks not running

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install
```

### Slow hooks

```bash
# Update hooks to latest version
pre-commit autoupdate
```

## See Also

- [Building Guide](building.md)
- [Testing Guide](testing.md)
- [Contributing Guide](contributing.md)
