# Contributing to PyRust

Thank you for your interest in contributing to PyRust!

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Set up development environment** (see [Building](building.md))
4. **Create a branch** for your changes
5. **Make your changes** with tests
6. **Submit a pull request**

## Development Setup

See [Building](building.md) for detailed setup instructions.

Quick start:
```bash
git clone https://github.com/YOUR_USERNAME/PyRust.git
cd PyRust
python -m venv .venv
source .venv/bin/activate
pip install maturin pytest
maturin develop
```

## Code Style

### Rust
- Run `cargo fmt` before committing
- Run `cargo clippy` and fix warnings
- Follow Rust naming conventions

### Python
- Use `ruff format` for formatting
- Use `ruff check` for linting
- Follow PEP 8 style guide

## Testing

### Run All Tests
```bash
pytest python/tests/
```

### Run Specific Test File
```bash
pytest python/tests/test_dataframe.py -v
```

### Add Tests
- Add test files in `python/tests/`
- Test new features thoroughly
- Include edge cases

## Pre-commit Hooks

PyRust uses pre-commit hooks for quality:

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

Hooks check:
- Rust formatting (cargo fmt)
- Rust linting (clippy)
- Python formatting (ruff)
- Python linting (ruff)
- YAML syntax
- Trailing whitespace

## Pull Request Process

1. **Create an issue** describing the change
2. **Reference the issue** in your PR
3. **Include tests** for new features
4. **Update documentation** if needed
5. **Ensure CI passes** before requesting review

### PR Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Pre-commit hooks pass
- [ ] All tests pass
- [ ] No clippy warnings
- [ ] Commit messages are clear

## Areas to Contribute

See [ROADMAP.md](https://github.com/hadrien-chicault/PyRust/blob/main/ROADMAP.md) for priorities.

**High Impact:**
- Expression system (col(), lit())
- withColumn() implementation
- Column functions (string, math, date)
- Window functions

**Good First Issues:**
- Documentation improvements
- Example scripts
- Test coverage
- Bug fixes

## Code Review

Maintainers will review your PR and may:
- Request changes
- Ask questions
- Suggest improvements

Please be patient and responsive to feedback.

## License

By contributing, you agree that your contributions will be licensed under Apache 2.0.

## Questions?

- Open an [Issue](https://github.com/hadrien-chicault/PyRust/issues)
- Start a [Discussion](https://github.com/hadrien-chicault/PyRust/discussions)

Thank you for contributing! 🎉
