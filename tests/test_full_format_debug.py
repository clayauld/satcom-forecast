#!/usr/bin/env python3
"""
Debug script to test full format processing and identify extra spaces.
"""

import re

def clean_forecast_text(text):
    """Clean and format the raw forecast text."""
    print(f"Cleaning forecast text, input length: {len(text)} characters")
    
    # Split by periods and clean up
    lines = text.strip().splitlines()
    print(f"Split into {len(lines)} lines")
    
    cleaned_lines = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Handle the case where periods are concatenated
        if ':' in line:
            # Split by common period patterns
            parts = re.split(r'(Today:|Tonight:|Monday:|Monday Night:|Tuesday:|Tuesday Night:|Wednesday:|Wednesday Night:|Thursday:|Thursday Night:|Friday:|Friday Night:|Saturday:|Saturday Night:|Sunday:)', line)
            
            current_period = ""
            for part in parts:
                part = part.strip()
                if part.endswith(':') and any(day in part for day in ['Today', 'Tonight', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']):
                    current_period = part
                elif part and current_period:
                    # Don't add extra space if the part already starts with a space
                    if part.startswith(' '):
                        cleaned_lines.append(f"{current_period}{part}")
                    else:
                        cleaned_lines.append(f"{current_period} {part}")
                    current_period = ""
        else:
            cleaned_lines.append(line)
    
    result = '\n'.join(cleaned_lines)
    print(f"Cleaned forecast text, output length: {len(result)} characters")
    return result

def normalize_spaces(text):
    """Normalize spaces in text - replace multiple spaces with single spaces."""
    # Replace multiple spaces with single spaces
    text = re.sub(r' +', ' ', text)
    # Ensure proper spacing after periods (single space)
    text = re.sub(r'\. +', '. ', text)
    return text

def format_full_forecast(text):
    """Format the full forecast with proper line breaks."""
    print("Formatting full forecast")
    cleaned_text = clean_forecast_text(text)
    lines = cleaned_text.strip().splitlines()
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if ':' in line and any(day in line for day in ['Today', 'Tonight', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']):
            # Normalize spaces in the line
            line = normalize_spaces(line)
            formatted_lines.append(line)
    
    result = '\n'.join(formatted_lines)
    
    # If result is longer than 2000 chars, truncate at a complete sentence
    if len(result) > 2000:
        # Try to find a good break point near 2000 characters
        truncated = result[:2000]
        # Look for the last complete sentence
        last_period = truncated.rfind('.')
        last_newline = truncated.rfind('\n')
        break_point = max(last_period, last_newline)
        
        if break_point > 1800:  # Only use if we have a reasonable break point
            result = result[:break_point + 1]
        else:
            result = result[:2000] + "..."
    
    print(f"Full forecast formatted, result length: {len(result)} characters")
    return result

def test_full_format():
    """Test the full format processing."""
    print("🔍 Testing Full Format Processing")
    print("=" * 50)
    
    # Sample NOAA forecast text (similar to what we get from the API)
    sample_text = """NWS Forecast for: Knik Heights AK
Tonight:Showers likely, mainly before 10pm.  Mostly cloudy, with a low around 47. West wind around 5 mph becoming calm  in the evening.  Chance of precipitation is 60%.
Tuesday:Scattered showers, mainly after 10am.  Partly sunny, with a high near 58. Calm wind becoming west around 5 mph in the afternoon.  Chance of precipitation is 30%.
Tuesday Night:Scattered showers.  Mostly cloudy, with a low around 45. West wind around 5 mph becoming calm.  Chance of precipitation is 30%."""
    
    print(f"📝 Sample Text (first 200 chars):")
    print(repr(sample_text[:200]))
    print(sample_text[:200])
    
    print(f"\n🧹 Cleaned Text (first 200 chars):")
    cleaned = clean_forecast_text(sample_text)
    print(repr(cleaned[:200]))
    print(cleaned[:200])
    
    print(f"\n📋 Full Format (first 200 chars):")
    full_format = format_full_forecast(sample_text)
    print(repr(full_format[:200]))
    print(full_format[:200])
    
    # Look for double spaces
    print(f"\n🔍 Checking for double spaces:")
    double_spaces = full_format.count('  ')
    print(f"Double spaces found: {double_spaces}")
    
    if double_spaces > 0:
        # Find the positions of double spaces
        matches = re.finditer(r'  +', full_format)
        for i, match in enumerate(matches):
            start = max(0, match.start() - 20)
            end = min(len(full_format), match.end() + 20)
            context = full_format[start:end]
            print(f"  Double space {i+1}: '{context}'")
    
    # Show the full result
    print(f"\n📋 Full Result:")
    print(full_format)

if __name__ == "__main__":
    test_full_format() 