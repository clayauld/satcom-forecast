# 🔧 Pre-commit Setup & Implementation Guide

This guide explains how to implement comprehensive code quality checks using pre-commit hooks for the SatCom Forecast project.

## 📋 Overview

Our pre-commit configuration performs the following checks:
- **🎨 Code Formatting**: Black (automatic formatting)
- **📦 Import Sorting**: isort (organized imports)
- **🔍 Code Quality**: Flake8 (PEP 8 compliance)
- **🏷️ Type Checking**: MyPy (type annotation validation)
- **🛡️ Security**: Bandit (security vulnerability scanning)
- **✨ General Quality**: Trailing whitespace, file endings, YAML validation

## 🚀 Quick Start

### 1. Install Pre-commit

```bash
# Install pre-commit globally
pip install pre-commit

# Or install in your virtual environment
source venv/bin/activate
pip install pre-commit
```

### 2. Install the Git Hooks

```bash
# Navigate to your project root
cd /path/to/satcom-forecast

# Install the pre-commit hooks
pre-commit install

# Optional: Install pre-push hooks for comprehensive testing
pre-commit install --hook-type pre-push
```

### 3. Test the Setup

```bash
# Run pre-commit on all files to test
pre-commit run --all-files

# Run specific hooks
pre-commit run black
pre-commit run flake8
```

## 📖 Detailed Setup Instructions

### Step 1: Project Setup

Ensure you have the following files in your project root:

```
satcom-forecast/
├── .pre-commit-config.yaml  ✅ (already configured)
├── custom_components/
├── tests/
├── requirements.txt
└── venv/
```

### Step 2: Install Dependencies

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install project dependencies
pip install -r requirements.txt

# Install pre-commit
pip install pre-commit

# Install additional tools for manual use
pip install black isort flake8 mypy bandit pytest pytest-cov
```

### Step 3: Configure Pre-commit

```bash
# Install hooks (this creates .git/hooks/pre-commit)
pre-commit install

# Optional: Also install pre-push hooks
pre-commit install --hook-type pre-push

# Update hooks to latest versions
pre-commit autoupdate
```

## 🎯 Usage Examples

### Automatic Usage (Recommended)

Once installed, pre-commit runs automatically:

```bash
# Make your changes
git add custom_components/satcom_forecast/sensor.py

# Commit (pre-commit runs automatically)
git commit -m "Update sensor configuration"
```

**Example Output:**
```
🔍 Running pre-commit checks...
black....................................................................Passed
isort....................................................................Passed
flake8...................................................................Passed
mypy.....................................................................Passed
trailing-whitespace...................................................... Passed
end-of-file-fixer........................................................Passed
check-yaml...............................................................Passed
bandit...................................................................Passed

✅ All checks passed! Proceeding with commit.
```

### Manual Usage

Run checks manually anytime:

```bash
# Run all hooks on staged files
pre-commit run

# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black
pre-commit run flake8

# Run hooks on specific files
pre-commit run --files custom_components/satcom_forecast/config_flow.py
```

### Fix Issues Automatically

Many hooks can auto-fix issues:

```bash
# Auto-fix formatting and imports
pre-commit run black --all-files
pre-commit run isort --all-files

# Then stage the changes
git add .
```

## 🛠️ Configuration Details

### Hook Configuration

Our `.pre-commit-config.yaml` includes:

#### **Black (Code Formatting)**
```yaml
- repo: https://github.com/psf/black
  rev: 23.12.1
  hooks:
    - id: black
      files: ^(custom_components|tests)/.*\.py$
```
- **What it does**: Automatically formats Python code
- **Auto-fix**: ✅ Yes
- **Scope**: Custom components and tests only

#### **isort (Import Sorting)**
```yaml
- repo: https://github.com/pycqa/isort
  rev: 5.13.2
  hooks:
    - id: isort
      args: ["--profile", "black"]
      files: ^(custom_components|tests)/.*\.py$
```
- **What it does**: Sorts and organizes import statements
- **Auto-fix**: ✅ Yes
- **Configuration**: Black-compatible profile

#### **Flake8 (Code Quality)**
```yaml
- repo: https://github.com/pycqa/flake8
  rev: 7.0.0
  hooks:
    - id: flake8
      args: ["--max-line-length=88", "--extend-ignore=E203,W503"]
      files: ^custom_components/satcom_forecast/.*\.py$
```
- **What it does**: Checks PEP 8 compliance and code quality
- **Auto-fix**: ❌ No (manual fixes required)
- **Configuration**: 88-char line limit, Black-compatible

#### **MyPy (Type Checking)**
```yaml
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.8.0
  hooks:
    - id: mypy
      args: ["--ignore-missing-imports", "--strict-optional"]
      files: ^custom_components/satcom_forecast/.*\.py$
      additional_dependencies: [types-aiofiles]
