"""
API Data Models

This module defines data models for API responses and forecast data structures.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ForecastPeriod:
    """Represents a single forecast period."""

    name: str  # "Tonight", "Today", "Monday", etc.
    start_time: str  # ISO 8601 timestamp
    end_time: str  # ISO 8601 timestamp
    is_daytime: bool
    temperature: Optional[int] = None
    temperature_unit: str = "F"
    wind_speed: Optional[str] = None
    wind_direction: Optional[str] = None
    short_forecast: str = ""
    detailed_forecast: str = ""
    probability_of_precipitation: Optional[int] = None
    relative_humidity: Optional[Dict[str, Any]] = None
    heat_index: Optional[int] = None
    wind_chill: Optional[int] = None
    dewpoint: Optional[Dict[str, Any]] = None
    apparent_temperature: Optional[Dict[str, Any]] = None
    wind_gust: Optional[str] = None
    sky_cover: Optional[str] = None
    weather: Optional[List[Dict[str, Any]]] = None


@dataclass
class WeatherEvent:
    """Represents a detected weather event."""

    event_type: str  # "rain", "snow", "fog", etc.
    probability: int  # 0-100
    severity: str  # "low", "medium", "high", "extreme"
    description: str
    keywords: List[str] = field(default_factory=list)


@dataclass
class APIResponse:
    """Represents an API response with metadata."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    response_time: float = 0.0
    cached: bool = False


@dataclass
class GridPointInfo:
    """Represents NWS grid point information."""

    office: str
    grid_x: int
    grid_y: int
    forecast_office: str
    forecast_grid_data: str
    observation_stations: str
    relative_location: Dict[str, Any]
    forecast_zone: str
    county: str
    fire_weather_zone: str
    time_zone: str
    radar_station: str


@dataclass
class ForecastData:
    """Represents processed forecast data."""

    periods: List[ForecastPeriod]
    location: Optional[str] = None
    generated_at: Optional[str] = None
    valid_times: Optional[str] = None
    elevation: Optional[Dict[str, Any]] = None


@dataclass
class WeatherAlert:
    """Represents a weather alert."""

    id: str
    area_desc: str
    geocode: List[Dict[str, Any]]
    affected_zones: List[str]
    references: List[Dict[str, Any]]
    sent: str
    effective: str
    onset: Optional[str] = None
    expires: str = ""
    ends: Optional[str] = None
    status: str = ""
    message_type: str = ""
    category: str = ""
    severity: str = ""
    certainty: str = ""
    urgency: str = ""
    event: str = ""
    sender: str = ""
    sender_name: str = ""
    headline: str = ""
    description: str = ""
    instruction: str = ""
    response: str = ""


@dataclass
class ProcessedForecast:
    """Represents a fully processed forecast with all formats."""

    raw_data: Dict[str, Any]
    periods: List[ForecastPeriod]
    events: List[WeatherEvent]
    summary_format: str
    compact_format: str
    full_format: str
    location: Optional[str] = None
    generated_at: Optional[str] = None


def create_forecast_period_from_api(period_data: Dict[str, Any]) -> ForecastPeriod:
    """
    Create a ForecastPeriod from API response data.

    Args:
        period_data: Period data from API response

    Returns:
        ForecastPeriod object
    """
    return ForecastPeriod(
        name=period_data.get("name", ""),
        start_time=period_data.get("startTime", ""),
        end_time=period_data.get("endTime", ""),
        is_daytime=period_data.get("isDaytime", True),
        temperature=period_data.get("temperature"),
        temperature_unit=period_data.get("temperatureUnit", "F"),
        wind_speed=period_data.get("windSpeed"),
        wind_direction=period_data.get("windDirection"),
        short_forecast=period_data.get("shortForecast", ""),
        detailed_forecast=period_data.get("detailedForecast", ""),
        probability_of_precipitation=(
            period_data.get("probabilityOfPrecipitation", {}).get("value")
            if period_data.get("probabilityOfPrecipitation")
            else None
        ),
        relative_humidity=period_data.get("relativeHumidity"),
        heat_index=period_data.get("heatIndex"),
        wind_chill=period_data.get("windChill"),
        dewpoint=period_data.get("dewpoint"),
        apparent_temperature=period_data.get("apparentTemperature"),
        wind_gust=period_data.get("windGust"),
        sky_cover=period_data.get("skyCover"),
        weather=period_data.get("weather", []),
    )


def create_weather_event(
    event_type: str,
    probability: int,
    description: str,
    keywords: Optional[List[str]] = None,
) -> WeatherEvent:
    """
    Create a WeatherEvent with appropriate severity.

    Args:
        event_type: Type of weather event
        probability: Probability percentage (0-100)
        description: Description of the event
        keywords: Keywords that triggered the event

    Returns:
        WeatherEvent object
    """
    if keywords is None:
        keywords = []

    # Determine severity based on probability and event type
    if probability >= 90 or event_type in [
        "tornado",
        "hurricane",
        "blizzard",
        "ice storm",
    ]:
        severity = "extreme"
    elif probability >= 70 or event_type in [
        "severe thunderstorm",
        "high wind warning",
        "flood warning",
    ]:
        severity = "high"
    elif probability >= 40:
        severity = "medium"
    else:
        severity = "low"

    return WeatherEvent(
        event_type=event_type,
        probability=probability,
        severity=severity,
        description=description,
        keywords=keywords,
    )


def create_grid_point_from_api(data: Dict[str, Any]) -> GridPointInfo:
    """
    Create a GridPointInfo from API response data.

    Args:
        data: Grid point data from API response

    Returns:
        GridPointInfo object
    """
    properties = data.get("properties", {})

    return GridPointInfo(
        office=properties.get("cwa", ""),
        grid_x=properties.get("gridX", 0),
        grid_y=properties.get("gridY", 0),
        forecast_office=properties.get("forecastOffice", ""),
        forecast_grid_data=properties.get("forecastGridData", ""),
        observation_stations=properties.get("observationStations", ""),
        relative_location=properties.get("relativeLocation", {}),
        forecast_zone=properties.get("forecastZone", ""),
        county=properties.get("county", ""),
        fire_weather_zone=properties.get("fireWeatherZone", ""),
        time_zone=properties.get("timeZone", ""),
        radar_station=properties.get("radarStation", ""),
    )


def create_weather_alert_from_api(alert_data: Dict[str, Any]) -> WeatherAlert:
    """
    Create a WeatherAlert from API response data.

    Args:
        alert_data: Alert data from API response

    Returns:
        WeatherAlert object
    """
    properties = alert_data.get("properties", {})

    return WeatherAlert(
        id=alert_data.get("id", ""),
        area_desc=properties.get("areaDesc", ""),
        geocode=properties.get("geocode", {}).get("SAME", []),
        affected_zones=properties.get("affectedZones", []),
        references=properties.get("references", []),
        sent=properties.get("sent", ""),
        effective=properties.get("effective", ""),
        onset=properties.get("onset"),
        expires=properties.get("expires", ""),
        ends=properties.get("ends"),
        status=properties.get("status", ""),
        message_type=properties.get("messageType", ""),
        category=properties.get("category", ""),
        severity=properties.get("severity", ""),
        certainty=properties.get("certainty", ""),
        urgency=properties.get("urgency", ""),
        event=properties.get("event", ""),
        sender=properties.get("sender", ""),
        sender_name=properties.get("senderName", ""),
        headline=properties.get("headline", ""),
        description=properties.get("description", ""),
        instruction=properties.get("instruction", ""),
        response=properties.get("response", ""),
    )
