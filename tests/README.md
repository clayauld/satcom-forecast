# SatCom Forecast Test Suite

This directory contains comprehensive tests for the SatCom Forecast integration.

## Test Structure

### Core Tests
- **`test_integration_structure.py`** - Validates integration file structure and manifest
- **`test_reconfiguration.py`** - Tests reconfiguration functionality and polling interval
- **`test_core_functionality.py`** - Tests basic forecast fetching and formatting
- **`test_multi_region.py`** - Tests forecast functionality across different geographic regions
- **`test_weather_detection.py`** - Tests weather event detection (fog, thunderstorms, etc.)
- **`test_summary_length.py`** - Validates summary format character limits

### Test Runner
- **`run_tests.py`** - Main test runner that executes all tests in logical order

## Running Tests

### Run All Tests
```bash
cd tests
python run_tests.py
```

### Run Individual Tests
```bash
cd tests
python test_integration_structure.py
python test_reconfiguration.py
python test_core_functionality.py
python test_multi_region.py
python test_weather_detection.py
python test_summary_length.py
```

### Test Categories

#### 1. Integration Structure Test
Validates that the integration has the correct file structure and manifest:
- ✅ Required files exist
- ✅ Manifest.json is complete and valid
- ✅ Python syntax is correct
- ✅ Directory structure is proper

#### 2. Reconfiguration Test
Tests the new reconfiguration functionality:
- ✅ Polling interval configuration (1-1440 minutes)
- ✅ Password handling logic
- ✅ Migration from version 2 to 3
- ✅ Schema structure validation

#### 3. Core Functionality Test
Tests basic integration functionality:
- ✅ NOAA forecast fetching
- ✅ All three format types (summary, compact, full)
- ✅ Format length validation
- ✅ Character limit compliance

#### 4. Multi-Region Test
Tests forecast functionality across different geographic regions:
- ✅ Alaska (Fairbanks, Anchorage) - Coastal weather, fog, thunderstorms
- ✅ Florida (Miami) - Hurricane season, wind, thunderstorms
- ✅ Illinois (Chicago) - Spring storms, rain, wind
- ✅ Massachusetts (Boston) - Heat waves, thunderstorms
- ✅ California (Los Angeles) - Fog conditions
- ✅ New York - Mixed conditions
- ✅ Colorado (Denver) - Mountain weather

#### 5. Weather Detection Test
Tests detection of various weather events:
- ✅ Fog conditions (dense, patchy, general)
- ✅ Thunderstorms and extreme weather
- ✅ Rain and precipitation
- ✅ Wind conditions
- ✅ Event probability inference

#### 6. Summary Length Test
Validates summary format character limits:
- ✅ All summaries under 200 characters
- ✅ Proper weather event prioritization
- ✅ Percentage display
- ✅ Format efficiency analysis

## Test Output

The test suite provides detailed output including:
- 📍 Location and coordinates being tested
- 📝 Sample forecast content for each format
- 📊 Character analysis and efficiency metrics
- ✅/❌ Pass/fail indicators
- 🎉 Success summaries

## GitHub Actions

Tests are automatically run on:
- Every push to `main` and `develop` branches
- Every pull request to `main` branch
- Multiple Python versions (3.9, 3.10, 3.11)

The GitHub Action includes:
- **Test Suite** - Runs all functional tests
- **Linting** - Code quality checks (Black, Flake8)
- **Integration Structure** - Validates file structure

## Test Requirements

### Dependencies
- Python 3.9+
- `aiohttp` - For API requests
- `beautifulsoup4` - For HTML parsing

### Environment
Tests can be run in any environment with Python 3.9+ installed. No Home Assistant environment is required for most tests.

## Troubleshooting

### Common Issues

#### Test Fails with "No module named 'homeassistant'"
- This is expected for tests run outside of Home Assistant
- The integration will work fine inside Home Assistant
- Only the integration structure test requires the actual files

#### Integration Structure Test Fails
- Ensure you're running from the project root directory
- Check that all required files exist in `custom_components/satcom_forecast/`
- Verify manifest.json has all required fields

#### Weather API Tests Fail
- Check internet connectivity
- NOAA API may be temporarily unavailable
- Some tests use real API calls to validate functionality

### Debug Mode
To see detailed debug output, set the debug environment variable:
```bash
DEBUG=1 python run_tests.py
```

## Contributing

When adding new tests:
1. Follow the existing naming convention (`test_*.py`)
2. Include comprehensive docstrings
3. Add the test to `run_tests.py` in the appropriate order
4. Ensure tests can run independently
5. Add appropriate error handling

## Test Coverage

The test suite covers:
- ✅ Integration structure and manifest validation
- ✅ Configuration and reconfiguration functionality
- ✅ Core forecast fetching and formatting
- ✅ Multi-region weather conditions
- ✅ Weather event detection
- ✅ Character limits and format validation
- ✅ Migration and backward compatibility
- ✅ Polling interval configuration 