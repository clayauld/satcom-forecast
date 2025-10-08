# Weather.gov API Migration

This document provides a comprehensive guide to the Weather.gov API migration for the SatCom Forecast system.

## Overview

The SatCom Forecast system has been migrated from HTML web scraping to use the official Weather.gov API. This migration provides:

- **Improved Reliability**: Stable JSON API instead of fragile HTML parsing
- **Better Data Quality**: Access to precise numerical data and structured responses
- **Reduced Maintenance**: Official API contract vs. HTML parsing
- **Future-Proofing**: Long-term support from the National Weather Service
- **Enhanced Performance**: Caching and optimized data processing

## Architecture

### New Components

The migration introduces several new modules:

```
custom_components/satcom_forecast/
├── api_client.py              # Weather.gov API client
├── api_config.py              # Configuration management
├── api_models.py              # Data models and structures
├── api_data_processor.py      # API data processing
├── api_formatter.py           # Output formatting
├── api_cache.py               # Response caching
├── api_error_handler.py       # Error handling framework
└── forecast_fetcher_api.py    # Enhanced forecast fetcher
```

### Data Flow

```
Coordinates → API Client → Weather.gov API → JSON Response → 
Data Processor → Weather Events → Formatter → Output Text
```

## Configuration

### Environment Variables

The system can be configured using environment variables:

```bash
# API Configuration
WEATHER_API_BASE_URL="https://api.weather.gov"
WEATHER_API_USER_AGENT="SatComForecast/1.0"
WEATHER_API_TIMEOUT=10
WEATHER_API_RETRY_ATTEMPTS=3
WEATHER_API_RATE_LIMIT_DELAY=0.5
WEATHER_API_CACHE_DURATION=300
WEATHER_API_MAX_CACHE_SIZE=1000

# Feature Flags
WEATHER_USE_API=true
WEATHER_FALLBACK_HTML=true
WEATHER_ENABLE_CACHING=true
WEATHER_DEBUG_MODE=false
```

### Feature Flags

The system supports several feature flags for gradual rollout:

- `use_api`: Enable API mode (default: false)
- `fallback_to_html`: Fallback to HTML scraping on API failure (default: true)
- `enable_caching`: Enable response caching (default: true)
- `enable_metrics`: Enable performance metrics (default: true)
- `debug_mode`: Enable debug logging (default: false)

## Usage

### Basic Usage

The API migration is transparent to existing code. The `fetch_forecast` function automatically chooses between API and HTML modes based on configuration:

```python
from custom_components.satcom_forecast.forecast_fetcher_api import fetch_forecast

# Automatically uses API or HTML based on configuration
forecast_text = await fetch_forecast(lat, lon, days)
```

### Advanced Usage

For more control, you can use the individual components:

```python
from custom_components.satcom_forecast.api_client import WeatherGovAPIClient
from custom_components.satcom_forecast.api_data_processor import APIDataProcessor
from custom_components.satcom_forecast.api_formatter import APIFormatter

# Use API client directly
async with WeatherGovAPIClient() as client:
    office, grid_x, grid_y = await client.get_gridpoint(lat, lon)
    forecast_data = await client.get_forecast(office, grid_x, grid_y)

# Process and format data
processor = APIDataProcessor()
formatter = APIFormatter()

processed_data = processor.process_forecast_data(forecast_data)
events = []
for period in processed_data.periods:
    events.extend(processor.extract_weather_events(period))

summary = formatter.format_forecast(processed_data.periods, events, "summary")
```

### Hybrid Mode

The system supports hybrid mode for gradual migration:

```python
from custom_components.satcom_forecast.forecast_fetcher_api import fetch_forecast_hybrid

# Force API mode
forecast = await fetch_forecast_hybrid(lat, lon, days, mode='api')

# Force HTML mode
forecast = await fetch_forecast_hybrid(lat, lon, days, mode='html')

# Auto mode (uses configuration)
forecast = await fetch_forecast_hybrid(lat, lon, days, mode='auto')
```

## Testing

### Running Tests

The migration includes comprehensive tests:

```bash
# Run unit tests
python scripts/run_api_tests.py unit

# Run integration tests (requires internet)
python scripts/run_api_tests.py integration

# Run compatibility tests
python scripts/run_api_tests.py compatibility

# Run performance tests
python scripts/run_api_tests.py performance

# Run all tests
python scripts/run_api_tests.py all

# Run with coverage
python scripts/run_api_tests.py unit --coverage --html-report
```

