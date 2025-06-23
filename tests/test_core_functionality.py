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
from forecast_parser import format_forecast

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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
            if len(formatted) <= 200:
                print("   ✅ Summary format: Under 200 character limit")
            else:
                print("   ❌ Summary format: Over 200 character limit")
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
    if (len(results['summary']) < len(results['compact']) < len(results['full'])):
        print("   ✅ Format lengths are properly ordered (summary < compact < full)")
    else:
        print("   ⚠️  Format lengths may not be properly ordered")
    
    print(f"\n🎉 Core functionality test completed successfully!")
    return True

if __name__ == "__main__":
    print("🚀 Starting Core Functionality Test\n")
    success = asyncio.run(test_core_functionality())
    sys.exit(0 if success else 1) 