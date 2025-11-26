
import sys
import os
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add custom_components/satcom_forecast to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "custom_components", "satcom_forecast"))

try:
    import aiohttp
except ImportError:
    print("Error: aiohttp module not found. Please install it using 'pip install aiohttp'")
    sys.exit(1)

from api_client import WeatherGovAPIClient, APIError


async def test_api():
    print("Starting API connectivity test...")
    
    # Get config from api_config.py (which uses environment variables)
    # We'll use the default values from the class since we're not setting env vars here
    # but we want to test the client with the same structure as the app
    
    # Manually construct config to ensure it matches what we expect
    config = {
        'base_url': "https://api.weather.gov",
        'user_agent': "SatComForecast/1.0 (https://github.com/clayauld/satcom-forecast)", # Updated User-Agent
        'timeout': 10,
        'retry_attempts': 3,
        'retry_delay': 1.0,
        'rate_limit_delay': 0.5
    }
    
    print(f"Using configuration: {config}")
    
    async with WeatherGovAPIClient(**config) as client:
        # Test coordinates (same as in logs)
        lat = 61.40804
        lon = -148.44403
        
        print(f"\n1. Testing Gridpoint Lookup for {lat}, {lon}...")
        try:
            office, grid_x, grid_y = await client.get_gridpoint(lat, lon)
            print(f"Success! Gridpoint: {office}/{grid_x},{grid_y}")
        except Exception as e:
            print(f"Failed to get gridpoint: {e}")
            return

        print(f"\n2. Testing Forecast Fetch for {office}/{grid_x},{grid_y}...")
        try:
            forecast = await client.get_forecast(office, grid_x, grid_y)
            periods = forecast.get('properties', {}).get('periods', [])
            print(f"Success! Retrieved {len(periods)} forecast periods.")
            if periods:
                print(f"First period: {periods[0].get('name')}: {periods[0].get('detailedForecast')[:100]}...")
        except Exception as e:
            print(f"Failed to get forecast: {e}")
            return

    print("\nAPI Test Completed Successfully.")

if __name__ == "__main__":
    asyncio.run(test_api())