```
- **What it does**: Validates type annotations
- **Auto-fix**: ❌ No (add type hints manually)
- **Dependencies**: Includes type stubs for aiofiles

#### **Bandit (Security)**
```yaml
- repo: https://github.com/PyCQA/bandit
  rev: 1.7.6
  hooks:
    - id: bandit
      args: ["-r", "-f", "json"]
      files: ^custom_components/satcom_forecast/.*\.py$
      exclude: ^tests/
```
- **What it does**: Scans for security vulnerabilities
- **Auto-fix**: ❌ No (manual review required)
- **Scope**: Integration code only (excludes tests)

## 🔥 Common Workflows

### Daily Development

```bash
# 1. Make changes to your code
vim custom_components/satcom_forecast/sensor.py

# 2. Stage changes
git add .

# 3. Commit (pre-commit runs automatically)
git commit -m "Add new sensor functionality"

# 4. If pre-commit fails:
#    - Review the output
#    - Fix auto-fixable issues: git add . && git commit -m "..."
#    - Fix manual issues and repeat
```

### Before Opening a PR

```bash
# Run comprehensive checks
pre-commit run --all-files

# Run tests (if not included in pre-commit)
pytest tests/ -v --cov=custom_components/satcom_forecast

# If everything passes, push
git push origin feature-branch
```

### Updating Pre-commit

```bash
# Update to latest hook versions
pre-commit autoupdate

# Test the updates
pre-commit run --all-files

# Commit the updated config
git add .pre-commit-config.yaml
git commit -m "Update pre-commit hook versions"
```

## 🚨 Troubleshooting

### Common Issues and Solutions

#### **Hook Installation Fails**
```bash
# Error: "pre-commit command not found"
# Solution: Install pre-commit
pip install pre-commit

# Or globally
pipx install pre-commit
```

#### **MyPy Import Errors**
```bash
# Error: "Cannot find implementation or library stub"
# Solution: Install missing type stubs
pip install types-aiofiles types-requests

# Or add to .pre-commit-config.yaml additional_dependencies
```

#### **Flake8 Line Too Long**
```bash
# Error: "E501 line too long (95 > 88 characters)"
# Solution: Break long lines or use Black to auto-format
black custom_components/satcom_forecast/problem_file.py
```

#### **Import Sorting Conflicts**
```bash
# Error: isort and black disagree on formatting
# Solution: Ensure isort uses black profile
isort --profile=black custom_components/satcom_forecast/
```

#### **Skip Hooks Temporarily**
```bash
# Skip all hooks for emergency commit
git commit --no-verify -m "Emergency fix"

# Skip specific hooks
SKIP=mypy,bandit git commit -m "Skip heavy checks"
```

### Performance Issues

If pre-commit is slow:

```bash
# Run only on changed files (default)
pre-commit run

# Cache hook environments
export PRE_COMMIT_COLOR=never

# Update hooks for performance improvements
pre-commit autoupdate
```

## 🔄 Integration with GitHub Actions

Our pre-commit setup integrates with GitHub Actions:

### Local vs CI Checks

| Check | Pre-commit (Local) | GitHub Actions (CI) |
|-------|-------------------|-------------------|
| **Black** | ✅ Auto-fix | ✅ Validate only |
| **isort** | ✅ Auto-fix | ✅ Validate only |
| **Flake8** | ✅ Check | ✅ Check + Report |
| **MyPy** | ✅ Check | ✅ Check + Report |
| **Tests** | ❌ Optional | ✅ Full suite |
| **Coverage** | ❌ Optional | ✅ With reports |

### Pre-commit CI Service

Enable pre-commit.ci for automatic fixes:

1. Visit [pre-commit.ci](https://pre-commit.ci)
2. Connect your GitHub repository
3. Enable auto-fixes on PRs

## 📊 Advanced Configuration

### Custom Hook Stages

```yaml
# Add to .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest
        language: system
        pass_filenames: false
        stages: [pre-push]  # Only run on push
```

### Selective File Targeting

```yaml
hooks:
  - id: black
    files: ^custom_components/satcom_forecast/.*\.py$  # Only integration files
    exclude: ^tests/.*\.py$  # Exclude tests
```

### Environment Variables

```bash
# Skip all hooks
export SKIP=all

# Skip specific hooks
export SKIP=mypy,bandit

# Force color output
export PRE_COMMIT_COLOR=always
```

## 📚 Additional Resources

- **Pre-commit Documentation**: https://pre-commit.com/
- **Black Documentation**: https://black.readthedocs.io/
- **Flake8 Error Codes**: https://flake8.pycqa.org/en/latest/user/error-codes.html
- **MyPy Documentation**: https://mypy.readthedocs.io/
- **isort Documentation**: https://pycqa.github.io/isort/

## 🎯 Best Practices

1. **Run pre-commit before opening PRs**
2. **Update hooks regularly** with `pre-commit autoupdate`
3. **Don't skip hooks without good reason**
4. **Add type hints incrementally** to improve MyPy coverage
5. **Review Bandit warnings** for security implications
6. **Use auto-fix hooks** (Black, isort) to save time
7. **Keep commits focused** to make pre-commit faster

---

**💡 Pro Tip**: Set up your IDE to run Black and isort on save to catch formatting issues before committing!