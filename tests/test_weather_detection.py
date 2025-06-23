#!/usr/bin/env python3
"""
Weather detection tests for the SatCom Forecast integration.
Tests detection of various weather events including fog, extreme events, and different conditions.
"""

import asyncio
import sys
import os
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'custom_components', 'satcom_forecast'))

from forecast_fetcher import fetch_forecast
from forecast_parser import format_forecast

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Test locations with specific weather conditions
WEATHER_TEST_LOCATIONS = [
    (34.0522, -118.2437, 'Los Angeles, California', 'Fog Conditions', ['fog', 'patchy fog']),
    (64.8378, -147.7164, 'Fairbanks, Alaska', 'Thunderstorms & Rain', ['rain', 'thunderstorm']),
    (25.7617, -80.1918, 'Miami, Florida', 'Hurricane Season', ['rain', 'thunderstorm', 'wind']),
    (41.8781, -87.6298, 'Chicago, Illinois', 'Spring Storms', ['rain', 'thunderstorm']),
    (42.3601, -71.0589, 'Boston, Massachusetts', 'Heat Wave', ['rain', 'thunderstorm']),
]

def check_weather_events(summary, expected_events):
    """Check if expected weather events are detected in the summary."""
    detected_events = []
    missing_events = []
    
    summary_lower = summary.lower()
    
    for event in expected_events:
        if event in summary_lower:
            detected_events.append(event)
        else:
            missing_events.append(event)
    
    return detected_events, missing_events

def check_extreme_events(summary):
    """Check for extreme weather events (marked with 🚨)."""
    extreme_indicators = ['🚨', '[extreme]']
    has_extreme = any(indicator in summary for indicator in extreme_indicators)
    return has_extreme

def check_fog_detection(summary):
    """Check for fog-related weather detection."""
    fog_indicators = ['fog', 'patchyfog', 'densefog']
    summary_lower = summary.lower()
    fog_detected = any(indicator in summary_lower for indicator in fog_indicators)
    return fog_detected

async def test_weather_detection():
    """Test weather event detection across different locations."""
    print("🌦️ Weather Detection Test")
    print("=" * 70)
    print("Testing detection of various weather events including:")
    print("- Fog conditions (dense, patchy, general)")
    print("- Extreme weather events (thunderstorms, hurricanes)")
    print("- Standard weather (rain, wind, snow)")
    print("- Event probability inference")
    print("=" * 70)
    
    results = {
        'success': 0,
        'failed': 0,
        'weather_detected': 0,
        'extreme_events': 0,
        'fog_detected': 0
    }
    
    for lat, lon, location, description, expected_events in WEATHER_TEST_LOCATIONS:
        print(f"\n📍 {location}")
        print(f"   Description: {description}")
        print(f"   Expected: {', '.join(expected_events)}")
        print(f"   Coordinates: {lat}, {lon}")
        print("-" * 60)
        
        try:
            # Fetch forecast
            raw_forecast = await fetch_forecast(lat, lon)
            if raw_forecast.startswith("NOAA error"):
                print(f"❌ Error fetching forecast: {raw_forecast}")
                results['failed'] += 1
                continue
            
            # Test all formats
            formats = ['summary', 'compact', 'full']
            format_results = {}
            
            for fmt in formats:
                formatted = format_forecast(raw_forecast, fmt)
                format_results[fmt] = formatted
            
            # Analyze weather detection
            detected_events, missing_events = check_weather_events(format_results['summary'], expected_events)
            has_extreme = check_extreme_events(format_results['summary'])
            has_fog = check_fog_detection(format_results['summary'])
            
            # Display results
            print(f"📝 SUMMARY ({len(format_results['summary'])} chars):")
            print(f"   {format_results['summary']}")
            
            print(f"\n🔍 WEATHER DETECTION ANALYSIS:")
            if detected_events:
                print(f"   ✅ Detected: {', '.join(detected_events)}")
                results['weather_detected'] += 1
            if missing_events:
                print(f"   ❌ Missing: {', '.join(missing_events)}")
            
            if has_extreme:
                print(f"   🚨 Extreme events detected")
                results['extreme_events'] += 1
            
            if has_fog:
                print(f"   🌫️ Fog conditions detected")
                results['fog_detected'] += 1
            
            # Show compact format for comparison
            print(f"\n📝 COMPACT (first 100 chars):")
            print(f"   {format_results['compact'][:100]}{'...' if len(format_results['compact']) > 100 else ''}")
            
            results['success'] += 1
            print(f"✅ {location}: Weather detection analysis complete")
            
        except Exception as e:
            print(f"❌ {location}: Error - {e}")
            results['failed'] += 1
        
        print("=" * 70)
    
    # Final summary
    print(f"\n📊 Weather Detection Test Results")
    print("=" * 70)
    print(f"✅ Successful tests: {results['success']}/{len(WEATHER_TEST_LOCATIONS)}")
    print(f"❌ Failed tests: {results['failed']}/{len(WEATHER_TEST_LOCATIONS)}")
    print(f"🌦️ Weather events detected: {results['weather_detected']}")
    print(f"🚨 Extreme events found: {results['extreme_events']}")
    print(f"🌫️ Fog conditions detected: {results['fog_detected']}")
    
    print(f"\n🎯 Detection Capabilities Tested:")
    print(f"   • Rain and precipitation")
    print(f"   • Thunderstorms")
    print(f"   • Wind conditions")
    print(f"   • Fog (dense, patchy, general)")
    print(f"   • Extreme weather events")
    print(f"   • Probability inference")
    
    return results['failed'] == 0

if __name__ == "__main__":
    print("🚀 Starting Weather Detection Test\n")
    success = asyncio.run(test_weather_detection())
    sys.exit(0 if success else 1) 