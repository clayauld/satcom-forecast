"""
API Output Formatter Module

This module provides output formatting for API data that produces identical
results to the existing HTML-based formatter.
"""

import logging
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .api_models import ForecastPeriod, WeatherEvent
from .api_data_processor import EVENT_TYPES, EVENT_NAME_MAP

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
    
    def __init__(self):
        self.logger = _LOGGER
        
    def format_forecast(self, 
                       periods: List[ForecastPeriod], 
                       events: List[WeatherEvent],
                       mode: str = "summary", 
                       days: Optional[int] = None) -> str:
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
            
    def format_full_forecast(self, 
                            periods: List[ForecastPeriod], 
                            events: List[WeatherEvent],
                            days: Optional[int] = None) -> str:
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
        filtered_periods = self._filter_periods_by_days(periods, days)
        
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
                result = result[:break_point + 1]
            else:
                result = result[:2000] + "..."
                
        self.logger.debug(f"Full forecast formatted, result length: {len(result)} characters")
        return result
        
    def format_compact_forecast(self, 
                               periods: List[ForecastPeriod], 
                               events: List[WeatherEvent],
                               days: Optional[int] = None) -> str:
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
        filtered_periods = self._filter_periods_by_days(periods, days)
        
        result = []
        extreme_events = [
            "blizzard", "ice storm", "tornado", "hurricane", 
            "severe thunderstorm", "high wind warning", "flood warning", 
            "dense fog", "smoke"
        ]
        
        for period in filtered_periods:
            try:
                # Detect weather events for this period
                period_events = self._detect_period_events(period, events)
                
                # Extract temperature and wind info
                temp_info = self._extract_temperature_info(period)
                wind_info = self._extract_wind_info(period)
                
                # Clean forecast text for display
                display_forecast = self._clean_forecast_for_display(period.detailed_forecast)
                
                # Take first sentence
                first_sentence = (
                    display_forecast.split(".")[0]
                    if "." in display_forecast
                    else display_forecast
                )
                
                # Build details string
                details = []
                if temp_info:
                    if "high" in temp_info:
                        details.append(temp_info["high"].replace("°", ""))
                    if "low" in temp_info:
                        details.append(temp_info["low"].replace("°", ""))
                if wind_info:
                    details.append(wind_info)
                    
                details_str = f" ({', '.join(details)})" if details else ""
                
                # Format events
                if period_events:
                    smoke_events = [ev for ev in period_events if ev.startswith("🚨Smoke(")]
                    if smoke_events:
                        events_str = ", ".join(smoke_events)
                        result.append(f"{period.name.strip()}: {events_str}{details_str} - Smoke")
                    else:
                        events_str = ", ".join(period_events)
                        result.append(f"{period.name.strip()}: {events_str}{details_str} - {first_sentence}")
                else:
                    result.append(f"{period.name.strip()}: {first_sentence}{details_str}")
                    
            except Exception as e:
                self.logger.debug(f"Failed to format period {period.name}: {e}")
                continue
                
        # Join with newlines and limit length
        final_result = "\n".join(result)[:1500]
        self.logger.debug(f"Compact forecast formatted, result length: {len(final_result)} characters")
        return final_result
        
    def format_summary_forecast(self, 
                               periods: List[ForecastPeriod], 
                               events: List[WeatherEvent],
                               days: Optional[int] = None) -> str:
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
        filtered_periods = self._filter_periods_by_days(periods, days)
        
        # Group events by period
        period_events_dict = {}
        extreme_events = [
            "blizzard", "ice storm", "tornado", "hurricane", 
            "severe thunderstorm", "high wind warning", "flood warning", 
            "dense fog", "smoke"
        ]
        
        for period in filtered_periods:
            # Detect events for this period
            period_events = self._detect_period_events(period, events)
            
            # Extract temperature and wind info
            temp_info = self._extract_temperature_info(period)
            wind_info = self._extract_wind_info(period)
            
            # Combine all information
            all_info = period_events + temp_info + wind_info
            
            if all_info:
                # Get base period name
                base_period = self._get_base_period_name(period.name)
                short_period_name = self._shorten_period_name(base_period)
                
                # Merge with existing events for this period
                if short_period_name in period_events_dict:
                    existing_events = period_events_dict[short_period_name]
                    all_info = self._merge_period_events(existing_events, all_info)
                    
                period_events_dict[short_period_name] = all_info
                
        # Convert to list format
        period_events = []
        for period, events_list in period_events_dict.items():
            if events_list:
                period_events.append(f"{period}: {','.join(events_list)}")
                
        # Join with newlines
        summary = "\n".join(period_events)
        
        if not summary:
            summary = "No significant weather expected."
            
        self.logger.debug(f"Summary forecast formatted, result length: {len(summary)} characters")
        return summary
        
    def _filter_periods_by_days(self, periods: List[ForecastPeriod], days: Optional[int]) -> List[ForecastPeriod]:
        """Filter periods based on days parameter."""
        if days is None or days <= 0:
            return periods
            
        # Group periods by day
        day_groups = {}
        for period in periods:
            day_name = self._get_day_name(period.name)
            if day_name not in day_groups:
                day_groups[day_name] = []
            day_groups[day_name].append(period)
            
        # Select the first N days
        selected_days = list(day_groups.keys())[:days]
        filtered_periods = []
        
        for day in selected_days:
            filtered_periods.extend(day_groups[day])
            
        return filtered_periods
        
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
            "Sunday": "Sun"
        }
        return period_map.get(period_name, period_name[:3])
        
    def _detect_period_events(self, period: ForecastPeriod, all_events: List[WeatherEvent]) -> List[str]:
        """Detect weather events for a specific period."""
        events = []
        forecast_lower = period.detailed_forecast.lower()
        
        for event_type, keywords in EVENT_TYPES.items():
            if any(keyword in forecast_lower for keyword in keywords):
                # For wind events, check if speeds are significant
                if event_type == "wind" and not self._check_significant_wind(period):
                    continue
                    
                probability = self._infer_chance(event_type, forecast_lower, period)
                if probability > 0:
                    event_name = EVENT_NAME_MAP.get(event_type, event_type.replace(" ", "").title()[:2])
                    
                    # Check if it's an extreme event
                    extreme_events = [
                        "blizzard", "ice storm", "tornado", "hurricane", 
                        "severe thunderstorm", "high wind warning", "flood warning", 
                        "dense fog", "smoke"
                    ]
                    
                    if event_type in extreme_events:
                        events.append(f"🚨{event_name}({probability}%)")
                    else:
                        events.append(f"{event_name}({probability}%)")
                        
        return events
        
    def _extract_temperature_info(self, period: ForecastPeriod) -> List[str]:
        """Extract temperature information from period."""
        temp_info = []
        
        if period.temperature is not None:
            if period.is_daytime:
                temp_info.append(f"H:{period.temperature}°")
            else:
                temp_info.append(f"L:{period.temperature}°")
                
        return temp_info
        
    def _extract_wind_info(self, period: ForecastPeriod) -> List[str]:
        """Extract wind information from period."""
        if not period.wind_speed or not period.wind_direction:
            return []
            
        # Convert wind direction to abbreviation
        direction_abbr = self._get_wind_direction_abbr(period.wind_direction)
        
        # Format wind speed
        speed = period.wind_speed.replace(' mph', '').replace(' mph', '')
        
        # Handle wind gusts
        wind_str = f"{direction_abbr}{speed}mph"
        if period.wind_gust:
            gust_speed = period.wind_gust.replace(' mph', '').replace(' mph', '')
            wind_str += f" (G:{gust_speed}mph)"
            
        return [wind_str]
        
    def _check_significant_wind(self, period: ForecastPeriod) -> bool:
        """Check if wind speeds are significant (15+ mph)."""
        if not period.wind_speed:
            return False
            
        wind_match = re.search(r'(\d+)', period.wind_speed)
        if wind_match:
            speed = int(wind_match.group(1))
            return speed >= 15
            
        return False
        
    def _infer_chance(self, event_type: str, forecast_text: str, period: ForecastPeriod) -> int:
        """Infer probability percentage for weather events."""
        # Use explicit precipitation probability if available
        if event_type == "rain" and period.probability_of_precipitation is not None:
            return period.probability_of_precipitation
            
        # Look for explicit percentages
        percent_patterns = [r"(\d+)\s*percent", r"(\d+)%"]
        
        for pattern in percent_patterns:
            matches = re.findall(pattern, forecast_text)
            for match in matches:
                percent_val = int(match)
                context_start = max(0, forecast_text.find(match) - 100)
                context_end = min(len(forecast_text), forecast_text.find(match) + 100)
                context = forecast_text[context_start:context_end]
                
                event_keywords = EVENT_TYPES.get(event_type, [])
                if any(kw in context for kw in event_keywords):
                    if "precipitation" not in context or event_type == "rain":
                        return percent_val
                        
        # Infer based on keywords (simplified version)
        if event_type == "rain":
            if "likely" in forecast_text:
                return 70
            elif "scattered" in forecast_text:
                return 40
            elif "isolated" in forecast_text:
                return 20
            elif "chance" in forecast_text:
                return 30
            else:
                return 50
        elif event_type == "snow":
            if "blizzard" in forecast_text:
                return 90
            elif "likely" in forecast_text:
                return 70
            elif "flurries" in forecast_text:
                return 30
            else:
                return 50
        elif event_type == "wind":
            if "high wind" in forecast_text or "gusts" in forecast_text:
                return 80
            elif "windy" in forecast_text:
                return 60
            else:
                return 30
        elif event_type == "fog":
            if "dense fog" in forecast_text:
                return 90
            elif "patchy fog" in forecast_text:
                return 60
            else:
                return 70
        elif event_type == "smoke":
            if "heavy smoke" in forecast_text:
                return 90
            else:
                return 65
        elif event_type in ["tornado", "hurricane", "blizzard", "ice storm"]:
            return 90
            
        return 0
        
    def _get_wind_direction_abbr(self, direction: str) -> str:
        """Convert wind direction to abbreviation."""
        direction_map = {
            "north": "N", "northeast": "NE", "east": "E", "southeast": "SE",
            "south": "S", "southwest": "SW", "west": "W", "northwest": "NW",
            "north northeast": "NNE", "east northeast": "ENE", "east southeast": "ESE",
            "south southeast": "SSE", "south southwest": "SSW", "west southwest": "WSW",
            "west northwest": "WNW", "north northwest": "NNW", "variable": "VAR"
        }
        return direction_map.get(direction.lower(), direction.upper()[:2])
        
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
            r"(\b(?:north|south|east|west|northeast|southeast|southwest|northwest)\b) wind (\d+ to \d+|\d+) mph",
            r"wind (\d+ to \d+|\d+) mph from the (\b(?:north|south|east|west|northeast|southeast|southwest|northwest)\b)",
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
def format_forecast_api(periods: List[ForecastPeriod], 
                       events: List[WeatherEvent],
                       mode: str = "summary", 
                       days: Optional[int] = None) -> str:
    """Format forecast data using API formatter."""
    formatter = APIFormatter()
    return formatter.format_forecast(periods, events, mode, days)