"""
API Data Processor Module

This module processes raw API data into structured format compatible with
the existing forecast parser and formatter.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from . import weather_utils
from .api_models import (
    ForecastData,
    ForecastPeriod,
    WeatherEvent,
    create_forecast_period_from_api,
    create_weather_event,
)
from .weather_utils import EVENT_TYPES

_LOGGER = logging.getLogger(__name__)

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

    def parse_forecast_periods(
        self, api_response: Dict[str, Any]
    ) -> List[ForecastPeriod]:
        """
        Parse forecast periods from API response.

        Args:
            api_response: Raw API response data

        Returns:
            List of ForecastPeriod objects
        """
        try:
            properties = api_response.get("properties", {})
            periods_data = properties.get("periods", [])

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
                    self.logger.error(
                        f"Failed to parse period {period_data.get('name', 'unknown')}: {e}"
                    )
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
                if event_type == "wind" and not weather_utils.check_significant_wind(
                    period
                ):
                    continue

                probability = weather_utils.infer_chance(
                    event_type, forecast_text, period
                )
                if probability > 0:
                    event = create_weather_event(
                        event_type=event_type,
                        probability=probability,
                        description=period.detailed_forecast,
                        keywords=[kw for kw in keywords if kw in forecast_text],
                    )
                    events.append(event)
                    self.logger.debug(
                        f"Detected {event_type} event with {probability}% probability"
                    )

        return events

    def extract_temperature_data(self, period: ForecastPeriod) -> Dict[str, str]:
        """
        Extract temperature information from a forecast period.

        Args:
            period: ForecastPeriod object

        Returns:
            Dictionary with temperature information
        """
        temp_list = weather_utils.extract_temperature_info(period)
        temp_info = {}

        for item in temp_list:
            if item.startswith("H:"):
                temp_info["high"] = item
            elif item.startswith("L:"):
                temp_info["low"] = item

        return temp_info

    def extract_wind_data(self, period: ForecastPeriod) -> Optional[str]:
        """
        Extract wind information from a forecast period.

        Args:
            period: ForecastPeriod object

        Returns:
            Formatted wind string or None
        """
        wind_list = weather_utils.extract_wind_info(period)
        return wind_list[0] if wind_list else None

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
            precip_info["probability"] = period.probability_of_precipitation

        # Extract precipitation type from weather field
        if period.weather:
            precip_types = []
            for weather_item in period.weather:
                if "precipitation" in weather_item:
                    precip_types.append(weather_item["precipitation"])
            if precip_types:
                precip_info["types"] = precip_types

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
        if "properties" in api_response:
            properties = api_response["properties"]
            if "relativeLocation" in properties:
                rel_loc = properties["relativeLocation"]
                city = rel_loc.get("properties", {}).get("city", "")
                state = rel_loc.get("properties", {}).get("state", "")
                if city and state:
                    location = f"{city}, {state}"

        # Extract generation time
        generated_at = api_response.get("properties", {}).get("generatedAt")

        # Extract valid times
        valid_times = api_response.get("properties", {}).get("validTimes")

        # Extract elevation
        elevation = api_response.get("properties", {}).get("elevation")

        return ForecastData(
            periods=periods,
            location=location,
            generated_at=generated_at,
            valid_times=valid_times,
            elevation=elevation,
        )


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
