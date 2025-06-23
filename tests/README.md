# SatCom Forecast Integration Tests

This directory contains a comprehensive test suite for the SatCom Forecast Home Assistant integration.

## Test Structure

The test suite is organized into logical categories:

### 🧪 Core Functionality Tests
- **`test_core_functionality.py`** - Tests basic forecast fetching, parsing, and all three output formats
- **`test_multi_region.py`** - Tests forecast functionality across different geographic regions and weather conditions

### 🌦️ Weather Detection Tests
- **`test_weather_detection.py`** - Tests detection of various weather events including fog, extreme events, and different conditions

### 📝 Format Validation Tests
- **`test_summary_length.py`** - Tests summary format constraints and character limits

## Running Tests

### Run All Tests
```bash
cd tests
python3 run_tests.py
```

### Run Individual Tests
```bash
cd tests
python3 test_core_functionality.py
python3 test_multi_region.py
python3 test_weather_detection.py
python3 test_summary_length.py
```

## Test Coverage

### Core Functionality
- ✅ NOAA API integration
- ✅ Forecast fetching
- ✅ All three output formats (Summary, Compact, Full)
- ✅ Format length validation
- ✅ Error handling

### Multi-Region Testing
- ✅ 8 different geographic locations
- ✅ Various weather conditions
- ✅ Different seasons and climates
- ✅ Duplicate detection validation
- ✅ Format consistency across regions

### Weather Detection
- ✅ Rain and precipitation
- ✅ Thunderstorms
- ✅ Wind conditions
- ✅ Fog (dense, patchy, general)
- ✅ Extreme weather events
- ✅ Probability inference
- ✅ Event merging and deduplication

### Format Validation
- ✅ Summary format 200-character limit
- ✅ Compact format readability
- ✅ Full format completeness
- ✅ Character count analysis
- ✅ Format efficiency metrics

## Test Output Files

- **`multi_region_test_fixed_full.txt`** - Multi-region test output for analysis

## Requirements

- Python 3.8+
- Internet connection (for NOAA API calls)
- Home Assistant environment (for integration imports)

## Test Results

The test suite provides comprehensive validation of:
- **API Reliability** - NOAA forecast fetching across regions
- **Format Consistency** - All three formats working correctly
- **Weather Detection** - Accurate identification of weather events
- **Performance** - Character limits and efficiency metrics
- **Error Handling** - Graceful handling of API failures

## Notes

- Tests require the integration to be properly installed in Home Assistant
- Some tests make real API calls to NOAA services
- Test output includes detailed formatting examples for all three forecast formats
- All tests include validation and error reporting 