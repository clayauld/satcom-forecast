#!/usr/bin/env python3
"""
Example script demonstrating Weather.gov API usage.

This script shows how to use the new API-based forecast system
with various configuration options and error handling.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from custom_components.satcom_forecast.forecast_fetcher_api import (
    fetch_forecast,
    fetch_forecast_api,
    fetch_forecast_hybrid,
    ForecastFetcherAPI
)
from custom_components.satcom_forecast.api_client import WeatherGovAPIClient
from custom_components.satcom_forecast.api_config import get_config
from custom_components.satcom_forecast.api_data_processor import APIDataProcessor
from custom_components.satcom_forecast.api_formatter import APIFormatter


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def example_basic_usage():
    """Example of basic API usage."""
    print("\n=== Basic API Usage ===")
    
    # Test coordinates (New York City)
    lat, lon = 40.7128, -74.0060
    days = 2
    
    try:
        # Simple forecast fetch (uses configuration)
        forecast = await fetch_forecast(lat, lon, days)
        print(f"Forecast length: {len(forecast)} characters")
        print(f"Forecast preview: {forecast[:200]}...")
        
    except Exception as e:
        print(f"Error: {e}")


async def example_hybrid_mode():
    """Example of hybrid mode usage."""
    print("\n=== Hybrid Mode Usage ===")
    
    lat, lon = 40.7128, -74.0060
    days = 2
    
    try:
        # Force API mode
        print("Using API mode...")
        api_forecast = await fetch_forecast_hybrid(lat, lon, days, mode='api')
        print(f"API forecast length: {len(api_forecast)} characters")
        
        # Force HTML mode
        print("\nUsing HTML mode...")
        html_forecast = await fetch_forecast_hybrid(lat, lon, days, mode='html')
        print(f"HTML forecast length: {len(html_forecast)} characters")
        
        # Auto mode (uses configuration)
        print("\nUsing auto mode...")
        auto_forecast = await fetch_forecast_hybrid(lat, lon, days, mode='auto')
        print(f"Auto forecast length: {len(auto_forecast)} characters")
        
    except Exception as e:
        print(f"Error: {e}")


async def example_direct_api_usage():
    """Example of direct API client usage."""
    print("\n=== Direct API Client Usage ===")
    
    lat, lon = 40.7128, -74.0060
    
    try:
        async with WeatherGovAPIClient() as client:
            # Get grid point
            print("Getting grid point...")
            office, grid_x, grid_y = await client.get_gridpoint(lat, lon)
            print(f"Grid point: {office}/{grid_x},{grid_y}")
            
            # Get forecast
            print("Getting forecast...")
            forecast_data = await client.get_forecast(office, grid_x, grid_y)
            print(f"Retrieved {len(forecast_data['properties']['periods'])} forecast periods")
            
            # Get alerts (optional)
            print("Getting alerts...")
            alerts_data = await client.get_alerts(lat, lon)
            print(f"Retrieved {len(alerts_data['features'])} alerts")
            
    except Exception as e:
        print(f"Error: {e}")


async def example_data_processing():
    """Example of data processing and formatting."""
    print("\n=== Data Processing and Formatting ===")
    
    lat, lon = 40.7128, -74.0060
    
    try:
        # Get raw API data
        async with WeatherGovAPIClient() as client:
            office, grid_x, grid_y = await client.get_gridpoint(lat, lon)
            forecast_data = await client.get_forecast(office, grid_x, grid_y)
        
        # Process data
        processor = APIDataProcessor()
        processed_data = processor.process_forecast_data(forecast_data)
        
        print(f"Processed {len(processed_data.periods)} periods")
        
        # Extract weather events
        all_events = []
        for period in processed_data.periods:
            events = processor.extract_weather_events(period)
            all_events.extend(events)
            print(f"Period {period.name}: {len(events)} events")
        
        # Format in different modes
        formatter = APIFormatter()
        
        summary = formatter.format_forecast(processed_data.periods, all_events, "summary")
        compact = formatter.format_forecast(processed_data.periods, all_events, "compact")
        full = formatter.format_forecast(processed_data.periods, all_events, "full")
        
        print(f"\nSummary ({len(summary)} chars): {summary[:100]}...")
        print(f"Compact ({len(compact)} chars): {compact[:100]}...")
        print(f"Full ({len(full)} chars): {full[:100]}...")
        
    except Exception as e:
        print(f"Error: {e}")


async def example_configuration():
    """Example of configuration management."""
    print("\n=== Configuration Management ===")
    
    config = get_config()
    
    # Get API configuration
    api_config = config.get_api_config_dict()
    print("API Configuration:")
    for key, value in api_config.items():
        print(f"  {key}: {value}")
    
    # Get feature flags
    feature_flags = config.get_feature_flags_dict()
    print("\nFeature Flags:")
    for key, value in feature_flags.items():
        print(f"  {key}: {value}")
    
    # Validate configuration
    is_valid = config.validate_config()
    print(f"\nConfiguration valid: {is_valid}")
    
    # Check specific flags
    print(f"API enabled: {config.is_api_enabled()}")
    print(f"Fallback enabled: {config.is_fallback_enabled()}")
    print(f"Caching enabled: {config.is_caching_enabled()}")


async def example_error_handling():
    """Example of error handling."""
    print("\n=== Error Handling ===")
    
    # Test with invalid coordinates
    print("Testing invalid coordinates...")
    try:
        forecast = await fetch_forecast(91, 0, 1)  # Invalid latitude
        print(f"Unexpected success: {forecast[:100]}...")
    except Exception as e:
        print(f"Expected error: {e}")
    
    # Test with valid coordinates but invalid grid point
    print("\nTesting invalid grid point...")
    try:
        async with WeatherGovAPIClient() as client:
            forecast_data = await client.get_forecast("INVALID", 999, 999)
            print(f"Unexpected success: {forecast_data}")
    except Exception as e:
        print(f"Expected error: {e}")


async def example_caching():
    """Example of caching functionality."""
    print("\n=== Caching Functionality ===")
    
    lat, lon = 40.7128, -74.0060
    
    try:
        fetcher = ForecastFetcherAPI()
        
        # First call (should hit API)
        print("First call (API hit)...")
        start_time = asyncio.get_event_loop().time()
        forecast1 = await fetcher.fetch_forecast_api(lat, lon, 1)
        first_time = asyncio.get_event_loop().time() - start_time
        print(f"Time: {first_time:.2f}s, Length: {len(forecast1)} chars")
        
        # Second call (should hit cache)
        print("Second call (cache hit)...")
        start_time = asyncio.get_event_loop().time()
        forecast2 = await fetcher.fetch_forecast_api(lat, lon, 1)
        second_time = asyncio.get_event_loop().time() - start_time
        print(f"Time: {second_time:.2f}s, Length: {len(forecast2)} chars")
        
        # Check if results are identical
        print(f"Results identical: {forecast1 == forecast2}")
        print(f"Speedup: {first_time / second_time:.1f}x")
        
        # Get cache statistics
        stats = await fetcher.get_cache_stats()
        print(f"Cache stats: {stats}")
        
    except Exception as e:
        print(f"Error: {e}")


async def example_performance_comparison():
    """Example of performance comparison."""
    print("\n=== Performance Comparison ===")
    
    lat, lon = 40.7128, -74.0060
    days = 2
    
    try:
        # Test API performance
        print("Testing API performance...")
        start_time = asyncio.get_event_loop().time()
        api_forecast = await fetch_forecast_api(lat, lon, days)
        api_time = asyncio.get_event_loop().time() - start_time
        print(f"API time: {api_time:.2f}s, Length: {len(api_forecast)} chars")
        
        # Test HTML performance
        print("Testing HTML performance...")
        start_time = asyncio.get_event_loop().time()
        html_forecast = await fetch_forecast_hybrid(lat, lon, days, mode='html')
        html_time = asyncio.get_event_loop().time() - start_time
        print(f"HTML time: {html_time:.2f}s, Length: {len(html_forecast)} chars")
        
        # Compare results
        print(f"API speedup: {html_time / api_time:.1f}x")
        print(f"Length difference: {abs(len(api_forecast) - len(html_forecast))} chars")
        
    except Exception as e:
        print(f"Error: {e}")


async def main():
    """Main function."""
    print("Weather.gov API Usage Examples")
    print("=" * 40)
    
    # Set up environment for testing
    os.environ['WEATHER_DEBUG_MODE'] = 'true'
    
    try:
        await example_basic_usage()
        await example_hybrid_mode()
        await example_direct_api_usage()
        await example_data_processing()
        await example_configuration()
        await example_error_handling()
        await example_caching()
        await example_performance_comparison()
        
        print("\n" + "=" * 40)
        print("All examples completed successfully!")
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        logger.exception("Unexpected error in examples")


if __name__ == "__main__":
    asyncio.run(main())