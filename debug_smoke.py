#!/usr/bin/env python3
"""
Debug script to test smoke detection.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'satcom_forecast'))

from forecast_parser import format_forecast, event_types

# Test widespread haze detection
test_text = "This Afternoon: Widespread haze. Mostly cloudy, with a high near 50. Southeast wind around 10 mph."

print("Testing widespread haze detection:")
print(f"Test text: {test_text}")
print()

# Check if widespread haze is in smoke keywords
print("Smoke keywords:", event_types['smoke'])
print("Contains 'widespread haze':", 'widespread haze' in event_types['smoke'])
print()

# Test compact format
compact_result = format_forecast(test_text, mode='compact')
print("Compact result:", compact_result)
print()

# Test summary format
summary_result = format_forecast(test_text, mode='summary')
print("Summary result:", summary_result) 