#!/usr/bin/env python3
"""
Multi-region test for the SatCom Forecast integration.
Tests forecast functionality across different geographic regions and weather conditions.
"""

import asyncio
import sys
import os
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'custom_components', 'satcom_forecast'))

from forecast_fetcher import fetch_forecast
from forecast_parser import format_forecast

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Comprehensive test locations covering different weather patterns
TEST_LOCATIONS = [
    (64.8378, -147.7164, 'Fairbanks, Alaska (Summer)', 'Wildfire smoke, rain, thunderstorms'),
    (61.11027, -149.79715, 'Anchorage, Alaska (Summer)', 'Coastal weather, rain, fog'),
    (25.7617, -80.1918, 'Miami, Florida (Hurricane Season)', 'Thunderstorms, hurricanes, wind'),
    (41.8781, -87.6298, 'Chicago, Illinois (Spring)', 'Rain, wind, possible snow'),
    (42.3601, -71.0589, 'Boston, Massachusetts (Summer)', 'Heat wave, thunderstorms, rain'),
    (34.0522, -118.2437, 'Los Angeles, California (Spring)', 'Fog, mild weather'),
    (40.7128, -74.0060, 'New York, NY (Spring)', 'Mixed conditions, coastal weather'),
    (39.7392, -104.9903, 'Denver, Colorado (Spring)', 'Mountain weather, variable conditions'),
]

def validate_summary_format(summary):
    """Validate summary format requirements."""
    issues = []
    
    if len(summary) > 200:
        issues.append(f"Summary too long: {len(summary)} chars (max 200)")
    
    if not summary or summary == "No significant weather expected.":
        issues.append("Summary is empty or shows no weather")
    
    # Check for duplicate periods
    parts = summary.split(' | ')
    periods = []
    for part in parts:
        if ':' in part:
            period = part.split(':')[0].strip()
            periods.append(period)
    
    duplicates = [p for p in set(periods) if periods.count(p) > 1]
    if duplicates:
        issues.append(f"Duplicate periods found: {duplicates}")
    
    return issues

async def test_multi_region():
    """Test forecast functionality across multiple regions."""
    print("🌎 Multi-Region Forecast Test")
    print("=" * 70)
    print("Testing forecast functionality across different geographic regions")
    print("and weather conditions to ensure robust performance.")
    print("=" * 70)
    
    results = {
        'success': 0,
        'failed': 0,
        'issues': []
    }
    
    for lat, lon, desc, expected_weather in TEST_LOCATIONS:
        print(f"\n📍 {desc}")
        print(f"   Coordinates: {lat}, {lon}")
        print(f"   Expected: {expected_weather}")
        print("-" * 60)
        
        try:
            # Fetch forecast
            raw_forecast = await fetch_forecast(lat, lon)
            if raw_forecast.startswith("NOAA error"):
                print(f"❌ Error fetching forecast: {raw_forecast}")
                results['failed'] += 1
                results['issues'].append(f"{desc}: NOAA API error")
                continue
            
            # Test all three formats
            formats = ['summary', 'compact', 'full']
            format_results = {}
            
            for fmt in formats:
                formatted = format_forecast(raw_forecast, fmt)
                format_results[fmt] = formatted
                
                if fmt == 'summary':
                    issues = validate_summary_format(formatted)
                    if issues:
                        results['issues'].extend([f"{desc} - {issue}" for issue in issues])
            
            # Display results
            print(f"📝 SUMMARY ({len(format_results['summary'])} chars):")
            print(f"   {format_results['summary']}")
            
            print(f"\n📝 COMPACT ({len(format_results['compact'])} chars):")
            print(f"   {format_results['compact'][:150]}{'...' if len(format_results['compact']) > 150 else ''}")
            
            print(f"\n📝 FULL ({len(format_results['full'])} chars):")
            print(f"   {format_results['full'][:200]}{'...' if len(format_results['full']) > 200 else ''}")
            
            results['success'] += 1
            print(f"✅ {desc}: All formats generated successfully")
            
        except Exception as e:
            print(f"❌ {desc}: Error - {e}")
            results['failed'] += 1
            results['issues'].append(f"{desc}: {e}")
        
        print("=" * 70)
    
    # Final summary
    print(f"\n📊 Test Results Summary")
    print("=" * 70)
    print(f"✅ Successful: {results['success']}/{len(TEST_LOCATIONS)}")
    print(f"❌ Failed: {results['failed']}/{len(TEST_LOCATIONS)}")
    
    if results['issues']:
        print(f"\n⚠️  Issues Found:")
        for issue in results['issues']:
            print(f"   • {issue}")
    else:
        print(f"\n🎉 No issues found!")
    
    print(f"\n🌍 Regions Tested:")
    for lat, lon, desc, expected in TEST_LOCATIONS:
        print(f"   • {desc} - {expected}")
    
    return results['failed'] == 0

if __name__ == "__main__":
    print("🚀 Starting Multi-Region Forecast Test\n")
    success = asyncio.run(test_multi_region())
    sys.exit(0 if success else 1) 