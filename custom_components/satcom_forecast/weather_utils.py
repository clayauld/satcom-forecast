"""
Weather Utility Functions Module

This module provides shared utility functions for weather data processing
and formatting. These functions are used by both the API data processor
and the API formatter to avoid code duplication.
"""

import logging
import re
from typing import List, Optional

_LOGGER = logging.getLogger(__name__)

# Import ForecastPeriod after defining EVENT_TYPES to avoid circular import
# This will be imported at the end of this section

# Weather event types and their keywords (ported from forecast_parser.py)
EVENT_TYPES = {
    "rain": ["rain", "showers", "precipitation", "drizzle", "sprinkles"],
    "snow": ["snow", "blizzard", "flurries", "snowfall"],
    "sleet": ["sleet"],
    "freezing rain": ["freezing rain", "ice", "icy"],
    "wind": ["windy", "gusts", "high wind", "breezy"],
    "hail": ["hail"],
    "thunderstorm": ["thunderstorm", "thunderstorms", "t-storm", "tstorms"],
    "smoke": [
        "smoke",
        "smoky",
        "wildfire smoke",
        "fire smoke",
        "smoke from fires",
        "smoke conditions",
        "smoke warning",
        "areas of smoke",
        "widespread haze",
    ],
    "fog": ["fog", "foggy", "mist"],
    "dense fog": ["dense fog", "thick fog", "heavy fog"],
    "patchy fog": ["patchy fog"],
    "tornado": ["tornado"],
    "hurricane": ["hurricane", "tropical storm"],
    "blizzard": ["blizzard"],
    "ice storm": ["ice storm"],
    "severe thunderstorm": ["severe thunderstorm", "severe t-storm", "severe tstorm"],
    "high wind warning": ["high wind warning"],
    "flood warning": ["flood warning", "flash flood warning"],
}

# Now import ForecastPeriod
from .api_models import ForecastPeriod


def check_significant_wind(period: ForecastPeriod) -> bool:
    """
    Check if wind speeds are significant (15+ mph).
    
    Args:
        period: ForecastPeriod object
        
    Returns:
        True if wind is significant
    """
    if not period.wind_speed:
        return False
        
    # Extract numeric wind speed
    wind_match = re.search(r'(\d+)', period.wind_speed)
    if wind_match:
        speed = int(wind_match.group(1))
        return speed >= 15
        
    return False


def infer_chance(event_type: str, forecast_text: str, period: ForecastPeriod) -> int:
    """
    Infer probability percentage for weather events.
    
    Args:
        event_type: Type of weather event
        forecast_text: Forecast text (lowercase)
        period: ForecastPeriod object
        
    Returns:
        Probability percentage (0-100)
    """
    # Use explicit precipitation probability if available
    if event_type == "rain" and period.probability_of_precipitation is not None:
        return period.probability_of_precipitation
        
    # Look for explicit percentages in forecast text
    percent_patterns = [
        r"(\d+)\s*percent",
        r"(\d+)%",
    ]
    
    # Track the best match (closest percentage to an event keyword)
    best_match = None
    best_distance = float('inf')
    
    for pattern in percent_patterns:
        # Use finditer to get match objects with positions
        for match_obj in re.finditer(pattern, forecast_text):
            percent_val = int(match_obj.group(1))
            match_pos = match_obj.start()
            
            # Check if this percentage is associated with the current event
            # Look for event keywords within 100 characters of the percentage
            context_start = max(0, match_pos - 100)
            context_end = min(len(forecast_text), match_pos + 100)
            context = forecast_text[context_start:context_end]
            
            event_keywords = EVENT_TYPES.get(event_type, [])
            for keyword in event_keywords:
                if keyword in context:
                    # Skip if "precipitation" is in context unless we're looking for rain
                    if "precipitation" in context and event_type != "rain":
                        continue
                    
                    # Find the position of the keyword in the full text
                    keyword_pos = forecast_text.find(keyword, context_start)
                    if keyword_pos != -1:
                        # Calculate distance between percentage and keyword
                        distance = abs(match_pos - keyword_pos)
                        
                        # Keep track of the closest match
                        if distance < best_distance:
                            best_distance = distance
                            best_match = percent_val
    
    # Return the best match if found
    if best_match is not None:
        return best_match
                    
    # Infer based on keywords
    if event_type == "rain":
        if "rain likely" in forecast_text or "showers likely" in forecast_text:
            return 70
        elif "scattered" in forecast_text:
            return 40
        elif "isolated" in forecast_text:
            return 20
        elif "chance" in forecast_text:
            return 30
        elif "drizzle" in forecast_text or "sprinkles" in forecast_text:
            return 25
        else:
            return 50
    elif event_type == "snow":
        if "blizzard" in forecast_text:
            return 90
        elif "snow likely" in forecast_text or "heavy snow" in forecast_text:
            return 70
        elif "flurries" in forecast_text:
            return 30
        elif "chance" in forecast_text:
            return 30
        else:
            return 50
    elif event_type in ["sleet", "freezing rain"]:
        if "likely" in forecast_text:
            return 60
        elif "chance" in forecast_text:
            return 30
        else:
            return 40
    elif event_type == "wind":
        if "high wind" in forecast_text or "gusts" in forecast_text:
            return 80
        elif "windy" in forecast_text:
            return 60
        elif "breezy" in forecast_text:
            return 40
        else:
            return 30
    elif event_type == "hail":
        if "likely" in forecast_text:
            return 60
        elif "chance" in forecast_text:
            return 30
        else:
            return 40
    elif event_type == "thunderstorm":
        if "severe" in forecast_text:
            return 80
        elif "likely" in forecast_text:
            return 60
        elif "chance" in forecast_text:
            return 30
        else:
            return 50
    elif event_type == "fog":
        if "dense fog" in forecast_text or "thick fog" in forecast_text or "heavy fog" in forecast_text:
            return 90
        elif "patchy fog" in forecast_text:
            return 60
        elif "fog" in forecast_text or "foggy" in forecast_text:
            return 70
        elif "mist" in forecast_text:
            return 30
        else:
            return 50
    elif event_type == "smoke":
        if "heavy smoke" in forecast_text or "thick smoke" in forecast_text or "dense smoke" in forecast_text:
            return 90
        elif "wildfire smoke" in forecast_text or "fire smoke" in forecast_text:
            return 75
        elif "smoke" in forecast_text or "smoky" in forecast_text:
            return 65
        else:
            return 50
    elif event_type == "dense fog":
        return 90
    elif event_type == "patchy fog":
        return 60
    elif event_type in ["tornado", "hurricane", "blizzard", "ice storm", "severe thunderstorm", "high wind warning", "flood warning"]:
        return 90
        
    return 0


