# Release Process

## 🚀 Creating a Release

### Automated Method (Recommended)

Use the provided script:

```bash
# Create release for version 0.2.0
./scripts/create-release.sh 0.2.0
```

The script will:
1. ✅ Update version in `Cargo.toml`, `pyproject.toml`, `__init__.py`
2. ✅ Create a commit with version bump
3. ✅ Create a git tag (e.g., `v0.2.0`)
4. ✅ Show you next steps

Then push:
```bash
git push origin main
git push origin v0.2.0
```

### Manual Method

#### 1. Update Version Numbers

Edit these files:

**Cargo.toml:**
```toml
[package]
version = "0.2.0"
```

**pyproject.toml:**
```toml
[project]
version = "0.2.0"
```

**python/pyrust/__init__.py:**
```python
__version__ = "0.2.0"
```

#### 2. Commit and Tag

```bash
git add Cargo.toml pyproject.toml python/pyrust/__init__.py
git commit -m "chore: bump version to 0.2.0"
git tag -a v0.2.0 -m "Release version 0.2.0"
```

#### 3. Push

```bash
git push origin main
git push origin v0.2.0
```

---

## 🤖 What Happens Automatically

When you push a tag starting with `v`, GitHub Actions will:

### 1. Run Tests ✅
- Lint Rust code
- Lint Python code
- Run tests on multiple platforms
- Generate coverage report

### 2. Build Packages 📦
- **Linux wheels** (x86_64)
- **macOS wheels** (x86_64 + ARM64)
- **Windows wheels** (x86_64)
- **Source distribution** (sdist)

### 3. Create GitHub Release 🎉
- Create a release with tag name
- Upload all wheels and sdist
- Generate release notes automatically
- Add installation instructions

### 4. Publish to PyPI 🌐
- Upload wheels to PyPI (if `PYPI_TOKEN` is configured)
- Upload source distribution
- Make package installable via `pip install pyrust`

---

## 📋 Release Checklist

Before creating a release:

- [ ] All tests passing on main branch
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if exists)
- [ ] Version bumped in all files
- [ ] No uncommitted changes
- [ ] Reviewed recent commits

---

## 🏷️ Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **Major** (1.0.0): Breaking changes
- **Minor** (0.2.0): New features, backwards compatible
- **Patch** (0.1.1): Bug fixes

### Pre-release Versions

- **Alpha**: `0.2.0-alpha.1` (early testing)
- **Beta**: `0.2.0-beta.1` (feature complete, testing)
- **RC**: `0.2.0-rc.1` (release candidate)

Pre-releases are marked as "pre-release" in GitHub and **not** published to PyPI.

---

## 📦 Release Artifacts

Each release includes:

### Wheels (Binary)
```
pyrust-0.2.0-cp38-cp38-manylinux_2_34_x86_64.whl
pyrust-0.2.0-cp39-cp39-manylinux_2_34_x86_64.whl
pyrust-0.2.0-cp310-cp310-manylinux_2_34_x86_64.whl
pyrust-0.2.0-cp311-cp311-manylinux_2_34_x86_64.whl
pyrust-0.2.0-cp312-cp312-manylinux_2_34_x86_64.whl
pyrust-0.2.0-cp312-cp312-macosx_10_12_x86_64.whl
pyrust-0.2.0-cp312-cp312-macosx_11_0_arm64.whl
pyrust-0.2.0-cp312-cp312-win_amd64.whl
```

### Source Distribution
```
pyrust-0.2.0.tar.gz
```

---

## 🔧 Configuration Required

### GitHub Secrets

Set in **Settings → Secrets and variables → Actions**:

| Secret | Required | Purpose |
|--------|----------|---------|
| `PYPI_TOKEN` | ⚠️ Optional | Publish to PyPI |
| `CODECOV_TOKEN` | ✅ Optional | Code coverage |

### Getting PyPI Token

1. Create account on https://pypi.org
2. Go to https://pypi.org/manage/account/token/
3. Create token with scope "Upload packages"
4. Add to GitHub Secrets as `PYPI_TOKEN`

---

## 🐛 Troubleshooting

### Release Failed

Check GitHub Actions logs:
- Go to Actions tab
- Click on failed workflow
- Check each job for errors

### PyPI Upload Failed

```bash
# Manually upload
pip install maturin
maturin build --release
maturin upload target/wheels/*.whl
```

### Tag Already Exists

Delete and recreate:
```bash
git tag -d v0.2.0
git push origin :refs/tags/v0.2.0
# Fix and recreate tag
```

---

## 📊 Release Metrics

After release, check:

- [ ] GitHub Release created
- [ ] All wheels uploaded (8+ files)
- [ ] PyPI package available
- [ ] Installation works: `pip install pyrust==0.2.0`
- [ ] Documentation accessible

---

## 🎯 Release Schedule (Suggested)

- **Patch releases**: As needed for bugs
- **Minor releases**: Monthly or when features ready
- **Major releases**: Quarterly or for breaking changes

---

## 📞 Need Help?

- Check [CI/CD README](.github/README.md)
- Review failed Actions logs
- Open an issue on GitHub

---

## Example: Complete Release Process

```bash
# 1. Make sure you're up to date
git checkout main
git pull

# 2. Create release
./scripts/create-release.sh 0.2.0

# 3. Review changes
git log -1
git show v0.2.0

# 4. Push
git push origin main
git push origin v0.2.0

# 5. Monitor CI
# Go to: https://github.com/USERNAME/pyrust/actions

# 6. Verify release
# Go to: https://github.com/USERNAME/pyrust/releases

# 7. Test installation
pip install pyrust==0.2.0

# 8. Celebrate! 🎉
```

---

**Tip**: Test the release process on a fork first!
