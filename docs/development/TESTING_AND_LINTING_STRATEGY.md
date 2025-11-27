# Testing and Linting Strategy

This document outlines the testing and linting strategy for the SatCom Forecast integration. It explains the tools we use, how they are configured, and the reasoning behind our choices.

## Overview

Our strategy aims to ensure:
1.  **Code Quality**: Maintaining a consistent, readable, and error-free codebase.
2.  **Robustness**: Verifying that the integration functions correctly under various conditions.
3.  **Security**: Identifying and preventing potential security vulnerabilities.
4.  **Home Assistant Compliance**: Adhering to Home Assistant integration development standards.

## Tooling Stack

We use a combination of standard Python tools and Home Assistant-specific practices. While Home Assistant Core has migrated to `ruff` for linting and formatting, we currently employ the "Classic Stack" (Black, Flake8, Isort) which provides equivalent guarantees and is widely understood.

### 1. Code Formatting (`black`)

*   **Tool**: [Black](https://black.readthedocs.io/)
*   **Reasoning**: Black is the uncompromising Python code formatter. It ensures deterministic formatting, eliminating debates over style. It produces PEP 8 compliant code.
*   **Configuration**:
    *   Line length: **88** characters (standard Black default).
    *   Target Python version: 3.8+.
    *   Configured in: `pyproject.toml`.

### 2. Import Sorting (`isort`)

*   **Tool**: [isort](https://pycqa.github.io/isort/)
*   **Reasoning**: Consistent import sorting makes dependencies clear and prevents merge conflicts.
*   **Configuration**:
    *   Profile: `black` (to ensure compatibility with Black).
    *   Configured in: `pyproject.toml` (via arguments in `.pre-commit-config.yaml` and CI scripts, though `pyproject.toml` support is standard).

### 3. Linting (`flake8`)

*   **Tool**: [Flake8](https://flake8.pycqa.org/)
*   **Reasoning**: Flake8 checks for style violations (PEP 8) and logic errors (unused imports, undefined variables). It is a staple of Python development.
*   **Configuration**:
    *   Max line length: **88** characters (to match Black).
    *   Ignores: `E203` (whitespace before ':'), `W503` (line break before binary operator) - required for Black compatibility.
    *   Configured in: `pyproject.toml`.

### 4. Type Checking (`mypy`)

*   **Tool**: [MyPy](https://mypy.readthedocs.io/)
*   **Reasoning**: Static type checking catches type-related bugs before runtime. Home Assistant encourages strict typing.
*   **Configuration**:
    *   Strict optional: True.
    *   Ignore missing imports: True (for some HA dependencies that might not have stubs).
    *   Configured in: `pyproject.toml`.

### 5. Security Scanning (`bandit`)

*   **Tool**: [Bandit](https://bandit.readthedocs.io/)
*   **Reasoning**: Scans for common security issues in Python code (e.g., hardcoded passwords, unsafe execution).
*   **Configuration**:
    *   Recursive scan of `custom_components/satcom_forecast`.
    *   Configured in: `.pre-commit-config.yaml` and GitHub Actions.

### 6. Testing (`pytest`)

*   **Tool**: [pytest](https://docs.pytest.org/)
*   **Reasoning**: The industry standard for Python testing. It supports fixtures, parameterization, and async testing.
*   **Configuration**:
    *   Asyncio mode: `auto`.
    *   Test paths: `tests/`.
    *   Coverage: `pytest-cov` targeting `custom_components/satcom_forecast`.
    *   Configured in: `pyproject.toml`.

## Configuration Management

We have consolidated configuration into **`pyproject.toml`** wherever possible to reduce clutter and provide a single source of truth.

*   **`pyproject.toml`**: Contains config for `black`, `flake8`, `mypy`, and `pytest`.
*   **`.pre-commit-config.yaml`**: Defines the hooks that run locally before commits.
*   **`.github/workflows/test.yml`**: Defines the CI/CD pipeline that enforces these checks.

## CI/CD Integration

Our GitHub Actions workflow (`.github/workflows/test.yml`) enforces these standards on every pull request and push to main branches:

1.  **Test Job**: Runs `pytest` across multiple Python versions (3.9, 3.10, 3.11).
2.  **Lint Job**: Runs `black`, `flake8`, `isort`, `mypy`, and `bandit`.
3.  **Result Reporting**: Generates a summary of linting issues and posts it as a comment on Pull Requests.

## Pre-commit Hooks

We use `pre-commit` to run these checks locally. This prevents "fix style" commits and ensures that code pushed to the repo is already compliant.

*   **Installation**: `pre-commit install`
*   **Usage**: Runs automatically on `git commit`. Can be run manually via `pre-commit run --all-files`.

## Future Considerations: Ruff

Home Assistant Core has migrated to [Ruff](https://beta.ruff.rs/docs/), a highly performant linter and formatter written in Rust. Ruff can replace Black, Flake8, and Isort.

**Why we haven't switched yet:**
*   Our current "Classic Stack" is fully configured and working correctly.
*   We recently invested in standardizing the configuration in `pyproject.toml`.
*   Migration to Ruff is a planned future improvement but not a blocking requirement for current development.

## Compliance with Home Assistant Standards

Our strategy complies with Home Assistant recommendations by:
*   Using **async** tests (`pytest-asyncio`).
*   Enforcing **PEP 8** via Black/Flake8.
*   Using **Type Hints** (MyPy).
*   Structuring the integration as a standard `custom_component`.
*   Ensuring high test coverage for logic and parsing.

