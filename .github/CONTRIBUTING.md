# Contributing to PyRust

## 🚀 Before You Push - REQUIRED

**To avoid expensive CI failures, always run checks locally first:**

```bash
# Option 1: Full CI simulation (RECOMMENDED)
make ci-local

# Option 2: Quick check script
./scripts/ci-check.sh

# Option 3: Pre-commit hooks (automatic on git commit)
make pre-commit
```

**Why?** Each CI run costs money. Local checks are free and instant.

---

## 🛠️ Development Setup

### Initial Setup

```bash
# 1. Clone the repository
git clone https://github.com/USERNAME/pyrust.git
cd pyrust

# 2. One-command setup
make setup

# 3. Build and install
make build-dev
```

### Install Pre-commit Hooks (Recommended)

```bash
make pre-commit
```

Now checks run automatically on every `git commit`.

---

## 📝 Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Your Changes

Edit code in `src/` (Rust) or `python/` (Python).

### 3. Format Code

```bash
make format
```

### 4. Run Checks

```bash
make check
```

### 5. Run Tests

```bash
make test
```

### 6. Build Wheel

```bash
make build
```

---

## ✅ Pre-Push Checklist

Before pushing, **ALWAYS** run:

```bash
make ci-local
```

This runs:
- ✅ Rust format check
- ✅ Rust clippy (linter)
- ✅ Rust compilation
- ✅ Python lint (ruff)
- ✅ Python format check
- ✅ Wheel build
- ✅ All tests

**If it passes locally, it will pass in CI.**

---

## 🐛 Common Issues

### "Cargo fmt failed"

```bash
cargo fmt  # Auto-fix
```

### "Clippy warnings"

```bash
# See warnings
cargo clippy

# Fix common issues
cargo fix --allow-dirty
```

### "Python format failed"

```bash
ruff format python/  # Auto-fix
```

### "Python lint errors"

```bash
ruff check --fix python/  # Auto-fix
```

### "Tests failed"

```bash
# Run tests with verbose output
pytest python/tests/ -v -s

# Run specific test
pytest python/tests/test_dataframe.py::test_count -v
```

---

## 🔧 Makefile Commands

```bash
make help           # Show all commands
make check          # Run all checks
make format         # Auto-format code
make test           # Run tests
make build          # Build wheel
make build-dev      # Fast development build
make clean          # Clean artifacts
make ci-local       # Full CI simulation
make pre-commit     # Install pre-commit hooks
```

---

## 📊 Workflow

```
┌─────────────────────┐
│  1. Make changes    │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  2. make format     │  ← Auto-format
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  3. make check      │  ← Lint
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  4. make test       │  ← Test
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  5. make ci-local   │  ← Full CI check
└──────────┬──────────┘
           │
           ▼
    ✅ If passes
           │
┌──────────▼──────────┐
│  6. git commit      │
│     git push        │
└─────────────────────┘
```

---

## 🎯 Code Style

### Rust

- Follow `rustfmt` defaults
- All clippy warnings must be fixed
- Use descriptive variable names
- Add comments for complex logic

### Python

- Follow PEP 8 (enforced by ruff)
- Type hints encouraged
- Docstrings for public functions
- Keep functions under 50 lines

---

## 🧪 Testing

### Run All Tests

```bash
make test
```

### Run Specific Tests

```bash
pytest python/tests/test_dataframe.py -v
```

### Add New Tests

1. Create test file in `python/tests/`
2. Name it `test_*.py`
3. Use pytest fixtures
4. Run `make test`

---

## 📦 Pull Request Process

1. **Fork** the repository
2. **Create branch** from `main`
3. **Make changes** following this guide
4. **Run** `make ci-local` ✅
5. **Commit** with clear message
6. **Push** to your fork
7. **Open PR** with description

### PR Requirements

- ✅ All CI checks pass
- ✅ Tests included for new features
- ✅ Documentation updated
- ✅ No merge conflicts

---

## 💰 Cost Consideration

**Each CI run costs money!**

- ❌ Bad: Push without local checks → CI fails → Fix → Push again → Costs $$$
- ✅ Good: `make ci-local` → Fix locally → Push once → Saves money

**Be a good citizen: check locally first!**

---

## 🆘 Getting Help

- 📖 Read the [README](../README.md)
- 📖 Check [ARCHITECTURE](../ARCHITECTURE.md)
- 🐛 Search [Issues](https://github.com/USERNAME/pyrust/issues)
- 💬 Ask in [Discussions](https://github.com/USERNAME/pyrust/discussions)

---

## 📄 License

By contributing, you agree that your contributions will be licensed under Apache 2.0.
