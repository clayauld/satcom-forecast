# Contributing to SatCom Forecast

Thank you for your interest in contributing to SatCom Forecast! This guide will help you get started with development and ensure your contributions align with the project's standards.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)
- [Feature Requests](#feature-requests)
- [Code of Conduct](#code-of-conduct)

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- A Home Assistant instance for testing (optional for most development)
- Basic knowledge of Python and Home Assistant integrations

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/satcom-forecast.git
   cd satcom-forecast
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/clayauld/satcom-forecast.git
   ```

## Development Setup

### Virtual Environment

Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### Install Dependencies

Install development dependencies:

```bash
# Install all dependencies including dev tools
pip install -e ".[dev]"

# Or install manually
pip install pytest pytest-asyncio pytest-cov black flake8 mypy pre-commit
```

### Pre-commit Hooks

Set up pre-commit hooks for automatic code formatting and linting:

```bash
# Install pre-commit hooks
pre-commit install

# Run manually (optional)
pre-commit run --all-files
```

## Code Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **String quotes**: Double quotes for docstrings, single quotes for strings
- **Import order**: Standard library, third-party, local imports

### Code Formatting

We use [Black](https://black.readthedocs.io/) for automatic code formatting:

```bash
# Format all Python files
black custom_components/satcom_forecast/ tests/

# Check formatting without making changes
black --check custom_components/satcom_forecast/ tests/
```

### Linting

We use [Flake8](https://flake8.pycqa.org/) for linting:

```bash
# Run linting
flake8 custom_components/satcom_forecast/ tests/ --max-line-length=88 --extend-ignore=E203,W503
```

### Type Checking

We use [MyPy](https://mypy.readthedocs.io/) for static type checking:

```bash
# Run type checking
mypy custom_components/satcom_forecast/
```

### Home Assistant Integration Standards

Follow the [Home Assistant Integration Development](https://developers.home-assistant.io/docs/integration_development/) guidelines:

- Use async/await for all I/O operations
- Implement proper error handling
- Follow the configuration flow pattern
- Use the coordinator pattern for data updates
- Implement proper logging with appropriate levels

### File Structure

Maintain the existing file structure:

```
custom_components/satcom_forecast/
├── __init__.py              # Integration entry point
├── config_flow.py           # Configuration flow
├── const.py                 # Constants and configuration
├── coordinator.py           # Data coordinator
├── forecast_fetcher.py      # NOAA API client
├── forecast_parser.py       # Forecast parsing and formatting
├── imap_handler.py          # Email handling
├── manifest.json            # Integration manifest
├── notifier.py              # Email notification
├── sensor.py                # Sensor entity
├── services.yaml            # Service definitions
├── split_util.py            # Message splitting utilities
└── translations/            # Translation files
    └── en.json
```

## Testing

### Running Tests

We use pytest for testing. Run tests from the project root:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=custom_components/satcom_forecast

# Run specific test file
pytest tests/test_forecast_parser.py -v

# Run specific test method
pytest tests/test_forecast_parser.py::TestForecastParser::test_smoke_conditions -v
```

### Test Structure

- **Unit tests**: Test individual functions and classes
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete workflows

### Writing Tests

Follow these guidelines when writing tests:

1. **Use descriptive names**: Test method names should clearly describe what they test
2. **Test one thing**: Each test should verify a single behavior
3. **Use parametrized tests**: For testing multiple scenarios efficiently
4. **Mock external dependencies**: Use mocks for API calls and file operations
5. **Test edge cases**: Include tests for error conditions and boundary values

Example test structure:

```python
import pytest
from unittest.mock import Mock, patch

class TestForecastParser:
    """Test forecast parsing functionality."""
    
    def test_basic_format_parsing(self):
        """Test basic forecast format parsing."""
        # Arrange
        forecast_data = {...}
        
        # Act
        result = parse_forecast(forecast_data)
        
        # Assert
        assert result is not None
        assert "summary" in result
    
    @pytest.mark.parametrize("weather_event,expected", [
        ("rain", "Rain"),
        ("snow", "Snow"),
        ("fog", "Fog"),
    ])
    def test_weather_event_detection(self, weather_event, expected):
        """Test weather event detection for various conditions."""
        # Test implementation
        pass
```

### Test Coverage

Maintain high test coverage (aim for 90%+):

```bash
# Generate coverage report
pytest tests/ --cov=custom_components/satcom_forecast --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Pull Request Process

### Before Submitting

1. **Update your fork**: Keep your fork up to date with the main repository
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**: Follow the coding standards and add tests

4. **Run tests**: Ensure all tests pass
   ```bash
   pytest tests/ -v
   ```

5. **Run linting**: Fix any linting issues
   ```bash
   black custom_components/satcom_forecast/ tests/
   flake8 custom_components/satcom_forecast/ tests/
   mypy custom_components/satcom_forecast/
   ```

6. **Commit your changes**: Use conventional commit messages
   ```bash
   git commit -m "feat: add new weather event detection"
   git commit -m "fix: resolve IMAP connection timeout issue"
   git commit -m "docs: update configuration documentation"
   ```

### Conventional Commits

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

### Pull Request Guidelines

1. **Title**: Use a clear, descriptive title
2. **Description**: Provide a detailed description of your changes
3. **Related issues**: Link to any related issues
4. **Testing**: Describe how you tested your changes
5. **Breaking changes**: Note any breaking changes

Example PR description:

```markdown
## Description
Adds support for detecting heavy smoke conditions with probability levels.

## Changes
- Added heavy smoke detection (90% probability threshold)
- Updated smoke detection logic to handle multiple smoke types
- Added tests for new smoke detection functionality

## Testing
- Added unit tests for heavy smoke detection
- Tested with real NOAA forecast data
- Verified backward compatibility

## Related Issues
Closes #123
```

### Review Process

1. **Automated checks**: GitHub Actions will run tests and linting
2. **Code review**: At least one maintainer must approve
3. **Merge**: Once approved, your PR will be merged

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

1. **Environment details**:
   - Home Assistant version
   - Integration version
   - Python version
   - Operating system

2. **Steps to reproduce**:
   - Clear, step-by-step instructions
   - Sample data or configuration

3. **Expected vs actual behavior**:
   - What you expected to happen
   - What actually happened

4. **Logs**: Include relevant debug logs (with sensitive information removed)

5. **Additional context**:
   - Screenshots if applicable
   - Configuration files (with sensitive data removed)

### Issue Templates

Use the provided issue templates for:
- Bug reports
- Feature requests
- Documentation improvements

## Feature Requests

When requesting features:

1. **Describe the problem**: What problem does this feature solve?
2. **Propose a solution**: How should the feature work?
3. **Consider alternatives**: Are there other ways to solve this?
4. **Implementation ideas**: Do you have ideas for implementation?

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Use welcoming and inclusive language
- Be collaborative and constructive
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Publishing others' private information
- Other conduct inappropriate in a professional setting

### Enforcement

Violations will be addressed by the project maintainers. We reserve the right to remove, edit, or reject comments, commits, code, and other contributions that are not aligned with this Code of Conduct.

## Getting Help

If you need help with development:

1. **Check existing issues**: Search for similar issues or questions
2. **Read documentation**: Review the README and other docs
3. **Ask questions**: Use GitHub Discussions for general questions
4. **Join the community**: Engage with other contributors

## Recognition

Contributors will be recognized in:
- The project README
- Release notes
- GitHub contributors list

Thank you for contributing to SatCom Forecast! 🚀 