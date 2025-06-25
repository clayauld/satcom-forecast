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
                    # Don't add extra space if the part already starts with a space
                    if part.startswith(' '):
                        cleaned_lines.append(f"{current_period}{part}")
                    else:
                        cleaned_lines.append(f"{current_period} {part}")
                    current_period = ""
        else:
            cleaned_lines.append(line)
    
    result = '\n'.join(cleaned_lines)
    _LOGGER.debug("Cleaned forecast text, output length: %d characters", len(result))
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
    _LOGGER.debug("Formatting full forecast")
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
    
    _LOGGER.debug("Full forecast formatted, result length: %d characters", len(result))
    return result

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
            # Check for "slight chance" specifically
            if 'slight chance' in forecast_lower:
                return 10
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
    elif event == 'smoke':
        if 'heavy smoke' in forecast_lower or 'thick smoke' in forecast_lower or 'dense smoke' in forecast_lower:
            return 90
        elif 'smoke' in forecast_lower or 'smoky' in forecast_lower:
            return 80
        elif 'wildfire smoke' in forecast_lower or 'fire smoke' in forecast_lower:
            return 85
        else:
            return 70
    elif event == 'dense fog':
        return 90
    elif event == 'patchy fog':
        return 60
    elif event in ['tornado', 'hurricane', 'blizzard', 'ice storm', 'severe thunderstorm', 'high wind warning', 'flood warning']:
        return 90
    return 0

def check_significant_wind(forecast_text):
    """Check if wind speeds are significant (15+ mph) to warrant a wind event."""
    forecast_lower = forecast_text.lower()
    
    # Look for wind speed patterns
    wind_patterns = [
        r'(\d+) to (\d+) mph',  # Range like "15 to 25 mph"
        r'(\d+) mph',           # Single speed like "20 mph"
        r'gusts (?:up to|as high as|to) (\d+) mph',  # Gusts
        r'wind (\d+) to (\d+) mph',
        r'wind (\d+) mph'
    ]
    
    for pattern in wind_patterns:
        matches = re.findall(pattern, forecast_lower)
        for match in matches:
            if len(match) == 2:  # Range
                try:
                    min_speed = int(match[0])
                    max_speed = int(match[1])
                    if min_speed >= 15 or max_speed >= 15:
                        return True
                except ValueError:
                    continue
            elif len(match) == 1:  # Single speed
                try:
                    speed = int(match[0])
                    if speed >= 15:
                        return True
                except ValueError:
                    continue
    
    return False

def extract_temperature_info(forecast_text):
    """Extracts high and low temperature, returning a dict."""
    temps = {}
    high_match = re.search(r'high (?:near|around) (\d+)', forecast_text, re.IGNORECASE)
    if high_match:
        temps['high'] = f"H:{high_match.group(1)}°"

    low_match = re.search(r'low (?:around|near) (\d+)', forecast_text, re.IGNORECASE)
    if low_match:
        temps['low'] = f"L:{low_match.group(1)}°"
    
    return temps

def get_wind_abbr(direction_word):
    # Expanded abbreviations
    mapping = {
        "north": "N", "east": "E", "south": "S", "west": "W",
        "northeast": "NE", "southeast": "SE", "southwest": "SW", "northwest": "NW",
        "north northeast": "NNE", "east northeast": "ENE", "east southeast": "ESE", "south southeast": "SSE",
        "south southwest": "SSW", "west southwest": "WSW", "west northwest": "WNW", "north northwest": "NNW"
    }
    return mapping.get(direction_word.lower(), direction_word)