### Test Categories

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test with real Weather.gov API endpoints
3. **Compatibility Tests**: Ensure output matches current implementation
4. **Performance Tests**: Benchmark performance improvements

## Migration Guide

### Phase 1: Preparation

1. **Review Configuration**: Ensure all environment variables are set correctly
2. **Test API Access**: Verify connectivity to Weather.gov API
3. **Backup Current System**: Ensure rollback capability

### Phase 2: Gradual Rollout

1. **Enable API Mode**: Set `WEATHER_USE_API=true`
2. **Keep Fallback**: Ensure `WEATHER_FALLBACK_HTML=true`
3. **Monitor Performance**: Watch for errors and performance metrics
4. **Validate Output**: Compare API output with HTML output

### Phase 3: Full Migration

1. **Disable Fallback**: Set `WEATHER_FALLBACK_HTML=false` when confident
2. **Optimize Configuration**: Tune caching and performance settings
3. **Remove HTML Code**: Clean up old HTML scraping code (optional)

## Monitoring

### Error Handling

The system includes comprehensive error handling:

- **Retry Logic**: Automatic retry with exponential backoff
- **Circuit Breaker**: Prevents cascading failures
- **Fallback Mechanisms**: Automatic fallback to HTML scraping
- **Error Classification**: Categorized error reporting

### Performance Metrics

Monitor these key metrics:

- **API Success Rate**: Should be >99%
- **Response Time**: Should be <5 seconds
- **Cache Hit Rate**: Should be >80% for repeated requests
- **Error Rate**: Should be <1%

### Logging

The system provides detailed logging:

```python
import logging

# Enable debug logging
logging.getLogger('custom_components.satcom_forecast').setLevel(logging.DEBUG)
```

## Troubleshooting

### Common Issues

1. **API Rate Limiting**
   - **Symptom**: 429 errors or slow responses
   - **Solution**: Increase `WEATHER_API_RATE_LIMIT_DELAY`

2. **Invalid Coordinates**
   - **Symptom**: 404 errors
   - **Solution**: Validate coordinates are within valid ranges

3. **Network Timeouts**
   - **Symptom**: Timeout errors
   - **Solution**: Increase `WEATHER_API_TIMEOUT`

4. **Cache Issues**
   - **Symptom**: Stale data or memory usage
   - **Solution**: Adjust `WEATHER_API_CACHE_DURATION` or `WEATHER_API_MAX_CACHE_SIZE`

### Debug Mode

Enable debug mode for detailed logging:

```bash
export WEATHER_DEBUG_MODE=true
```

### Fallback Testing

Test fallback mechanism:

```python
# Force API failure to test fallback
import os
os.environ['WEATHER_API_BASE_URL'] = 'https://invalid-url.com'
```

## Performance

### Caching

The system implements intelligent caching:

- **Grid Point Data**: Cached for 24 hours (coordinates don't change)
- **Forecast Data**: Cached for 1 hour (forecast updates frequently)
- **Alert Data**: Cached for 30 minutes (alerts change frequently)

### Optimization

Performance optimizations include:

- **Connection Pooling**: Reuse HTTP connections
- **Parallel Processing**: Concurrent data processing
- **Memory Management**: Efficient data structures
- **Rate Limiting**: Respect API limits

## Security

### Best Practices

- **User-Agent**: Always include proper User-Agent header
- **Rate Limiting**: Respect API rate limits
- **Error Handling**: Don't expose sensitive information
- **Input Validation**: Validate all inputs

### API Terms of Service

Ensure compliance with Weather.gov API terms of service:

- Include proper User-Agent header
- Respect rate limits
- Don't abuse the service
- Follow attribution requirements

## Support

### Documentation

- **API Documentation**: [Weather.gov API](https://www.weather.gov/documentation/services-web-api)
- **Migration Documents**: See `docs/development/` directory
- **Test Results**: See test output and coverage reports

### Issues

Report issues with:

1. **Error logs** with debug information
2. **Configuration** used
3. **Test results** if applicable
4. **Steps to reproduce**

### Contributing

When contributing to the API migration:

1. **Follow existing code style**
2. **Add comprehensive tests**
3. **Update documentation**
4. **Test with real API endpoints**

## Changelog

### Version 1.0.0

- Initial API migration implementation
- Complete Weather.gov API integration
- Comprehensive error handling
- Caching system
- Hybrid mode support
- Full test suite
- Documentation

## License

This migration maintains the same license as the original SatCom Forecast system.

---

For more information, see the detailed migration documents in `docs/development/`.