def get_wind_direction_abbr(direction: str) -> str:
    """
    Convert wind direction to abbreviation.
    
    Args:
        direction: Wind direction string
        
    Returns:
        Abbreviated direction
    """
    direction_map = {
        "north": "N",
        "northeast": "NE",
        "east": "E",
        "southeast": "SE",
        "south": "S",
        "southwest": "SW",
        "west": "W",
        "northwest": "NW",
        "north northeast": "NNE",
        "east northeast": "ENE",
        "east southeast": "ESE",
        "south southeast": "SSE",
        "south southwest": "SSW",
        "west southwest": "WSW",
        "west northwest": "WNW",
        "north northwest": "NNW",
        "variable": "VAR",
    }
    
    return direction_map.get(direction.lower(), direction.upper()[:2])


def extract_temperature_info(period: ForecastPeriod) -> List[str]:
    """
    Extract temperature information from a forecast period.
    
    Args:
        period: ForecastPeriod object
        
    Returns:
        List of temperature strings
    """
    temp_info = []
    
    if period.temperature is not None:
        if period.is_daytime:
            temp_info.append(f"H:{period.temperature}°")
        else:
            temp_info.append(f"L:{period.temperature}°")
            
    return temp_info


def extract_wind_info(period: ForecastPeriod) -> List[str]:
    """
    Extract wind information from a forecast period.
    
    Args:
        period: ForecastPeriod object
        
    Returns:
        List containing formatted wind string, or empty list if no wind data
    """
    if not period.wind_speed or not period.wind_direction:
        return []
        
    # Convert wind direction to abbreviation
    direction_abbr = get_wind_direction_abbr(period.wind_direction)
    
    # Format wind speed (remove units if present)
    speed = period.wind_speed.replace(' mph', '').replace(' mph', '')
    speed = speed.replace(' to ', '-')
    
    # Handle wind gusts
    wind_str = f"{direction_abbr}{speed}mph"
    if period.wind_gust:
        gust_speed = period.wind_gust.replace(' mph', '').replace(' mph', '')
        wind_str += f" (G:{gust_speed}mph)"
        
    return [wind_str]


def filter_periods_by_days(periods: List[ForecastPeriod], days: Optional[int]) -> List[ForecastPeriod]:
    """
    Filter forecast periods based on days parameter.
    
    Args:
        periods: List of forecast periods
        days: Number of days to include
        
    Returns:
        Filtered list of periods
    """
    # Handle days parameter
    # days=0 means "Today" (current day)
    # days=1 means "Today + Tomorrow" (current day + 1 day)
    # So we want to select (days + 1) days
    
    if days is None:
        return periods
    
    _LOGGER.debug(f"filter_periods_by_days input days: {days}")
    
    target_days = 1

    if days is not None:
        # Ensure non-negative
        days_val = max(0, days)
        target_days = days_val + 1
        
    _LOGGER.debug(f"Calculated target_days: {target_days}")
        
    filtered_periods = []
    current_day_index = 0
    
    # Track if the previous period was a night period
    # We initialize to False, but we handle the first period specially if needed
    is_previous_night = False
    
    for i, period in enumerate(periods):
        # Check if we are transitioning from Night to Day
        # This marks the start of a new day (except for the very first period)
        if i > 0 and period.is_daytime and is_previous_night:
            current_day_index += 1
            
        # If we've reached the target number of days, stop
        if current_day_index >= target_days:
            break
            
        filtered_periods.append(period)
        
        # Update previous night status for next iteration
        is_previous_night = not period.is_daytime
        
    _LOGGER.debug(f"Returning {len(filtered_periods)} filtered periods (covered {current_day_index + (1 if filtered_periods else 0)} days)")
    return filtered_periods