def extract_wind_info(forecast_text):
    """Extracts wind direction and speed, supporting various formats including gusts."""
    # Pattern for direction and speed, with optional gusts
    patterns = [
        r'(\b(?:north|south|east|west|northeast|southeast|southwest|northwest|north northeast|east northeast|east southeast|south southeast|south southwest|west southwest|west northwest|north northwest)\b) wind (\d+ to \d+|\d+) mph(?:, with gusts as high as (\d+) mph)?',
        r'wind (\d+ to \d+|\d+) mph from the (\b(?:north|south|east|west|northeast|southeast|southwest|northwest|north northeast|east northeast|east southeast|south southeast|south southwest|west southwest|west northwest|north northwest)\b)',
        r'(\b(?:north|south|east|west|northeast|southeast|southwest|northwest|north northeast|east northeast|east southeast|south southeast|south southwest|west southwest|west northwest|north northwest)\b) wind around (\d+) mph',
        r'becoming (\b(?:north|south|east|west|northeast|southeast|southwest|northwest)\b) (\d+ to \d+|\d+) mph'
    ]

    for pattern in patterns:
        match = re.search(pattern, forecast_text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if "from the" in pattern:
                direction, speed = get_wind_abbr(groups[1]), groups[0].replace(' to ', '-')
                return f"{direction}{speed}mph"
            if "becoming" in pattern:
                direction, speed = get_wind_abbr(groups[0]), groups[1].replace(' to ', '-')
                return f"{direction}{speed}mph"
            
            direction, speed = get_wind_abbr(groups[0]), groups[1].replace(' to ', '-')
            gusts = groups[2] if len(groups) > 2 and groups[2] else None
            
            wind_str = f"{direction}{speed}mph"
            if gusts:
                wind_str += f" (G:{gusts}mph)"
            return wind_str
    return None

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
        'smoke': ['smoke', 'smoky', 'wildfire smoke', 'fire smoke', 'smoke from fires'],
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
        'blizzard', 'ice storm', 'tornado', 'hurricane', 'severe thunderstorm', 'high wind warning', 'flood warning', 'dense fog', 'smoke'
    ]
    
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
                        # For wind events, only add if speeds are significant
                        if event == 'wind' and not check_significant_wind(forecast):
                            continue
                            
                        chance = infer_chance(event, forecast)
                        if chance > 0:
                            if event in extreme_events:
                                detected_events.append(f"🚨{event.title()}({chance}%)")
                                extreme_detected = True
                            else:
                                detected_events.append(f"{event.title()}({chance}%)")
                
                # Extract temperature and wind info
                temp_info = extract_temperature_info(forecast)
                wind_info = extract_wind_info(forecast)

                # Make a clean version of the forecast for display
                display_forecast = forecast

                # Remove verbose weather details from the display version
                temp_patterns = [
                    r'with a high (?:near|around) \d+',
                    r'with a low (?:around|near) \d+',
                    r'a high (?:near|around) \d+',
                    r'a low (?:around|near) \d+',
                    r'high (?:near|around) \d+',
                    r'low (?:around|near) \d+',
                ]
                for pattern in temp_patterns:
                    display_forecast = re.sub(pattern, '', display_forecast, flags=re.IGNORECASE)

                wind_patterns = [
                    r'(\b(?:north|south|east|west|northeast|southeast|southwest|northwest|north northeast|east northeast|east southeast|south southeast|south southwest|west southwest|west northwest|north northwest)\b) wind (\d+ to \d+|\d+) mph(?:, with gusts as high as (\d+) mph)?',
                    r'wind (\d+ to \d+|\d+) mph from the (\b(?:north|south|east|west|northeast|southeast|southwest|northwest|north northeast|east northeast|east southeast|south southeast|south southwest|west southwest|west northwest|north northwest)\b)',
                    r'(\b(?:north|south|east|west|northeast|southeast|southwest|northwest|north northeast|east northeast|east southeast|south southeast|south southwest|west southwest|west northwest|north northwest)\b) wind around (\d+) mph'
                ]
                for pattern in wind_patterns:
                    display_forecast = re.sub(pattern, '', display_forecast, flags=re.IGNORECASE)

                # General cleanup
                display_forecast = re.sub(r'Chance of precipitation is \d+%', '', display_forecast, flags=re.IGNORECASE)
                display_forecast = re.sub(r'\s+', ' ', display_forecast).strip()
                display_forecast = display_forecast.replace(' ,', ',').replace(' .', '.').strip(' ,.')
                if display_forecast.endswith(','):
                    display_forecast = display_forecast[:-1]
                
                # Take just the first sentence of the cleaned forecast
                first_sentence = display_forecast.split('.')[0] if '.' in display_forecast else display_forecast
                
                # Build details string
                details = []
                if temp_info:
                    if 'high' in temp_info:
                        details.append(temp_info['high'].replace("°", ""))
                    if 'low' in temp_info:
                        details.append(temp_info['low'].replace("°", ""))
                if wind_info:
                    details.append(wind_info)
                
                details_str = f" ({', '.join(details)})" if details else ""

                # Add weather event indicators if detected
                if detected_events:
                    events_str = ', '.join(detected_events)
                    result.append(f"{day.strip()}: {events_str}{details_str} | {first_sentence}")
                else:
                    result.append(f"{day.strip()}: {first_sentence}{details_str}")
                    
                _LOGGER.debug("Added compact forecast for %s: %s", day.strip(), first_sentence[:50] + "..." if len(first_sentence) > 50 else first_sentence)
            except ValueError:
                _LOGGER.debug("Failed to parse line for compact format: %s", line)
                continue
    
    final_result = '\n'.join(result)[:1500]
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
        'smoke': ['smoke', 'smoky', 'wildfire smoke', 'fire smoke', 'smoke from fires'],
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
        'blizzard', 'ice storm', 'tornado', 'hurricane', 'severe thunderstorm', 'high wind warning', 'flood warning', 'dense fog', 'smoke'
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

    def extract_temperature_info(forecast_text):
        """Extract high and low temperature information from forecast text."""
        temp_info = []
        
        # Look for high temperature patterns
        high_patterns = [
            r'with a high near (\d+)',
            r'high near (\d+)',
            r'high of (\d+)',
            r'high (\d+)',
            r'temperature near (\d+)'
        ]
        
        # Look for low temperature patterns
        low_patterns = [
            r'with a low around (\d+)',
            r'low around (\d+)',
            r'low of (\d+)',
            r'low (\d+)',
            r'temperature around (\d+)'
        ]
        
        for pattern in high_patterns:
            match = re.search(pattern, forecast_text.lower())
            if match:
                temp_info.append(f"H:{match.group(1)}")
                break
                
        for pattern in low_patterns:
            match = re.search(pattern, forecast_text.lower())
            if match:
                temp_info.append(f"L:{match.group(1)}")
                break
        
        return temp_info

    def extract_wind_info(forecast_text):
        """Extract wind direction and speed information from forecast text."""
        
        direction_map = {
            'north': 'N', 'northeast': 'NE', 'east': 'E', 'southeast': 'SE',
            'south': 'S', 'southwest': 'SW', 'west': 'W', 'northwest': 'NW',
            'variable': 'VAR'
        }

        def get_abbr(direction_word):
            return direction_map.get(direction_word.lower(), direction_word.title()[:1])

        forecast_lower = forecast_text.lower()
        
        # Special handling for 'becoming' phrases
        if 'becoming' in forecast_lower:
            after_becoming = forecast_lower.split('becoming', 1)[1].strip()
            print('DEBUG after_becoming:', repr(after_becoming))  # DEBUG
            wind_patterns = [
                r'(\w+)\s+(\d+) to (\d+) mph',  # direction followed by range
                r'(\w+) wind (\d+) to (\d+) mph',
                r'wind (\w+) (\d+) to (\d+) mph',
                r'(\w+) wind (?:around|near|up to|to) (\d+) mph',
                r'wind (?:from the )?(\w+) (?:around|near|up to|to) (\d+) mph',
                r'(\w+) wind (\d+) mph',
                r'wind (\w+) (\d+) mph',
                r'(\w+) (?:around|near|up to|to) (\d+) mph',  # direction around speed mph
                r'(\d+) to (\d+) mph(?:\W|$)',  # just a range with no direction, allow trailing words
                r'(\w+)',  # just direction
            ]
            for pattern in wind_patterns:
                match = re.search(pattern, after_becoming)
                if match:
                    if len(match.groups()) == 3:
                        direction = get_abbr(match.group(1))
                        speed_min = match.group(2)
                        speed_max = match.group(3)
                        return [f"{direction}{speed_min}-{speed_max}mph"]
                    elif len(match.groups()) == 2:
                        # If it's just a range with no direction
                        if pattern == r'(\d+) to (\d+) mph':
                            speed_min = match.group(1)
                            speed_max = match.group(2)
                            return [f"{speed_min}-{speed_max}mph"]
                        direction = get_abbr(match.group(1))
                        speed = match.group(2)
                        return [f"{direction}{speed}mph"]
                    elif len(match.groups()) == 1:
                        direction_word = match.group(1).lower()
                        if direction_word == 'calm': return ['Calm']
                        if direction_word == 'light': return ['Light']
                        direction = get_abbr(direction_word)
                        return [f"{direction}wind"]
            if 'calm' in after_becoming: return ["Calm"]
            if 'light' in after_becoming: return ["Light"]
            return []

        # Otherwise, extract the first matching wind pattern
        wind_patterns = [
            r'(\w+) wind (\d+) to (\d+) mph',
            r'wind (\w+) (\d+) to (\d+) mph',
            r'(\w+) wind (?:around|near|up to|to) (\d+) mph',
            r'wind (?:from the )?(\w+) (?:around|near|up to|to) (\d+) mph',
            r'(\w+) wind (\d+) mph',
            r'wind (\w+) (\d+) mph',
            r'(\w+) (?:around|near|up to|to) (\d+) mph',  # direction around speed mph
            r'(\w+)wind',
            r'(\w+) wind',
        ]
        for pattern in wind_patterns:
            match = re.search(pattern, forecast_lower)
            if match:
                if len(match.groups()) == 3:
                    direction = get_abbr(match.group(1))
                    speed_min = match.group(2)
                    speed_max = match.group(3)
                    return [f"{direction}{speed_min}-{speed_max}mph"]
                elif len(match.groups()) == 2:
                    direction = get_abbr(match.group(1))
                    speed = match.group(2)
                    return [f"{direction}{speed}mph"]
                elif len(match.groups()) == 1:
                    direction_word = match.group(1).lower()
                    if direction_word == 'calm': return ['Calm']
                    if direction_word == 'light': return ['Light']
                    direction = get_abbr(direction_word)
                    return [f"{direction}wind"]
                    
        if 'calm wind' in forecast_lower or 'calm' in forecast_lower:
            return ["Calm"]
        elif 'light wind' in forecast_lower:
            return ["Light"]
            
        return []

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
        elif event == 'smoke':
            if 'heavy smoke' in forecast_lower or 'thick smoke' in forecast_lower or 'dense smoke' in forecast_lower:
                return 90
            elif 'smoke' in forecast_lower or 'smoky' in forecast_lower:
                return 80
            elif 'wildfire smoke' in forecast_lower or 'fire smoke' in forecast_lower:
                return 85
            else:
                return 70
        elif event == 'dense fog':
            return 90
        elif event == 'patchy fog':
            return 60
        elif event in ['tornado', 'hurricane', 'blizzard', 'ice storm', 'severe thunderstorm', 'high wind warning', 'flood warning']:
            return 90
        return 0

    # Dictionary to store events by period (consolidating day/night)
    period_events_dict = {}
    
    event_name_map = {
        'rain': 'Rn', 'snow': 'Snw', 'sleet': 'Slt', 'freezing rain': 'FzRn',
        'wind': 'Wnd', 'hail': 'Hl', 'thunderstorm': 'ThSt', 'smoke': 'Smk', 'fog': 'Fg',
        'dense fog': 'DFg', 'patchy fog': 'PFg', 'tornado': 'TOR',
        'hurricane': 'HUR', 'blizzard': 'BLZ', 'ice storm': 'ISt',
        'severe thunderstorm': 'SThSt', 'high wind warning': 'HiWW',
        'flood warning': 'FldWng'
    }
    
    for line in lines:
        if ':' in line and any(day in line for day in ['Today', 'Tonight', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']):
            try:
                period, forecast = line.split(':', 1)
                forecast = forecast.strip().lower()
                detected = []
                
                # Extract weather events
                for event, keywords in event_types.items():
                    if any(kw in forecast for kw in keywords):
                        # For wind events, only add if speeds are significant
                        if event == 'wind' and not check_significant_wind(forecast):
                            continue
                            
                        chance = infer_chance(event, forecast)
                        if chance > 0:
                            # Format event with proper capitalization and probability
                            event_name = event_name_map.get(event, event.replace(' ', '').title()[:2])
                            if event in extreme_events:
                                detected.append(f"🚨{event_name}({chance}%)")
                            else:
                                detected.append(f"{event_name}({chance}%)")
                
                # Extract temperature and wind information
                temp_info = extract_temperature_info(forecast)
                wind_info = extract_wind_info(forecast)
                
                # Combine all information
                all_info = detected + temp_info + wind_info
                
                if all_info:
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
                        for new_event in all_info:
                            # Skip temperature and wind info for merging (they're unique)
                            if any(temp in new_event for temp in ['H:', 'L:']) or any(wind in new_event for wind in ['mph', 'wind']):
                                if not any(existing_temp in new_event for existing_temp in existing_events if any(temp in existing_temp for temp in ['H:', 'L:'])):
                                    if not any(existing_wind in new_event for existing_wind in existing_events if any(wind in existing_wind for wind in ['mph', 'wind'])):
                                        existing_events.append(new_event)
                                continue
                            
                            # Handle weather events with probabilities
                            if '(' in new_event and '%' in new_event:
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
                                # For events without probabilities, just add if not already present
                                if new_event not in existing_events:
                                    existing_events.append(new_event)
                    else:
                        period_events_dict[short_period_name] = all_info
                        
            except ValueError:
                continue

    # Convert dictionary to list format
    period_events = []
    for period, events in period_events_dict.items():
        if events:
            period_events.append(f"{period}: {','.join(events)}")

    # Limit to first 6 periods
    period_events = period_events[:6]
    
    # Join period events into a single summary, separated by newlines
    summary = '\n'.join(period_events)

    if not summary:
        summary = "No significant weather expected."
    return summary

def get_email_body_from_subject(subject):
    """
    Parses an email subject to extract the email body (coordinates and format).
    Example subjects:
    - "61.408,-148.444"
    - "61.408, -148.444"
    - "61.408, -148.444 summary"
    - "61.408, -148.444 compact"
    - "61.408, -148.444 full"
    """
    _LOGGER.debug("Parsing email subject: %s", subject)
    # Regex to find coordinates and an optional format keyword
    # It looks for two numbers (latitude and longitude) separated by a comma,
    # and an optional word (summary, compact, full) at the end.
    match = re.search(r'(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*(\w+)?', subject)
    
    if match:
        lat, lon, fmt = match.groups()
        if fmt:
            result = f"{lat},{lon} {fmt}"
        else:
            result = f"{lat},{lon}"
        _LOGGER.debug("Parsed subject to: %s", result)
        return result
    else:
        _LOGGER.debug("No coordinates found in subject")
        return None
