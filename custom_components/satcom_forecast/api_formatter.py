"""
API Output Formatter Module

This module provides output formatting for API data that produces identical
results to the existing HTML-based formatter.
"""

import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from . import weather_utils
from .api_data_processor import EVENT_NAME_MAP
from .api_models import ForecastPeriod, WeatherEvent
from .weather_utils import EVENT_TYPES

_LOGGER = logging.getLogger(__name__)


@dataclass
class FormattingResult:
    """Result of formatting operation."""

    summary: str
    compact: str
    full: str
    character_counts: Dict[str, int]


class APIFormatter:
    """Formats API data into Summary, Compact, and Full formats."""

    def __init__(self) -> None:
        self.logger = _LOGGER

    def format_forecast(
        self,
        periods: List[ForecastPeriod],
        events: List[WeatherEvent],
        mode: str = "summary",
        days: Optional[int] = None,
    ) -> str:
        """
        Format forecast data into the specified format.

        Args:
            periods: List of forecast periods
            events: List of weather events
            mode: Format mode ('summary', 'compact', 'full')
            days: Number of days to include

        Returns:
            Formatted forecast text
        """
        if mode == "full":
            return self.format_full_forecast(periods, events, days)
        elif mode == "compact":
            return self.format_compact_forecast(periods, events, days)
        elif mode == "summary":
            return self.format_summary_forecast(periods, events, days)
        else:
            self.logger.warning(f"Unknown mode '{mode}', using summary")
            return self.format_summary_forecast(periods, events, days)

    def format_full_forecast(
        self,
        periods: List[ForecastPeriod],
        events: List[WeatherEvent],
        days: Optional[int] = None,
    ) -> str:
        """
        Format forecast in full format (1100-2000+ characters).

        Args:
            periods: List of forecast periods
            events: List of weather events
            days: Number of days to include

        Returns:
            Full format forecast text
        """
        self.logger.debug("Formatting full forecast")

        # Filter periods by days if specified
        filtered_periods = weather_utils.filter_periods_by_days(periods, days)

        formatted_lines = []

        for period in filtered_periods:
            # Clean and format the forecast text
            forecast_text = self._clean_forecast_text(period.detailed_forecast)
            line = f"{period.name}: {forecast_text}"
            formatted_lines.append(line)

        result = "\n".join(formatted_lines)

        # Truncate if too long (2000+ characters)
        if len(result) > 2000:
            truncated = result[:2000]
            # Try to find a good break point
            last_period = truncated.rfind(".")
            last_newline = truncated.rfind("\n")
            break_point = max(last_period, last_newline)

            if break_point > 1800:
                result = result[: break_point + 1]
            else:
                result = result[:2000] + "..."

        self.logger.debug(
            f"Full forecast formatted, result length: {len(result)} characters"
        )
        return result

    def format_compact_forecast(
        self,
        periods: List[ForecastPeriod],
        events: List[WeatherEvent],
        days: Optional[int] = None,
    ) -> str:
        """
        Format forecast in compact format (400-1500 characters).

        Args:
            periods: List of forecast periods
            events: List of weather events
            days: Number of days to include

        Returns:
            Compact format forecast text
        """
        self.logger.debug("Formatting compact forecast")

        # Filter periods by days if specified
        filtered_periods = weather_utils.filter_periods_by_days(periods, days)

        result = []

        for period in filtered_periods:
            try:
                # Detect weather events for this period
                period_events = self._detect_period_events(period, events)

                # Extract temperature and wind info
                temp_info = weather_utils.extract_temperature_info(period)
                wind_info = weather_utils.extract_wind_info(period)

                # Clean forecast text for display
                display_forecast = self._clean_forecast_for_display(
                    period.detailed_forecast
                )

                # Take first sentence
                first_sentence = (
                    display_forecast.split(".")[0]
                    if "." in display_forecast
                    else display_forecast
                )

                # Build details string
                details = []
                if temp_info:
                    for item in temp_info:
                        if item.startswith("H:"):
                            details.append(item.replace("H:", "").replace("°", ""))
                        elif item.startswith("L:"):
                            details.append(item.replace("L:", "").replace("°", ""))

                if wind_info:
                    details.extend(wind_info)

                details_str = f" ({', '.join(details)})" if details else ""

                # Format events
                if period_events:
                    smoke_events = [
                        ev for ev in period_events if ev.startswith("🚨Smoke(")
                    ]
                    if smoke_events:
                        events_str = ", ".join(smoke_events)
                        result.append(
                            f"{period.name.strip()}: {events_str}{details_str} - Smoke"
                        )
                    else:
                        events_str = ", ".join(period_events)
                        result.append(
                            f"{period.name.strip()}: {events_str}{details_str} "
                            f"- {first_sentence}"
                        )
                else:
                    result.append(
                        f"{period.name.strip()}: {first_sentence}{details_str}"
                    )

            except Exception as e:
                self.logger.debug(f"Failed to format period {period.name}: {e}")
                continue

        # Join with newlines and limit length
        final_result = "\n".join(result)[:1500]
        self.logger.debug(
            f"Compact forecast formatted, result length: {len(final_result)} characters"
        )
        return final_result

    def format_summary_forecast(
        self,
        periods: List[ForecastPeriod],
        events: List[WeatherEvent],
        days: Optional[int] = None,
    ) -> str:
        """
        Format forecast in summary format (80-150 characters).

        Args:
            periods: List of forecast periods
            events: List of weather events
            days: Number of days to include

        Returns:
            Summary format forecast text
        """
        self.logger.debug("Formatting summary forecast")

        # Filter periods by days if specified
        filtered_periods = weather_utils.filter_periods_by_days(periods, days)

        # Group events by period
        period_events_dict: Dict[str, List[str]] = {}

        for period in filtered_periods:
            # Detect events for this period
            current_period_events = self._detect_period_events(period, events)

            # Extract temperature and wind info
            temp_info = weather_utils.extract_temperature_info(period)
            wind_info = weather_utils.extract_wind_info(period)

            # Combine all information
            all_info = current_period_events + temp_info + wind_info

            if all_info:
                # Get base period name
                base_period = self._get_day_name(period.name)
                short_period_name = self._shorten_period_name(base_period)

                # Merge with existing events for this period
                if short_period_name in period_events_dict:
                    existing_events = period_events_dict[short_period_name]
                    all_info = self._merge_period_events(existing_events, all_info)

                period_events_dict[short_period_name] = all_info

        # Convert to list format
        period_events: List[str] = []
        for period_name, events_list in period_events_dict.items():
            if events_list:
                period_events.append(f"{period_name}: {','.join(events_list)}")

        # Join with newlines
        summary = "\n".join(period_events)

        if not summary:
            summary = "No significant weather expected."

        self.logger.debug(
            f"Summary forecast formatted, result length: {len(summary)} characters"
        )
        return summary

    def _get_day_name(self, period_name: str) -> str:
        """Extract day name from period name."""
        if period_name in ["Today", "Tonight", "This Afternoon", "Overnight"]:
            return "Today"
        elif period_name.endswith(" Night"):
            return period_name[:-6]
        return period_name

    def _get_base_period_name(self, period_name: str) -> str:
        """Get base period name without 'Night' suffix."""
        if period_name.endswith(" Night"):
            return period_name[:-6]
        return period_name

    def _shorten_period_name(self, period_name: str) -> str:
        """Shorten period names for summary format."""
        period_map = {
            "This Afternoon": "Aft",
            "Today": "Tdy",
            "Tonight": "Tngt",
            "Overnight": "ON",
            "Monday": "Mon",
            "Tuesday": "Tue",
            "Wednesday": "Wed",
            "Thursday": "Thu",
            "Friday": "Fri",
            "Saturday": "Sat",
            "Sunday": "Sun",
        }
        return period_map.get(period_name, period_name[:3])

    def _detect_period_events(
        self, period: ForecastPeriod, all_events: List[WeatherEvent]
    ) -> List[str]:
        """Detect weather events for a specific period."""
        events = []
        forecast_lower = period.detailed_forecast.lower()

        for event_type, keywords in EVENT_TYPES.items():
            if any(keyword in forecast_lower for keyword in keywords):
                # For wind events, check if speeds are significant
                if event_type == "wind" and not weather_utils.check_significant_wind(
                    period
                ):
                    continue

                probability = weather_utils.infer_chance(
                    event_type, forecast_lower, period
                )
                if probability > 0:
                    event_name = EVENT_NAME_MAP.get(
                        event_type, event_type.replace(" ", "").title()[:2]
                    )

                    # Check if it's an extreme event
                    extreme_events = [
                        "blizzard",
                        "ice storm",
                        "tornado",
                        "hurricane",
                        "severe thunderstorm",
                        "high wind warning",
                        "flood warning",
                        "dense fog",
                        "smoke",
                    ]

                    if event_type in extreme_events:
                        events.append(f"🚨{event_name}({probability}%)")
                    else:
                        events.append(f"{event_name}({probability}%)")

        return events

    def _clean_forecast_text(self, text: str) -> str:
        """Clean and format forecast text."""
        # Normalize spaces
        text = re.sub(r" +", " ", text)
        text = re.sub(r"\. +", ". ", text)
        return text.strip()

    def _clean_forecast_for_display(self, text: str) -> str:
        """Clean forecast text for display in compact format."""
        # Remove temperature patterns
        temp_patterns = [
            r"with a high (?:near|around) \d+",
            r"with a low (?:around|near) \d+",
            r"a high (?:near|around) \d+",
            r"a low (?:around|near) \d+",
            r"high (?:near|around) \d+",
            r"low (?:around|near) \d+",
        ]
        for pattern in temp_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)

        # Remove wind patterns
        wind_patterns = [
            r"(\b(?:north|south|east|west|northeast|southeast|southwest|northwest)\b) "
            r"wind (\d+ to \d+|\d+) mph",
            r"wind (\d+ to \d+|\d+) mph from the "
            r"(\b(?:north|south|east|west|northeast|southeast|southwest|northwest)\b)",
        ]
        for pattern in wind_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)

        # Remove precipitation chance
        text = re.sub(r"Chance of precipitation is \d+%", "", text, flags=re.IGNORECASE)

        # Clean up spaces
        text = re.sub(r"\s+", " ", text).strip()
        text = text.replace(" ,", ",").replace(" .", ".").strip(" ,.")

        return text

    def _merge_period_events(self, existing: List[str], new: List[str]) -> List[str]:
        """Merge period events, keeping highest probability for duplicates."""
        merged = existing.copy()

        for new_event in new:
            if "(" in new_event and ")" in new_event:
                event_name = new_event.split("(")[0]
                new_prob = int(new_event.split("(")[1].split("%")[0])

                # Check if we already have this event
                found = False
                for i, existing_event in enumerate(merged):
                    if existing_event.split("(")[0] == event_name:
                        existing_prob = int(existing_event.split("(")[1].split("%")[0])
                        if new_prob > existing_prob:
                            merged[i] = new_event
                        found = True
                        break

                if not found:
                    merged.append(new_event)
            else:
                if new_event not in merged:
                    merged.append(new_event)

        return merged


# Convenience functions
def format_forecast_api(
    periods: List[ForecastPeriod],
    events: List[WeatherEvent],
    mode: str = "summary",
    days: Optional[int] = None,
) -> str:
    """Format forecast data using API formatter."""
    formatter = APIFormatter()
    return formatter.format_forecast(periods, events, mode, days)
