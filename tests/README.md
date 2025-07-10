# SatCom Forecast Test Suite

This directory contains comprehensive tests for the SatCom Forecast integration, now using **pytest** for modern, maintainable testing.

## Test Structure

### Main Test Files
- **`test_forecast_parser.py`** - Comprehensive tests for forecast parsing, formatting, and all weather events
- **`test_imap_handler.py`** - Tests for IMAP email handling functionality
- **`verify_installation.py`** - Installation and integration structure validation

### Legacy Test Runner
- **`run_tests.py`** - Legacy test runner (deprecated, use pytest instead)

## Running Tests

### Run All Tests (Recommended)
```bash
# From project root
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=custom_components/satcom_forecast
```

### Run Specific Test Files
```bash
# Run main forecast parser tests
pytest tests/test_forecast_parser.py -v

# Run IMAP handler tests
pytest tests/test_imap_handler.py -v

# Run installation verification
pytest tests/verify_installation.py -v
```

### Run Specific Test Classes or Methods
```bash
# Run specific test class
pytest tests/test_forecast_parser.py::TestForecastParser -v

# Run specific test method
pytest tests/test_forecast_parser.py::TestForecastParser::test_smoke_conditions -v
```

## Test Coverage

### Forecast Parser Tests (`test_forecast_parser.py`)

#### Basic Functionality
- ✅ **Basic Formats**: Tests summary, compact, and full format generation
- ✅ **Explicit Percentages**: Validates explicit precipitation percentage handling
- ✅ **Temperature/Wind Extraction**: Tests temperature and wind information parsing

#### Weather Event Detection
- ✅ **Smoke Conditions**: Tests smoke detection with probability levels
  - Areas of smoke (65%)
  - Wildfire smoke (75%)
  - Heavy smoke (90%)
  - Widespread haze (50%)
- ✅ **Weather Events**: Parametrized tests for fog, thunderstorms, wind, snow, freezing rain
- ✅ **Smoke with Precipitation**: Ensures smoke and precipitation don't share percentages

#### Period Detection and Abbreviations
- ✅ **Period Detection**: Tests all forecast periods (This Afternoon, Tonight, Today, etc.)
- ✅ **Standard Abbreviations**: Validates "Tngt" for Tonight, "Aft" for This Afternoon
- ✅ **Summary Formatting**: Tests real-world forecast scenarios

#### Real-World Scenarios
- ✅ **Complex Forecasts**: Tests multi-day forecasts with various weather conditions
- ✅ **Edge Cases**: Handles edge cases in forecast parsing and formatting

### IMAP Handler Tests (`test_imap_handler.py`)
- ✅ **Email Processing**: Tests IMAP connection and email handling
- ✅ **GPS Extraction**: Validates coordinate extraction from email bodies
- ✅ **Format Detection**: Tests format keyword detection in emails

### Installation Verification (`verify_installation.py`)
- ✅ **File Structure**: Validates integration file structure and manifest
- ✅ **Dependencies**: Checks required dependencies and imports
- ✅ **Configuration**: Tests configuration flow and validation

## Test Output

The pytest suite provides:
- 📍 Detailed test results with pass/fail indicators
- 📝 Test descriptions and docstrings
- 📊 Coverage information (when using --cov)
- ✅/❌ Clear pass/fail status
- 🎯 Specific test method names and parameters

## GitHub Actions

Tests are automatically run on:
- Every push to `main` and `develop` branches
- Every pull request to `main` branch
- Multiple Python versions (3.9, 3.10, 3.11)

The GitHub Action includes:
- **Pytest Suite** - Runs all pytest-based tests
- **Linting** - Code quality checks (Black, Flake8)
- **Integration Structure** - Validates file structure

## Test Requirements

### Dependencies
- Python 3.9+
- `pytest` - Modern testing framework
- `pytest-cov` - Coverage reporting (optional)
- `aiohttp` - For API requests
- `beautifulsoup4` - For HTML parsing

### Installation
```bash
# Install pytest and dependencies
pip install pytest pytest-cov

# Or install from requirements
pip install -r requirements.txt
```

### Environment
Tests can be run in any environment with Python 3.9+ installed. No Home Assistant environment is required for most tests.

## Troubleshooting

### Common Issues

#### Test Fails with "No module named 'homeassistant'"
- This is expected for tests run outside of Home Assistant
- The integration will work fine inside Home Assistant
- Only the installation verification test requires the actual files

#### Pytest Not Found
```bash
# Install pytest
pip install pytest

# Or use python -m pytest
python -m pytest tests/ -v
```

#### Import Errors
- Ensure you're running from the project root directory
- Check that the custom_components path is correctly set in test files
- Verify all required dependencies are installed

### Debug Mode
To see detailed debug output:
```bash
# Run with verbose output
pytest tests/ -v -s

# Run with debug logging
pytest tests/ -v --log-cli-level=DEBUG
```

## Migration from Legacy Tests

The test suite has been modernized from the legacy `run_tests.py` approach:

### Before (Legacy)
```bash
cd tests
python run_tests.py
```

### After (Modern)
```bash
pytest tests/ -v
```

### Benefits of Pytest
- ✅ **Better organization**: Tests are organized in classes and methods
- ✅ **Parametrized tests**: Efficient testing of multiple scenarios
- ✅ **Clear output**: Detailed test results and failure information
- ✅ **Coverage reporting**: Built-in coverage analysis
- ✅ **Modern tooling**: Integration with CI/CD and development tools
- ✅ **Maintainable**: Easier to add, modify, and debug tests

## Contributing

When adding new tests:
1. Follow pytest conventions and naming
2. Use descriptive test method names
3. Include comprehensive docstrings
4. Use parametrized tests for multiple scenarios
5. Add appropriate assertions and error handling
6. Ensure tests can run independently

## Test Coverage Summary

The modern test suite covers:
- ✅ **Forecast Parsing**: All format types and edge cases
- ✅ **Weather Events**: Comprehensive event detection including smoke
- ✅ **Period Detection**: All forecast periods and abbreviations
- ✅ **Real-world Scenarios**: Complex multi-day forecasts
- ✅ **IMAP Handling**: Email processing and GPS extraction
- ✅ **Installation**: File structure and integration validation
- ✅ **Modern Testing**: Pytest-based, maintainable test suite
