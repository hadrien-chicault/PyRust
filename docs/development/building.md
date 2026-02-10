# Building PyRust

Instructions for building PyRust from source.

## Prerequisites

- **Python 3.8+**
- **Rust 1.70+**
- **Git**

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/hadrien-chicault/PyRust.git
cd PyRust
```

### 2. Install Rust (if needed)

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

### 3. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install maturin pytest ruff
```

### 5. Build PyRust

#### Development Build

```bash
maturin develop
```

#### Release Build (faster)

```bash
maturin develop --release
```

## Running Tests

```bash
# All tests
pytest python/tests/ -v

# Specific test file
pytest python/tests/test_dataframe.py

# With coverage
pytest python/tests/ --cov=pyrust
```

## Code Quality

### Format Code

```bash
# Rust
cargo fmt

# Python
ruff format python/
```

### Lint Code

```bash
# Rust
cargo clippy

# Python
ruff check python/
```

### Run All Checks

```bash
pre-commit run --all-files
```

## Documentation

### Build Docs Locally

```bash
pip install mkdocs mkdocs-material mkdocstrings[python]
mkdocs serve
```

View at: http://127.0.0.1:8000

### Generate Rust Docs

```bash
cargo doc --open
```

## Development Workflow

1. Make changes to Rust code in `src/`
2. Rebuild: `maturin develop`
3. Test: `pytest python/tests/`
4. Repeat

## Troubleshooting

### "No module named 'pyrust'"

Run `maturin develop` to build and install.

### Rust compilation errors

Check Rust version:
```bash
rustc --version  # Should be 1.70+
```

Update if needed:
```bash
rustup update
```

### Import errors after changes

Rebuild and reinstall:
```bash
maturin develop --release
```

### Tests fail after changes

1. Check if code compiles: `cargo build`
2. Rebuild Python module: `maturin develop`
3. Run specific failing test: `pytest path/to/test.py::test_name -v`

## IDE Setup

### VS Code

Recommended extensions:
- rust-analyzer
- Python
- Ruff

### PyCharm

- Enable Rust plugin
- Configure Python interpreter to use `.venv`

## See Also

- [Contributing Guide](contributing.md)
- [Testing Guide](testing.md)
- [Local CI](local-ci.md)
