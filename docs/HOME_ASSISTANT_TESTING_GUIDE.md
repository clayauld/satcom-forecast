# Home Assistant Testing Guide - Weather API Migration

This guide provides detailed instructions for testing the Weather.gov API migration in Home Assistant with Docker.

## Overview

The API migration can be tested in Home Assistant using environment variables to control the behavior. This allows for safe testing and gradual rollout without affecting the existing system.

## Prerequisites

- Home Assistant running in Docker
- Access to Docker configuration files
- Basic understanding of Docker environment variables

## Testing Methods

### Method 1: Docker Compose (Recommended)

This is the easiest and most maintainable approach for testing.

#### Step 1: Update docker-compose.yml

Add the environment variables to your `docker-compose.yml`:

```yaml
version: '3.8'
services:
  homeassistant:
    container_name: homeassistant
    image: ghcr.io/home-assistant/home-assistant:stable
    volumes:
      - ./config:/config
      - /etc/localtime:/etc/localtime:ro
    environment:
      # Weather API Configuration - Phase 2 Testing
      - WEATHER_USE_API=true
      - WEATHER_FALLBACK_HTML=true
      - WEATHER_ENABLE_CACHING=true
      - WEATHER_DEBUG_MODE=true
      - WEATHER_API_TIMEOUT=10
      - WEATHER_API_RETRY_ATTEMPTS=3
      - WEATHER_API_RATE_LIMIT_DELAY=0.5
      - WEATHER_API_CACHE_DURATION=300
      - WEATHER_API_MAX_CACHE_SIZE=1000
    restart: unless-stopped
    privileged: true
    network_mode: host
    ports:
      - "8123:8123"
```

#### Step 2: Restart Home Assistant

```bash
# Stop the container
docker-compose down

# Start with new configuration
docker-compose up -d

# Check logs
docker-compose logs -f homeassistant
```

### Method 2: Docker Run Command

If you're using `docker run` instead of Docker Compose:

```bash
# Stop existing container
docker stop homeassistant
docker rm homeassistant

# Start with environment variables
docker run -d \
  --name homeassistant \
  --privileged \
  --restart unless-stopped \
  -e WEATHER_USE_API=true \
  -e WEATHER_FALLBACK_HTML=true \
  -e WEATHER_ENABLE_CACHING=true \
  -e WEATHER_DEBUG_MODE=true \
  -e WEATHER_API_TIMEOUT=10 \
  -e WEATHER_API_RETRY_ATTEMPTS=3 \
  -e WEATHER_API_RATE_LIMIT_DELAY=0.5 \
  -e WEATHER_API_CACHE_DURATION=300 \
  -e WEATHER_API_MAX_CACHE_SIZE=1000 \
  -v /path/to/your/config:/config \
  -v /etc/localtime:/etc/localtime:ro \
  --network=host \
  ghcr.io/home-assistant/home-assistant:stable
```

### Method 3: Environment File

For easier management, create a `.env` file:

#### Step 1: Create .env file

```bash
# .env file
WEATHER_USE_API=true
WEATHER_FALLBACK_HTML=true
WEATHER_ENABLE_CACHING=true
WEATHER_DEBUG_MODE=true
WEATHER_API_TIMEOUT=10
WEATHER_API_RETRY_ATTEMPTS=3
WEATHER_API_RATE_LIMIT_DELAY=0.5
WEATHER_API_CACHE_DURATION=300
WEATHER_API_MAX_CACHE_SIZE=1000
```

#### Step 2: Update docker-compose.yml

```yaml
version: '3.8'
services:
  homeassistant:
    container_name: homeassistant
    image: ghcr.io/home-assistant/home-assistant:stable
    env_file:
      - .env
    volumes:
      - ./config:/config
      - /etc/localtime:/etc/localtime:ro
    restart: unless-stopped
    privileged: true
    network_mode: host
    ports:
      - "8123:8123"
```

## Testing Phases

### Phase 1: Safe Testing (HTML Mode)

Start with the original HTML scraping to ensure everything works:

```bash
# Environment variables for Phase 1
WEATHER_USE_API=false
WEATHER_FALLBACK_HTML=true
WEATHER_DEBUG_MODE=true
```

**What this tests:**
- Original functionality still works
- No API calls are made
- System behaves exactly as before

### Phase 2: API Testing (With Fallback)

Enable the API with HTML fallback:

```bash
# Environment variables for Phase 2
WEATHER_USE_API=true
WEATHER_FALLBACK_HTML=true
WEATHER_DEBUG_MODE=true
```

