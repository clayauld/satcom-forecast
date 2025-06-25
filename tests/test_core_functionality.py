#!/usr/bin/env python3
"""
Core functionality tests for the SatCom Forecast integration.
Tests basic forecast fetching, parsing, and all three output formats.
"""

import asyncio
import sys
import os
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'custom_components', 'satcom_forecast'))

from forecast_fetcher import fetch_forecast
from forecast_parser import format_forecast, summarize_forecast

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_summary_with_temp_wind():
    """Test the summary format with temperature and wind information."""
    print("🌬️  Temperature and Wind Test")
    print("=" * 60)
    
    # Sample NOAA forecast text with temperature and wind information
    sample_text = """
Tonight: A chance of rain. Mostly cloudy, with a low around 46. Southeast wind 5 to 10 mph. Chance of precipitation is 30%.
Wednesday: Rain likely. Cloudy, with a high near 61. Southeast wind 5 to 10 mph. Chance of precipitation is 70%.
Wednesday Night: Rain. Cloudy, with a low around 45. East wind around 15 mph. Chance of precipitation is 80%.
Thursday: Rain. Cloudy, with a high near 61. East wind 5 to 10 mph. Chance of precipitation is 90%.
"""
    
    print("📝 Sample Text:")
    print(sample_text)
    
    summary = summarize_forecast(sample_text)
    
    print(f"\n📋 Summary Format Result:")
    print(summary)
    
    expected_summary = "Ton: Rn(30%),L:46,SE5-10mph\nWed: Rn(80%),H:61,SE5-10mph,L:45,E15mph\nThu: Rn(90%),H:61,E5-10mph"

    # Validate temperature and wind info
    assert summary == expected_summary
    
    print("   ✅ Summary contains correct weather events and percentages")
    print("-" * 60)
    return True

def test_real_world_summary():
    """Test the summary format with real-world forecast data that caused issues."""
    print("🌍 Real-World Summary Test")
    print("=" * 60)
    
    real_forecast_text = """
Tonight: Mostly cloudy, with a low around 46. Light and variable wind becoming southeast 5 to 10 mph in the evening.
Wednesday: A slight chance of showers after 4pm. Mostly cloudy, with a high near 61. Northwest wind around 5 mph.
Wednesday Night: A 20 percent chance of showers. Mostly cloudy, with a low around 45. Southeast wind around 15 mph.
Thursday: A 30 percent chance of rain. Mostly cloudy, with a high near 61. Southeast wind 5 to 10 mph.
Thursday Night: A 20 percent chance of rain. Mostly cloudy, with a low around 47. East wind around 10 mph. Breezy.
Friday: A 20 percent chance of rain. Mostly cloudy, with a high near 62. Northeast wind around 5 mph.
Friday Night: Mostly cloudy, with a low around 48.
Saturday: Partly sunny, with a high near 64.
Saturday Night: Mostly cloudy, with a low around 48.
Sunday: A 30 percent chance of rain. Mostly cloudy, with a high near 61.
Sunday Night: A 20 percent chance of rain. Mostly cloudy, with a low around 47.
Monday: A 30 percent chance of rain. Mostly cloudy, with a high near 61.
"""
    
    print("📝 Real Forecast Text:")
    print(real_forecast_text)
    
    summary = summarize_forecast(real_forecast_text)
    
    print(f"\n📋 Summary Format Result:")
    print(summary)
    
    expected_summary = (
        "Ton: L:46,SE5-10mph\n"
        "Wed: Rn(30%),H:61,NW5mph,L:45,SE15mph\n"
        "Thu: Rn(30%),H:61,SE5-10mph,L:47,E10mph\n"
        "Fri: Rn(30%),H:62,NE5mph,L:48\n"
        "Sat: H:64,L:48\n"
        "Sun: Rn(30%),H:61"
    )
    
    assert summary == expected_summary
    
    print("   ✅ Real-world summary test passed")
    print("-" * 60)
    return True

async def test_core_functionality():
    """Test core functionality: forecast fetching and all three formats."""
    print("🧪 Core Functionality Test")
    print("=" * 60)
    
    # Test location
    lat, lon = 61.11027, -149.79715  # Anchorage, Alaska
    print(f"📍 Test Location: Anchorage, Alaska")
    print(f"   Coordinates: {lat}, {lon}")
    print("-" * 50)
    
    # Step 1: Test forecast fetching
    print("🌤️  Step 1: Testing Forecast Fetching")
    print("-" * 40)
    raw_forecast = await fetch_forecast(lat, lon)
    
    if raw_forecast.startswith("NOAA error"):
        print(f"❌ Error fetching forecast: {raw_forecast}")
        return False
    
    print(f"✅ Raw forecast fetched successfully")
    print(f"   Length: {len(raw_forecast)} characters")
    print(f"   Preview: {raw_forecast[:200]}...")
    print()
    
    # Step 2: Test all three formats
    print("📝 Step 2: Testing All Formats")
    print("-" * 40)
    
    formats = ['summary', 'compact', 'full']
    results = {}
    
    for fmt in formats:
        print(f"\n🔍 Testing {fmt.upper()} format:")
        formatted = format_forecast(raw_forecast, fmt)
        results[fmt] = formatted
        
        print(f"   Length: {len(formatted)} characters")
        print(f"   Content: {formatted[:100]}{'...' if len(formatted) > 100 else ''}")
        
        # Validate format-specific requirements
        if fmt == 'summary':
            if len(formatted) > 0:
                print("   ✅ Summary format: Non-empty output")
            else:
                print("   ❌ Summary format: Empty output")
        elif fmt == 'compact':
            if len(formatted) > 0:
                print("   ✅ Compact format: Non-empty output")
            else:
                print("   ❌ Compact format: Empty output")
        elif fmt == 'full':
            if len(formatted) > 0:
                print("   ✅ Full format: Non-empty output")
            else:
                print("   ❌ Full format: Empty output")
    
    # Step 3: Validate format differences
    print(f"\n📊 Step 3: Format Comparison")
    print("-" * 40)
    print(f"   Summary: {len(results['summary'])} chars (concise)")
    print(f"   Compact: {len(results['compact'])} chars (detailed)")
    print(f"   Full: {len(results['full'])} chars (complete)")
    
    # Verify that formats are different
    if (len(results['summary']) < len(results['compact'])):
        print("   ✅ Format lengths are properly ordered (summary < compact)")
    else:
        print("   ⚠️  Format lengths may not be properly ordered")
    
    print(f"\n🎉 Core functionality test completed successfully!")
    return True

if __name__ == "__main__":
    print("🚀 Starting Core Functionality Test\n")
    # Run the temp/wind test first
    temp_wind_success = test_summary_with_temp_wind()
    
    # Run the real-world test
    real_world_success = test_real_world_summary()

    # Run the main core functionality test
    core_success = asyncio.run(test_core_functionality())
    
    if temp_wind_success and core_success and real_world_success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1) 