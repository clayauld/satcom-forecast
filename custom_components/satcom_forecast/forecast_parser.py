import re
import logging

_LOGGER = logging.getLogger(__name__)

def format_forecast(forecast_text, mode='summary'):
    _LOGGER.debug("Formatting forecast with mode: %s, input length: %d characters", mode, len(forecast_text))
    
    if mode == 'full':
        result = format_full_forecast(forecast_text)
    elif mode == 'compact':
        result = format_compact_forecast(forecast_text)
    elif mode == 'summary':
        result = summarize_forecast(forecast_text)
    else:
        result = forecast_text[:1000]
        _LOGGER.debug("Unknown mode '%s', using truncated original", mode)
    
    _LOGGER.debug("Forecast formatting completed, output length: %d characters", len(result))
    return result

def clean_forecast_text(text):
    """Clean and format the raw forecast text."""
    _LOGGER.debug("Cleaning forecast text, input length: %d characters", len(text))
    
    # Split by periods and clean up
    lines = text.strip().splitlines()
    _LOGGER.debug("Split into %d lines", len(lines))
    
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
                    cleaned_lines.append(f"{current_period} {part}")
                    current_period = ""
        else:
            cleaned_lines.append(line)
    
    result = '\n'.join(cleaned_lines)
    _LOGGER.debug("Cleaned forecast text, output length: %d characters", len(result))
    return result