**What this tests:**
- API integration works
- Fallback to HTML on API failure
- Performance improvements
- Output compatibility

### Phase 3: API Only (When Confident)

Use only the API (no fallback):

```bash
# Environment variables for Phase 3
WEATHER_USE_API=true
WEATHER_FALLBACK_HTML=false
WEATHER_DEBUG_MODE=false
```

**What this tests:**
- API reliability
- Performance under load
- Production readiness

## Verification and Testing

### Check Environment Variables

Verify that Home Assistant can see the environment variables:

```bash
# Check all weather-related environment variables
docker exec homeassistant printenv | grep WEATHER

# Expected output:
# WEATHER_USE_API=true
# WEATHER_FALLBACK_HTML=true
# WEATHER_ENABLE_CACHING=true
# WEATHER_DEBUG_MODE=true
# WEATHER_API_TIMEOUT=10
# WEATHER_API_RETRY_ATTEMPTS=3
# WEATHER_API_RATE_LIMIT_DELAY=0.5
# WEATHER_API_CACHE_DURATION=300
# WEATHER_API_MAX_CACHE_SIZE=1000
```

### Check Home Assistant Logs

Monitor the logs for API activity:

```bash
# Follow logs in real-time
docker logs -f homeassistant | grep -i weather

# Check recent logs
docker logs homeassistant --tail 100 | grep -i weather

# Look for specific patterns
docker logs homeassistant | grep -E "(API|Weather|Forecast)"
```

### Test API Configuration

Create a simple test script in Home Assistant:

```python
# Add this to a Home Assistant script or automation
import asyncio
import os
from custom_components.satcom_forecast.forecast_fetcher_api import fetch_forecast

async def test_weather_api():
    """Test the weather API configuration."""
    logger.info("=== Weather API Test ===")
    
    # Check configuration
    logger.info(f"USE_API: {os.getenv('WEATHER_USE_API', 'not set')}")
    logger.info(f"FALLBACK_HTML: {os.getenv('WEATHER_FALLBACK_HTML', 'not set')}")
    logger.info(f"DEBUG_MODE: {os.getenv('WEATHER_DEBUG_MODE', 'not set')}")
    
    try:
        # Test coordinates (New York City)
        lat, lon = 40.7128, -74.0060
        days = 2
        
        logger.info(f"Testing forecast for {lat}, {lon} ({days} days)")
        forecast = await fetch_forecast(lat, lon, days)
        
        if forecast and not forecast.startswith("NWS error"):
            logger.info(f"✓ API test successful: {len(forecast)} characters")
            logger.info(f"Forecast preview: {forecast[:200]}...")
            return True
        else:
            logger.error(f"✗ API test failed: {forecast}")
            return False
            
    except Exception as e:
        logger.error(f"✗ API test error: {e}")
        return False

# Run the test
result = await test_weather_api()
```

### Test Different Modes

Test the hybrid mode functionality:

```python
# Test different modes
from custom_components.satcom_forecast.forecast_fetcher_api import fetch_forecast_hybrid

async def test_modes():
    lat, lon = 40.7128, -74.0060
    days = 2
    
    # Test API mode
    try:
        api_forecast = await fetch_forecast_hybrid(lat, lon, days, mode='api')
        logger.info(f"API mode: {len(api_forecast)} chars")
    except Exception as e:
        logger.error(f"API mode failed: {e}")
    
    # Test HTML mode
    try:
        html_forecast = await fetch_forecast_hybrid(lat, lon, days, mode='html')
        logger.info(f"HTML mode: {len(html_forecast)} chars")
    except Exception as e:
        logger.error(f"HTML mode failed: {e}")
    
    # Test auto mode
    try:
        auto_forecast = await fetch_forecast_hybrid(lat, lon, days, mode='auto')
        logger.info(f"Auto mode: {len(auto_forecast)} chars")
    except Exception as e:
        logger.error(f"Auto mode failed: {e}")

# Run the test
await test_modes()
```

## Performance Testing

### Monitor Performance Metrics

Add this to a Home Assistant script to monitor performance:

```python
import time
import asyncio
from custom_components.satcom_forecast.forecast_fetcher_api import fetch_forecast

async def performance_test():
    """Test API performance."""
    lat, lon = 40.7128, -74.0060
    days = 2
    
    # Test multiple requests
    times = []
    for i in range(5):
        start_time = time.time()
        try:
            forecast = await fetch_forecast(lat, lon, days)
            end_time = time.time()
            duration = end_time - start_time
            times.append(duration)
            logger.info(f"Request {i+1}: {duration:.2f}s, {len(forecast)} chars")
        except Exception as e:
            logger.error(f"Request {i+1} failed: {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        logger.info(f"Performance: avg={avg_time:.2f}s, min={min_time:.2f}s, max={max_time:.2f}s")

# Run performance test
await performance_test()
```

