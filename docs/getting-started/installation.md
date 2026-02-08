# Installation

This guide will help you install PyRust on your system.

## Requirements

- **Python**: 3.8 or higher
- **Rust**: 1.70 or higher (only for building from source)
- **Operating System**: Linux, macOS, or Windows

## Installation Methods

### Via pip (Recommended)

Once PyRust is published to PyPI, installation is simple:

```bash
pip install pyrust
```

### From GitHub Release

Download a pre-built wheel from the [releases page](https://github.com/hadrien-chicault/PyRust/releases):

```bash
# Linux x86_64
pip install https://github.com/hadrien-chicault/PyRust/releases/download/v0.1.0/pyrust-0.1.0-cp312-cp312-linux_x86_64.whl

# macOS x86_64
pip install https://github.com/hadrien-chicault/PyRust/releases/download/v0.1.0/pyrust-0.1.0-cp312-cp312-macosx_x86_64.whl

# macOS ARM64 (Apple Silicon)
pip install https://github.com/hadrien-chicault/PyRust/releases/download/v0.1.0/pyrust-0.1.0-cp312-cp312-macosx_arm64.whl

# Windows x86_64
pip install https://github.com/hadrien-chicault/PyRust/releases/download/v0.1.0/pyrust-0.1.0-cp312-cp312-win_amd64.whl
```

### From Source

Building from source requires Rust and Maturin:

```bash
# Clone the repository
git clone https://github.com/hadrien-chicault/PyRust.git
cd PyRust

# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install maturin
pip install maturin

# Build and install
maturin develop --release
```

### Using UV (Fast Python Package Manager)

[UV](https://github.com/astral-sh/uv) is a fast Python package installer:

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install PyRust
uv pip install pyrust

# Or build from source
git clone https://github.com/hadrien-chicault/PyRust.git
cd PyRust
uv tool install maturin
maturin develop --release
```

## Verify Installation

Test that PyRust is correctly installed:

```python
from pyrust import SparkSession

# Create a session
spark = SparkSession.builder() \
    .appName("TestApp") \
    .getOrCreate()

print(f"PyRust installed successfully!")
print(f"App name: {spark.appName}")
```

Expected output:
```
PyRust installed successfully!
App name: TestApp
```

## Optional Dependencies

### For Development

If you're contributing to PyRust, install development dependencies:

```bash
pip install pyrust[dev]
```

This includes:
- `pytest` - Testing framework
- `pytest-benchmark` - Performance benchmarking
- `pandas` - For comparison tests
- `maturin` - Build tool

### For Data Analysis

Additional libraries you might want:

```bash
# Arrow for data interchange
pip install pyarrow

# Pandas for comparison
pip install pandas

# Jupyter for interactive analysis
pip install jupyter
```

## Platform-Specific Notes

### Linux

On Linux, you may need to install additional system dependencies:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install build-essential python3-dev

# Fedora/RHEL
sudo dnf install gcc python3-devel
```

### macOS

On macOS, ensure Xcode Command Line Tools are installed:

```bash
xcode-select --install
```

### Windows

On Windows, install the Visual C++ Build Tools:

1. Download from [Visual Studio Downloads](https://visualstudio.microsoft.com/downloads/)
2. Install "Desktop development with C++"

## Troubleshooting

### Import Error

If you get `ImportError: No module named '_pyrust'`:

```bash
# Reinstall with --force-reinstall
pip install --force-reinstall pyrust
```

### Permission Denied

On Linux/macOS, if you get permission errors:

```bash
# Install for current user only
pip install --user pyrust
```

### Rust Version Too Old

If building from source fails with Rust version errors:

```bash
# Update Rust
rustup update stable
```

## Next Steps

Now that PyRust is installed, check out:

- [Quick Start Tutorial](quickstart.md) - Write your first PyRust program
- [Basic Operations](basic-operations.md) - Learn common data operations
- [API Reference](../api/dataframe.md) - Explore the full API
