# 📦 AI Council - PyPI Publishing Guide

This guide walks you through publishing AI Council to PyPI (Python Package Index) so users can install it with `pip install ai-council`.

## 🎯 Overview

Once published to PyPI, users will be able to install AI Council with:
```bash
pip install ai-council
```

And use it in their code:
```python
from ai_council.factory import AICouncilFactory
from ai_council.core.models import ExecutionMode

factory = AICouncilFactory()
ai_council = factory.create_ai_council_sync()
```

## 📋 Prerequisites

### 1. PyPI Account Setup
- **Test PyPI Account**: Create at https://test.pypi.org/account/register/
- **Production PyPI Account**: Create at https://pypi.org/account/register/
- **API Tokens**: Generate API tokens for secure uploads

### 2. Required Tools
```bash
# Install publishing tools
pip install build twine

# Verify installation
python -m build --help
python -m twine --help
```

### 3. Authentication Setup
Create `~/.pypirc` file:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-production-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-token-here
```

## 🚀 Publishing Process

### Method 1: Automated Script (Recommended)

```bash
# Run the automated publishing script
python scripts/publish_to_pypi.py
```

The script will:
1. ✅ Check prerequisites
2. ✅ Validate package configuration
3. ✅ Run tests to ensure quality
4. ✅ Build the package
5. ✅ Upload to Test PyPI or Production PyPI

### Method 2: Manual Steps

#### Step 1: Prepare Package
```bash
# Ensure you're in the project root
cd /path/to/ai-council

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Run tests to ensure quality
python -m pytest tests/ -v
```

#### Step 2: Build Package
```bash
# Build source distribution and wheel
python -m build

# Verify build artifacts
ls dist/
# Should show: ai_council-1.0.0.tar.gz and ai_council-1.0.0-py3-none-any.whl
```

#### Step 3: Test Upload (Recommended First)
```bash
# Upload to Test PyPI first
python -m twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ ai-council

# Test the installation
python -c "from ai_council.factory import AICouncilFactory; print('✅ AI Council imported successfully!')"
```

#### Step 4: Production Upload
```bash
# Upload to Production PyPI
python -m twine upload dist/*

# Verify on PyPI
# Visit: https://pypi.org/project/ai-council/
```

## 📊 Package Information

### Package Details
- **Name**: `ai-council`
- **Version**: `1.0.0`
- **Description**: A production-grade multi-agent AI orchestration system
- **License**: MIT
- **Python Support**: 3.8+

### Installation Requirements
```bash
# Core dependencies (automatically installed)
pip install ai-council

# Development dependencies (optional)
pip install ai-council[dev]

# Test dependencies (optional)
pip install ai-council[test]
```

### Package Structure
```
ai-council/
├── ai_council/           # Main package
├── docs/                 # Documentation
├── examples/             # Usage examples
├── tests/                # Test suite
├── config/               # Configuration files
├── scripts/              # Utility scripts
├── README.md             # Package description
├── LICENSE               # MIT License
└── pyproject.toml        # Package configuration
```

## 🔍 Verification Steps

### After Publishing to Test PyPI
```bash
# Create fresh virtual environment
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
# or
test_env\Scripts\activate     # Windows

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ ai-council

# Test basic functionality
python -c "
from ai_council.factory import AICouncilFactory
from ai_council.core.models import ExecutionMode
print('✅ AI Council Test PyPI installation successful!')
"
```

### After Publishing to Production PyPI
```bash
# Create fresh virtual environment
python -m venv prod_test_env
source prod_test_env/bin/activate

# Install from Production PyPI
pip install ai-council

# Run comprehensive test
python -c "
from ai_council.factory import AICouncilFactory
from ai_council.core.models import ExecutionMode

factory = AICouncilFactory()
ai_council = factory.create_ai_council_sync()
print('✅ AI Council Production PyPI installation successful!')
print(f'Available execution modes: {list(ExecutionMode)}')
"
```

## 📈 Version Management

### Semantic Versioning
AI Council follows semantic versioning (semver):
- **Major** (1.x.x): Breaking changes
- **Minor** (x.1.x): New features, backward compatible
- **Patch** (x.x.1): Bug fixes, backward compatible

### Updating Version
```bash
# Update version in pyproject.toml
# [project]
# version = "1.1.0"  # New version

# Rebuild and republish
python -m build
python -m twine upload dist/*
```

## 🛡️ Security Best Practices

### API Token Security
- ✅ Use API tokens instead of passwords
- ✅ Store tokens securely in `~/.pypirc`
- ✅ Never commit tokens to version control
- ✅ Rotate tokens regularly

### Package Security
- ✅ Run security scans before publishing
- ✅ Keep dependencies updated
- ✅ Sign releases with GPG (optional)
- ✅ Monitor for vulnerabilities

## 🎯 Post-Publication Tasks

### 1. Update Documentation
- Update installation instructions in README.md
- Add PyPI badge to README.md
- Update documentation links

### 2. Announce Release
- Create GitHub release with changelog
- Update project website/blog
- Announce on social media/forums

### 3. Monitor Usage
- Track download statistics on PyPI
- Monitor GitHub issues and discussions
- Collect user feedback

## 🔧 Troubleshooting

### Common Issues

#### "Package already exists" Error
```bash
# Increment version in pyproject.toml and rebuild
# You cannot overwrite existing versions on PyPI
```

#### Authentication Errors
```bash
# Verify API token in ~/.pypirc
# Ensure token has correct permissions
```

#### Build Errors
```bash
# Check pyproject.toml syntax
# Ensure all required files are present
# Run tests to catch issues early
```

#### Import Errors After Installation
```bash
# Check package structure in pyproject.toml
# Verify __init__.py files are present
# Test in clean virtual environment
```

## 📊 Success Metrics

### Publication Success Indicators
- ✅ Package appears on PyPI: https://pypi.org/project/ai-council/
- ✅ Installation works: `pip install ai-council`
- ✅ Import works: `from ai_council.factory import AICouncilFactory`
- ✅ Basic functionality works
- ✅ Documentation links are accessible

### Usage Growth Metrics
- Download statistics on PyPI
- GitHub stars and forks
- Community contributions
- Issue reports and feature requests

## 🎉 Congratulations!

Once published, AI Council will be available to the entire Python community! Users worldwide will be able to:

```bash
# Install AI Council
pip install ai-council

# Use in their projects
from ai_council.factory import AICouncilFactory
from ai_council.core.models import ExecutionMode

# Build amazing multi-agent AI applications
factory = AICouncilFactory()
ai_council = factory.create_ai_council_sync()
response = ai_council.process_request_sync(
    "Your question here",
    ExecutionMode.BALANCED
)
```

**AI Council is now part of the official Python ecosystem!** 🚀