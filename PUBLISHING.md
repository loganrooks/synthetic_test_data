# Publishing Guide

This document describes how to publish `synth_data_gen` to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts on both [TestPyPI](https://test.pypi.org/) and [PyPI](https://pypi.org/)
2. **API Tokens**: Generate API tokens for both services
3. **Build Tools**: Install build tools: `pip install build twine`

## Manual Publishing

### 1. Update Version

Edit `pyproject.toml` and update the version:

```toml
[project]
version = "0.1.1"  # Increment appropriately
```

### 2. Update CHANGELOG

Add release notes to `CHANGELOG.md`:

```markdown
## [0.1.1] - YYYY-MM-DD

### Added
- New feature...

### Fixed
- Bug fix...
```

### 3. Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build source distribution and wheel
python -m build
```

This creates:
- `dist/synth_data_gen-0.1.1.tar.gz` (source distribution)
- `dist/synth_data_gen-0.1.1-py3-none-any.whl` (wheel)

### 4. Test with TestPyPI

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ synth_data_gen
```

### 5. Publish to PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*
```

## Automated Publishing (GitHub Actions)

The repository includes a GitHub Actions workflow for automated publishing.

### Setup

1. Add PyPI API token as a GitHub secret:
   - Go to repository Settings → Secrets → Actions
   - Add `PYPI_API_TOKEN` with your PyPI token

2. For TestPyPI (optional):
   - Add `TEST_PYPI_API_TOKEN`

### Triggering a Release

1. Create and push a version tag:

```bash
git tag v0.1.1
git push origin v0.1.1
```

2. The workflow will automatically:
   - Build the package
   - Run tests
   - Publish to PyPI

### Release Workflow

The `.github/workflows/publish.yml` workflow:

```yaml
on:
  push:
    tags:
      - 'v*'
```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0): Incompatible API changes
- **MINOR** (0.1.0): New functionality, backwards compatible
- **PATCH** (0.0.1): Bug fixes, backwards compatible

## Pre-release Checklist

- [ ] All tests pass: `pytest`
- [ ] Type checking passes: `mypy synth_data_gen`
- [ ] Linting passes: `ruff check .`
- [ ] CHANGELOG updated
- [ ] Version bumped in `pyproject.toml`
- [ ] Documentation updated
- [ ] Git tag created

## Troubleshooting

### "Package already exists"

You cannot overwrite existing versions on PyPI. Increment the version number.

### "Invalid token"

Ensure your API token:
- Has upload permissions
- Is scoped to the correct project (or all projects)
- Is entered correctly without extra whitespace

### Build Errors

```bash
# Ensure build tools are up to date
pip install --upgrade build twine setuptools wheel
```
