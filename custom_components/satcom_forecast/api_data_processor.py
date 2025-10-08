"""
API Data Processor Module

This module processes raw API data into structured format compatible with
the existing forecast parser and formatter.
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from .api_models import (
    ForecastPeriod, 
    WeatherEvent, 
    ForecastData, 
    ProcessedForecast,
    create_forecast_period_from_api,
    create_weather_event
)

_LOGGER = logging.getLogger(__name__)

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

# Event name mapping (ported from forecast_parser.py)
EVENT_NAME_MAP = {
    "rain": "Rn",
    "snow": "Snw",
    "sleet": "Slt",
    "freezing rain": "FzRn",
    "wind": "Wnd",
    "hail": "Hl",
    "thunderstorm": "ThSt",
    "smoke": "Smk",
    "fog": "Fg",
    "dense fog": "DFg",
    "patchy fog": "PFg",
    "tornado": "TOR",
    "hurricane": "HUR",
    "blizzard": "BLZ",
    "ice storm": "ISt",
    "severe thunderstorm": "SThSt",
    "high wind warning": "HiWW",
    "flood warning": "FldWng",
}


class APIDataProcessor:
    """Processes raw API data into structured format."""
    
    def __init__(self):
        self.logger = _LOGGER
        
    def parse_forecast_periods(self, api_response: Dict[str, Any]) -> List[ForecastPeriod]:
        """
        Parse forecast periods from API response.
        
        Args:
            api_response: Raw API response data
            
        Returns:
            List of ForecastPeriod objects
        """
        try:
            properties = api_response.get('properties', {})
            periods_data = properties.get('periods', [])
            
            if not periods_data:
                self.logger.warning("No forecast periods found in API response")
                return []
                
            periods = []
            for period_data in periods_data:
                try:
                    period = create_forecast_period_from_api(period_data)
                    periods.append(period)
                    self.logger.debug(f"Parsed period: {period.name}")
                except Exception as e:
                    self.logger.error(f"Failed to parse period {period_data.get('name', 'unknown')}: {e}")
                    continue
                    
            self.logger.info(f"Successfully parsed {len(periods)} forecast periods")
            return periods
            
        except Exception as e:
            self.logger.error(f"Failed to parse forecast periods: {e}")
            return []
            
    def extract_weather_events(self, period: ForecastPeriod) -> List[WeatherEvent]:
        """
        Extract weather events from a forecast period.
        
        Args:
            period: ForecastPeriod object
            
        Returns:
            List of WeatherEvent objects
        """
        events = []
        forecast_text = period.detailed_forecast.lower()
        
        for event_type, keywords in EVENT_TYPES.items():
            if any(keyword in forecast_text for keyword in keywords):
                # For wind events, check if speeds are significant
                if event_type == "wind" and not self._check_significant_wind(period):
                    continue
                    
                probability = self._infer_chance(event_type, forecast_text, period)
                if probability > 0:
                    event = create_weather_event(
                        event_type=event_type,
                        probability=probability,
                        description=period.detailed_forecast,
                        keywords=[kw for kw in keywords if kw in forecast_text]
                    )
                    events.append(event)
                    self.logger.debug(f"Detected {event_type} event with {probability}% probability")
                    
        return events
        
    def extract_temperature_data(self, period: ForecastPeriod) -> Dict[str, str]:
        """
        Extract temperature information from a forecast period.
        
        Args:
            period: ForecastPeriod object
            
        Returns:
            Dictionary with temperature information
        """
        temp_info = {}
        
        if period.temperature is not None:
            if period.is_daytime:
                temp_info['high'] = f"H:{period.temperature}°"
            else:
                temp_info['low'] = f"L:{period.temperature}°"
                
        return temp_info
        
    def extract_wind_data(self, period: ForecastPeriod) -> Optional[str]:
        """
        Extract wind information from a forecast period.
        
        Args:
            period: ForecastPeriod object
            
        Returns:
            Formatted wind string or None
        """
        if not period.wind_speed or not period.wind_direction:
            return None
            
        # Convert wind direction to abbreviation
        direction_abbr = self._get_wind_direction_abbr(period.wind_direction)
        
        # Format wind speed (remove units if present)
        speed = period.wind_speed.replace(' mph', '').replace(' mph', '')
        
        # Handle wind gusts
        wind_str = f"{direction_abbr}{speed}mph"
        if period.wind_gust:
            gust_speed = period.wind_gust.replace(' mph', '').replace(' mph', '')
            wind_str += f" (G:{gust_speed}mph)"
            
        return wind_str
        
    def extract_precipitation_data(self, period: ForecastPeriod) -> Dict[str, Any]:
        """
        Extract precipitation information from a forecast period.
        
        Args:
            period: ForecastPeriod object
            
        Returns:
            Dictionary with precipitation information
        """
        precip_info = {}
        
        if period.probability_of_precipitation is not None:
            precip_info['probability'] = period.probability_of_precipitation
            
        # Extract precipitation type from weather field
        if period.weather:
            precip_types = []
            for weather_item in period.weather:
                if 'precipitation' in weather_item:
                    precip_types.append(weather_item['precipitation'])
            if precip_types:
                precip_info['types'] = precip_types
                
        return precip_info
        
    def process_forecast_data(self, api_response: Dict[str, Any]) -> ForecastData:
        """
        Process complete forecast data from API response.
        
        Args:
            api_response: Raw API response data
            
        Returns:
            Processed ForecastData object
        """
        periods = self.parse_forecast_periods(api_response)
        
        # Extract location information
        location = None
        if 'properties' in api_response:
            properties = api_response['properties']
            if 'relativeLocation' in properties:
                rel_loc = properties['relativeLocation']
                city = rel_loc.get('properties', {}).get('city', '')
                state = rel_loc.get('properties', {}).get('state', '')
                if city and state:
                    location = f"{city}, {state}"
                    
        # Extract generation time
        generated_at = api_response.get('properties', {}).get('generatedAt')
        
        # Extract valid times
        valid_times = api_response.get('properties', {}).get('validTimes')
        
        # Extract elevation
        elevation = api_response.get('properties', {}).get('elevation')
        
        return ForecastData(
            periods=periods,
            location=location,
            generated_at=generated_at,
            valid_times=valid_times,
            elevation=elevation
        )
        
    def _check_significant_wind(self, period: ForecastPeriod) -> bool:
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
        
    def _infer_chance(self, event_type: str, forecast_text: str, period: ForecastPeriod) -> int:
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
        
        for pattern in percent_patterns:
            matches = re.findall(pattern, forecast_text)
            for match in matches:
                percent_val = int(match)
                # Check if this percentage is associated with the current event
                context_start = max(0, forecast_text.find(match) - 100)
                context_end = min(len(forecast_text), forecast_text.find(match) + 100)
                context = forecast_text[context_start:context_end]
                
                event_keywords = EVENT_TYPES.get(event_type, [])
                if any(kw in context for kw in event_keywords):
                    if "precipitation" not in context or event_type == "rain":
                        return percent_val
                        
        # Infer based on keywords (ported from forecast_parser.py)
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
        
    def _get_wind_direction_abbr(self, direction: str) -> str:
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


# Convenience functions for backward compatibility
def parse_forecast_periods(api_response: Dict[str, Any]) -> List[ForecastPeriod]:
    """Parse forecast periods from API response."""
    processor = APIDataProcessor()
    return processor.parse_forecast_periods(api_response)


def extract_weather_events(period: ForecastPeriod) -> List[WeatherEvent]:
    """Extract weather events from a forecast period."""
    processor = APIDataProcessor()
    return processor.extract_weather_events(period)


def extract_temperature_data(period: ForecastPeriod) -> Dict[str, str]:
    """Extract temperature data from a forecast period."""
    processor = APIDataProcessor()
    return processor.extract_temperature_data(period)


def extract_wind_data(period: ForecastPeriod) -> Optional[str]:
    """Extract wind data from a forecast period."""
    processor = APIDataProcessor()
    return processor.extract_wind_data(period)