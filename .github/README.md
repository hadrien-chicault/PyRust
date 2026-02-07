# PyRust CI/CD Documentation

## 📋 Workflows Overview

### 1. **ci.yml** - Main CI/CD Pipeline

Runs on every push and pull request.

**Jobs:**
- ✅ **lint-rust**: Rustfmt + Clippy
- ✅ **lint-python**: Ruff + MyPy
- ✅ **test**: Multi-platform testing (Ubuntu, macOS) × Python (3.8-3.12)
- ✅ **build-wheels**: Build wheels for all platforms
- ✅ **build-sdist**: Build source distribution
- ✅ **coverage**: Code coverage with Codecov
- ✅ **release**: Auto-publish on tags

### 2. **benchmark.yml** - Performance Benchmarks

Tracks performance over time.

**Features:**
- Runs pytest benchmarks
- Stores results for comparison
- Automatic trend detection

### 3. **docs.yml** - Documentation

Builds and deploys documentation.

**Features:**
- Rust docs (cargo doc)
- Python docs (MkDocs)
- Auto-deploy to GitHub Pages

---

## 🚀 Usage

### Running Locally

```bash
# Lint Rust
cargo fmt --check
cargo clippy -- -D warnings

# Lint Python
ruff check python/
ruff format --check python/

# Run tests
pytest python/tests/ -v

# Build wheels
maturin build --release
```

### Triggering Workflows

**Automatic:**
- Push to `master`, `main`, or `develop`
- Open a pull request

**Manual:**
- Go to Actions tab → Select workflow → Run workflow

### Creating a Release

```bash
# Tag a version
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0

# CI will automatically:
# 1. Build wheels for all platforms
# 2. Create GitHub release
# 3. Publish to PyPI (if PYPI_TOKEN is set)
```

---

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `.github/workflows/*.yml` | CI/CD workflows |
| `.github/dependabot.yml` | Dependency updates |
| `ruff.toml` | Python linter config |
| `.rustfmt.toml` | Rust formatter config |
| `.gitignore` | Git ignore patterns |

---

## 🔑 Required Secrets

Set these in **Settings → Secrets and variables → Actions**:

| Secret | Purpose | Required |
|--------|---------|----------|
| `PYPI_TOKEN` | Publish to PyPI | For releases |
| `CODECOV_TOKEN` | Upload coverage | Optional |

---

## 📊 Status Badges

Add to your README.md:

```markdown
![CI](https://github.com/USERNAME/pyrust/workflows/CI%2FCD%20Pipeline/badge.svg)
![Coverage](https://codecov.io/gh/USERNAME/pyrust/branch/master/graph/badge.svg)
```

---

## 🐛 Troubleshooting

### Build fails on macOS

```yaml
# Add this to the failing job
- name: Install dependencies (macOS)
  if: runner.os == 'macOS'
  run: brew install python@3.12
```

### Tests timeout

Increase timeout in workflow:

```yaml
- name: Run tests
  timeout-minutes: 30  # Default is 360
  run: pytest python/tests/
```

### Wheel build fails

Check Rust toolchain version:

```yaml
- name: Install Rust toolchain
  uses: dtolnay/rust-toolchain@stable
  with:
    targets: ${{ matrix.target }}
```

---

## 📈 Performance Matrix

Current CI runs test on:

| OS | Python Versions |
|----|-----------------|
| Ubuntu | 3.8, 3.9, 3.10, 3.11, 3.12 |
| macOS | 3.8, 3.11, 3.12 |
| Windows | (planned) |

---

## 🔄 Workflow Triggers

```yaml
on:
  push:
    branches: [ master, main, develop ]
  pull_request:
    branches: [ master, main, develop ]
  workflow_dispatch:  # Manual trigger
```

---

## 📝 Best Practices

1. ✅ Run linters locally before pushing
2. ✅ Keep CI fast (<10 minutes)
3. ✅ Cache dependencies aggressively
4. ✅ Test on multiple platforms
5. ✅ Use matrix builds for parallel testing

---

## 🆕 Adding New Jobs

Example: Add security audit

```yaml
security-audit:
  name: Security Audit
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: rustsec/audit-check@v1
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
```

---

For more information, see [GitHub Actions documentation](https://docs.github.com/en/actions).