def format_full_forecast(text):
    """Format the full forecast with proper line breaks."""
    _LOGGER.debug("Formatting full forecast")
    cleaned_text = clean_forecast_text(text)
    lines = cleaned_text.strip().splitlines()
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if ':' in line and any(day in line for day in ['Today', 'Tonight', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']):
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
    
    _LOGGER.debug("Full forecast formatted, result length: %d characters", len(result))
    return result

def format_compact_forecast(text):
    """Format a compact version of the forecast with enhanced weather detection."""
    _LOGGER.debug("Formatting compact forecast")
    cleaned_text = clean_forecast_text(text)
    lines = cleaned_text.strip().splitlines()
    result = []
    
    # Define event types and their keywords (same as summary)
    event_types = {
        'rain': ['rain', 'showers', 'precipitation', 'drizzle', 'sprinkles'],
        'snow': ['snow', 'blizzard', 'flurries', 'snowfall'],
        'sleet': ['sleet'],
        'freezing rain': ['freezing rain', 'ice', 'icy'],
        'wind': ['windy', 'gusts', 'high wind', 'breezy'],
        'hail': ['hail'],
        'thunderstorm': ['thunderstorm', 'thunderstorms', 't-storm', 'tstorms'],
        'fog': ['fog', 'foggy', 'haze', 'mist'],
        'dense fog': ['dense fog', 'thick fog', 'heavy fog'],
        'patchy fog': ['patchy fog'],
        'tornado': ['tornado'],
        'hurricane': ['hurricane', 'tropical storm'],
        'blizzard': ['blizzard'],
        'ice storm': ['ice storm'],
        'severe thunderstorm': ['severe thunderstorm', 'severe t-storm', 'severe tstorm'],
        'high wind warning': ['high wind warning'],
        'flood warning': ['flood warning', 'flash flood warning']
    }
    
    # List of extreme event keys
    extreme_events = [
        'blizzard', 'ice storm', 'tornado', 'hurricane', 'severe thunderstorm', 'high wind warning', 'flood warning', 'dense fog'
    ]
    
    def infer_chance(event, forecast_text):
        forecast_lower = forecast_text.lower()
        match = re.search(r'(\d+)%', forecast_text)
        if match:
            return int(match.group(1))
        if event == 'rain':
            if 'rain likely' in forecast_lower or 'showers likely' in forecast_lower:
                return 70
            elif 'scattered' in forecast_lower:
                return 40
            elif 'isolated' in forecast_lower:
                return 20
            elif 'chance' in forecast_lower:
                return 30
            elif 'drizzle' in forecast_lower or 'sprinkles' in forecast_lower:
                return 25
            else:
                return 50
        elif event == 'snow':
            if 'blizzard' in forecast_lower:
                return 90
            elif 'snow likely' in forecast_lower or 'heavy snow' in forecast_lower:
                return 70
            elif 'flurries' in forecast_lower:
                return 30
            elif 'chance' in forecast_lower:
                return 30
            else:
                return 50
        elif event == 'sleet' or event == 'freezing rain':
            if 'likely' in forecast_lower:
                return 60
            elif 'chance' in forecast_lower:
                return 30
            else:
                return 40
        elif event == 'wind':
            if 'high wind' in forecast_lower or 'gusts' in forecast_lower:
                return 80
            elif 'windy' in forecast_lower:
                return 60
            elif 'breezy' in forecast_lower:
                return 40
            else:
                return 30
        elif event == 'hail':
            if 'likely' in forecast_lower:
                return 60
            elif 'chance' in forecast_lower:
                return 30
            else:
                return 40
        elif event == 'thunderstorm':
            if 'severe' in forecast_lower:
                return 80
            elif 'likely' in forecast_lower:
                return 60
            elif 'chance' in forecast_lower:
                return 30
            else:
                return 50
        elif event == 'fog':
            if 'dense fog' in forecast_lower or 'thick fog' in forecast_lower or 'heavy fog' in forecast_lower:
                return 90
            elif 'patchy fog' in forecast_lower:
                return 60
            elif 'fog' in forecast_lower or 'foggy' in forecast_lower:
                return 70
            elif 'haze' in forecast_lower:
                return 40
            elif 'mist' in forecast_lower:
                return 30
            else:
                return 50
        elif event == 'dense fog':
            return 90
        elif event == 'patchy fog':
            return 60
        elif event in ['tornado', 'hurricane', 'blizzard', 'ice storm', 'severe thunderstorm', 'high wind warning', 'flood warning']:
            return 90
        return 0
    
    for line in lines:
        if ':' in line and any(day in line for day in ['Today', 'Tonight', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']):
            try:
                day, forecast = line.split(':', 1)
                forecast = forecast.strip()
                
                # Detect significant weather events
                forecast_lower = forecast.lower()
                detected_events = []
                extreme_detected = False
                
                for event, keywords in event_types.items():
                    if any(kw in forecast for kw in keywords):
                        chance = infer_chance(event, forecast)
                        if chance > 0:
                            if event in extreme_events:
                                detected_events.append(f"🚨{event.title()}")
                                extreme_detected = True
                            else:
                                detected_events.append(f"{event.title()}")
                
                # Simplify the forecast text (original logic)
                forecast = forecast.replace('with a high near', 'Hi')
                forecast = forecast.replace('with a low around', 'Lo')
                forecast = re.sub(r'Chance of precipitation is (\d+)%', r'POP: \1%', forecast)
                forecast = re.sub(r'Chance of precipitation (\d+)%', r'POP: \1%', forecast)
                
                # Take just the first sentence
                first_sentence = forecast.split('.')[0] if '.' in forecast else forecast
                
                # Add weather event indicators if detected
                if detected_events:
                    if extreme_detected:
                        result.append(f"{day.strip()}: 🚨 {', '.join(detected_events)} | {first_sentence}")
                    else:
                        result.append(f"{day.strip()}: {', '.join(detected_events)} | {first_sentence}")
                else:
                    result.append(f"{day.strip()}: {first_sentence}")
                    
                _LOGGER.debug("Added compact forecast for %s: %s", day.strip(), first_sentence[:50] + "..." if len(first_sentence) > 50 else first_sentence)
            except ValueError:
                _LOGGER.debug("Failed to parse line for compact format: %s", line)
                continue
    
    final_result = '\n'.join(result)[:1000]
    _LOGGER.debug("Compact forecast formatted, result length: %d characters", len(final_result))
    return final_result

def summarize_forecast(text):
    """Create a summary showing when significant weather events are expected, by period."""
    _LOGGER.debug("Creating forecast summary")
    cleaned_text = clean_forecast_text(text)
    lines = cleaned_text.strip().splitlines()

    # Define event types and their keywords
    event_types = {
        'rain': ['rain', 'showers', 'precipitation', 'drizzle', 'sprinkles'],
        'snow': ['snow', 'blizzard', 'flurries', 'snowfall'],
        'sleet': ['sleet'],
        'freezing rain': ['freezing rain', 'ice', 'icy'],
        'wind': ['windy', 'gusts', 'high wind', 'breezy'],
        'hail': ['hail'],
        'thunderstorm': ['thunderstorm', 'thunderstorms', 't-storm', 'tstorms'],
        'fog': ['fog', 'foggy', 'haze', 'mist'],
        'dense fog': ['dense fog', 'thick fog', 'heavy fog'],
        'patchy fog': ['patchy fog'],
        'tornado': ['tornado'],
        'hurricane': ['hurricane', 'tropical storm'],
        'blizzard': ['blizzard'],
        'ice storm': ['ice storm'],
        'severe thunderstorm': ['severe thunderstorm', 'severe t-storm', 'severe tstorm'],
        'high wind warning': ['high wind warning'],
        'flood warning': ['flood warning', 'flash flood warning']
    }
    # List of extreme event keys
    extreme_events = [
        'blizzard', 'ice storm', 'tornado', 'hurricane', 'severe thunderstorm', 'high wind warning', 'flood warning', 'dense fog'
    ]

    def short_period(period):
        # Shorten period names for brevity
        mapping = {
            'Tonight': 'Ton', 'Today': 'Tod',
            'Monday': 'Mon', 'Monday Night': 'MonN',
            'Tuesday': 'Tue', 'Tuesday Night': 'TueN',
            'Wednesday': 'Wed', 'Wednesday Night': 'WedN',
            'Thursday': 'Thu', 'Thursday Night': 'ThuN',
            'Friday': 'Fri', 'Friday Night': 'FriN',
            'Saturday': 'Sat', 'Saturday Night': 'SatN',
            'Sunday': 'Sun', 'Sunday Night': 'SunN',
        }
        for k, v in mapping.items():
            if period.strip().startswith(k):
                return v
        return period.strip()[:6]

    def infer_chance(event, forecast_text):
        forecast_lower = forecast_text.lower()
        match = re.search(r'(\d+)%', forecast_text)
        if match:
            return int(match.group(1))
        if event == 'rain':
            if 'rain likely' in forecast_lower or 'showers likely' in forecast_lower:
                return 70
            elif 'scattered' in forecast_lower:
                return 40
            elif 'isolated' in forecast_lower:
                return 20
            elif 'chance' in forecast_lower:
                return 30
            elif 'drizzle' in forecast_lower or 'sprinkles' in forecast_lower:
                return 25
            else:
                return 50
        elif event == 'snow':
            if 'blizzard' in forecast_lower:
                return 90
            elif 'snow likely' in forecast_lower or 'heavy snow' in forecast_lower:
                return 70
            elif 'flurries' in forecast_lower:
                return 30
            elif 'chance' in forecast_lower:
                return 30
            else:
                return 50
        elif event == 'sleet' or event == 'freezing rain':
            if 'likely' in forecast_lower:
                return 60
            elif 'chance' in forecast_lower:
                return 30
            else:
                return 40
        elif event == 'wind':
            if 'high wind' in forecast_lower or 'gusts' in forecast_lower:
                return 80
            elif 'windy' in forecast_lower:
                return 60
            elif 'breezy' in forecast_lower:
                return 40
            else:
                return 30
        elif event == 'hail':
            if 'likely' in forecast_lower:
                return 60
            elif 'chance' in forecast_lower:
                return 30
            else:
                return 40
        elif event == 'thunderstorm':
            if 'severe' in forecast_lower:
                return 80
            elif 'likely' in forecast_lower:
                return 60
            elif 'chance' in forecast_lower:
                return 30
            else:
                return 50
        elif event == 'fog':
            if 'dense fog' in forecast_lower or 'thick fog' in forecast_lower or 'heavy fog' in forecast_lower:
                return 90
            elif 'patchy fog' in forecast_lower:
                return 60
            elif 'fog' in forecast_lower or 'foggy' in forecast_lower:
                return 70
            elif 'haze' in forecast_lower:
                return 40
            elif 'mist' in forecast_lower:
                return 30
            else:
                return 50
        elif event == 'dense fog':
            return 90
        elif event == 'patchy fog':
            return 60
        elif event in ['tornado', 'hurricane', 'blizzard', 'ice storm', 'severe thunderstorm', 'high wind warning', 'flood warning']:
            return 90
        return 0

    # Dictionary to store events by period (consolidating day/night)
    period_events_dict = {}
    
    for line in lines:
        if ':' in line and any(day in line for day in ['Today', 'Tonight', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']):
            try:
                period, forecast = line.split(':', 1)
                forecast = forecast.strip().lower()
                detected = []
                for event, keywords in event_types.items():
                    if any(kw in forecast for kw in keywords):
                        chance = infer_chance(event, forecast)
                        if chance > 0:
                            # Format event with proper capitalization and probability
                            event_name = event.replace(' ', '').title()
                            if event in extreme_events:
                                detected.append(f"🚨{event_name} ({chance}%)")
                            else:
                                detected.append(f"{event_name} ({chance}%)")
                
                if detected:
                    # Get the base period name (without "Night")
                    base_period = period.strip()
                    if 'Night' in base_period:
                        # For night periods, use the base day name
                        base_period = base_period.replace(' Night', '')
                    
                    short_period_name = short_period(base_period)
                    
                    # If we already have events for this period, merge them
                    if short_period_name in period_events_dict:
                        existing_events = period_events_dict[short_period_name]
                        # Merge events, keeping the highest probability for duplicates
                        for new_event in detected:
                            event_name = new_event.split('(')[0]  # Get event name without probability
                            new_prob = int(new_event.split('(')[1].split('%')[0])
                            
                            # Check if we already have this event
                            found = False
                            for i, existing_event in enumerate(existing_events):
                                if existing_event.split('(')[0] == event_name:
                                    existing_prob = int(existing_event.split('(')[1].split('%')[0])
                                    # Keep the higher probability
                                    if new_prob > existing_prob:
                                        existing_events[i] = new_event
                                    found = True
                                    break
                            
                            if not found:
                                existing_events.append(new_event)
                    else:
                        period_events_dict[short_period_name] = detected
                        
            except ValueError:
                continue

    # Convert dictionary to list format
    period_events = []
    for period, events in period_events_dict.items():
        if events:
            period_events.append(f"{period}: {','.join(events)}")

    # Limit to first 6 periods to keep under 200 chars
    period_events = period_events[:6]
    
    # Join period events into a single summary, separated by newlines
    summary = '\n'.join(period_events)
    # Truncate to 200 chars if needed
    if len(summary) > 200:
        # Try to keep as many periods as possible
        parts = []
        total = 0
        for pe in period_events:
            if total + len(pe) + (1 if parts else 0) > 200:  # 1 for newline
                break
            parts.append(pe)
            total += len(pe) + (1 if parts else 0)
        summary = '\n'.join(parts)
        if len(summary) > 200:
            summary = summary[:197] + '...'
    if not summary:
        summary = "No significant weather expected."
    return summary
