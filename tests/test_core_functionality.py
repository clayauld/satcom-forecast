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
    sample_text = """NWS Forecast for: Knik Heights AK
Tonight: Showers likely, mainly before 10pm. Mostly cloudy, with a low around 47. West wind around 5 mph becoming calm in the evening. Chance of precipitation is 60%.
Tuesday: Scattered showers, mainly after 10am. Partly sunny, with a high near 58. Calm wind becoming west around 5 mph in the afternoon. Chance of precipitation is 30%.
Tuesday Night: Scattered showers. Mostly cloudy, with a low around 45. West wind around 5 mph becoming calm. Chance of precipitation is 30%.
Wednesday: Rain likely, mainly after 10am. Cloudy, with a high near 55. Southeast wind 5 to 10 mph. Chance of precipitation is 70%.
Wednesday Night: Rain. Low around 42. East wind 10 to 15 mph. Chance of precipitation is 80%.
Thursday: Rain and snow likely. High near 48. North wind 15 to 20 mph. Chance of precipitation is 60%."""
    
    print("📝 Sample Text:")
    print(sample_text)
    
    summary = summarize_forecast(sample_text)
    
    print(f"\n📋 Summary Format Result:")
    print(summary)
    
    # Validate temperature and wind info
    assert 'Rn(60%)' in summary, "Weather event (Rn(60%)) not found"
    assert 'Hi58°' in summary, "High temperature (Hi58°) not found"
    assert 'Lo47°' in summary, "Low temperature (Lo47°) not found"
    assert 'W5mph' in summary, "Wind info (W5mph) not found"
    assert 'SE5-10mph' in summary, "Wind info (SE5-10mph) not found"
    
    print("\n✅ Temperature and wind information correctly extracted.")
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
    
    # Run the main core functionality test
    core_success = asyncio.run(test_core_functionality())
    
    if temp_wind_success and core_success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1) 