### Test Caching

Test the caching functionality:

```python
from custom_components.satcom_forecast.forecast_fetcher_api import ForecastFetcherAPI

async def test_caching():
    """Test caching functionality."""
    fetcher = ForecastFetcherAPI()
    lat, lon = 40.7128, -74.0060
    
    # First call (should hit API)
    start_time = time.time()
    forecast1 = await fetcher.fetch_forecast_api(lat, lon, 1)
    first_time = time.time() - start_time
    
    # Second call (should hit cache)
    start_time = time.time()
    forecast2 = await fetcher.fetch_forecast_api(lat, lon, 1)
    second_time = time.time() - start_time
    
    logger.info(f"First call: {first_time:.2f}s")
    logger.info(f"Second call: {second_time:.2f}s")
    logger.info(f"Speedup: {first_time / second_time:.1f}x")
    logger.info(f"Results identical: {forecast1 == forecast2}")
    
    # Get cache statistics
    stats = await fetcher.get_cache_stats()
    logger.info(f"Cache stats: {stats}")

# Run caching test
await test_caching()
```

## Troubleshooting

### Common Issues

#### 1. Environment Variables Not Set

**Symptom**: Variables show as "not set" in logs

**Solution**: 
- Check Docker Compose syntax
- Restart the container after changes
- Verify the .env file exists and is readable

#### 2. API Connection Errors

**Symptom**: "API request failed" or timeout errors

**Solution**:
- Check internet connectivity
- Verify API endpoint is accessible
- Increase timeout values
- Check firewall settings

#### 3. Fallback Not Working

**Symptom**: API fails but no fallback to HTML

**Solution**:
- Ensure `WEATHER_FALLBACK_HTML=true`
- Check that original HTML fetcher is available
- Verify error handling is working

#### 4. Performance Issues

**Symptom**: Slow responses or high memory usage

**Solution**:
- Adjust cache settings
- Increase timeout values
- Check rate limiting settings
- Monitor memory usage

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Set debug mode
export WEATHER_DEBUG_MODE=true

# Or in docker-compose.yml
environment:
  - WEATHER_DEBUG_MODE=true
```

### Log Analysis

Use these commands to analyze logs:

```bash
# Find API-related errors
docker logs homeassistant | grep -i "error\|exception" | grep -i weather

# Find API requests
docker logs homeassistant | grep -i "api request"

# Find cache hits/misses
docker logs homeassistant | grep -i "cache"

# Find fallback usage
docker logs homeassistant | grep -i "fallback"
```

## Rollback Procedure

If issues occur, you can quickly rollback:

### Quick Rollback (Environment Variables)

```bash
# Set to HTML mode only
export WEATHER_USE_API=false
export WEATHER_FALLBACK_HTML=true

# Restart container
docker restart homeassistant
```

### Complete Rollback (Code)

If you need to revert to the original code:

1. Restore the original `coordinator.py`:
```python
from .forecast_fetcher import fetch_forecast  # Original import
```

2. Remove API environment variables from Docker configuration

3. Restart Home Assistant

## Best Practices

### Testing Checklist

- [ ] Environment variables are set correctly
- [ ] Home Assistant starts without errors
- [ ] Weather forecasts are generated successfully
- [ ] Performance is acceptable
- [ ] Error handling works correctly
- [ ] Fallback mechanism functions
- [ ] Caching improves performance
- [ ] Logs show expected behavior

### Monitoring

- Monitor Home Assistant logs regularly
- Check performance metrics
- Verify error rates are low
- Ensure cache hit rates are good
- Watch for memory usage

### Gradual Rollout

1. **Start with Phase 1** (HTML mode) to ensure basic functionality
2. **Move to Phase 2** (API with fallback) for testing
3. **Progress to Phase 3** (API only) when confident
4. **Monitor continuously** throughout the process

## Support

If you encounter issues:

1. Check the logs for error messages
2. Verify environment variables are set correctly
3. Test with different coordinates
4. Try different modes (API, HTML, auto)
5. Check the troubleshooting section above

For additional help, refer to the main API migration documentation or create an issue with:
- Your Docker configuration
- Relevant log excerpts
- Steps to reproduce the issue
- Expected vs. actual behavior