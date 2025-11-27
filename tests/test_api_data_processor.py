"""
Unit tests for API data processor module.
"""

import pytest

from custom_components.satcom_forecast import weather_utils
from custom_components.satcom_forecast.api_data_processor import APIDataProcessor
from custom_components.satcom_forecast.api_models import ForecastPeriod


class TestAPIDataProcessor:
    """Test cases for APIDataProcessor."""

    @pytest.fixture
    def processor(self):
        """Create a test processor instance."""
        return APIDataProcessor()

    @pytest.fixture
    def sample_api_response(self):
        """Sample API response data."""
        return {
            "properties": {
                "periods": [
                    {
                        "name": "Today",
                        "startTime": "2024-01-01T06:00:00-05:00",
                        "endTime": "2024-01-01T18:00:00-05:00",
                        "isDaytime": True,
                        "temperature": 75,
                        "temperatureUnit": "F",
                        "windSpeed": "10 to 15 mph",
                        "windDirection": "NW",
                        "shortForecast": "Sunny",
                        "detailedForecast": (
                            "Sunny with a high near 75. Northwest wind 10 to 15 mph."
                        ),
                        "probabilityOfPrecipitation": {"value": 0},
                        "relativeHumidity": {"value": 45},
                        "heatIndex": None,
                        "windChill": None,
                        "dewpoint": {"value": 50},
                        "apparentTemperature": None,
                        "windGust": None,
                        "skyCover": "Clear",
                        "weather": [],
                    },
                    {
                        "name": "Tonight",
                        "startTime": "2024-01-01T18:00:00-05:00",
                        "endTime": "2024-01-02T06:00:00-05:00",
                        "isDaytime": False,
                        "temperature": 55,
                        "temperatureUnit": "F",
                        "windSpeed": "5 to 10 mph",
                        "windDirection": "NW",
                        "shortForecast": "Clear",
                        "detailedForecast": (
                            "Clear with a low around 55. Northwest wind 5 to 10 mph."
                        ),
                        "probabilityOfPrecipitation": {"value": 0},
                        "relativeHumidity": {"value": 60},
                        "heatIndex": None,
                        "windChill": None,
                        "dewpoint": {"value": 45},
                        "apparentTemperature": None,
                        "windGust": None,
                        "skyCover": "Clear",
                        "weather": [],
                    },
                ]
            }
        }

    def test_parse_forecast_periods_success(self, processor, sample_api_response):
        """Test successful parsing of forecast periods."""
        periods = processor.parse_forecast_periods(sample_api_response)

        assert len(periods) == 2
        assert periods[0].name == "Today"
        assert periods[0].temperature == 75
        assert periods[0].is_daytime is True
        assert periods[1].name == "Tonight"
        assert periods[1].temperature == 55
        assert periods[1].is_daytime is False

    def test_parse_forecast_periods_empty(self, processor):
        """Test parsing with empty periods."""
        response = {"properties": {"periods": []}}
        periods = processor.parse_forecast_periods(response)
        assert len(periods) == 0

    def test_parse_forecast_periods_missing_properties(self, processor):
        """Test parsing with missing properties."""
        response = {"invalid": "data"}
        periods = processor.parse_forecast_periods(response)
        assert len(periods) == 0

    def test_extract_weather_events_rain(self, processor):
        """Test weather event extraction for rain."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            detailed_forecast=(
                "Rain likely with a high near 70. Chance of precipitation is 80%."
            ),
        )

        events = processor.extract_weather_events(period)
        assert len(events) == 1
        assert events[0].event_type == "rain"
        assert events[0].probability == 80

    def test_extract_weather_events_snow(self, processor):
        """Test weather event extraction for snow."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            detailed_forecast="Snow likely with a high near 30. Heavy snow possible.",
        )

        events = processor.extract_weather_events(period)
        assert len(events) == 1
        assert events[0].event_type == "snow"
        assert events[0].probability == 70  # "likely" should give 70%

    def test_extract_weather_events_wind_significant(self, processor):
        """Test weather event extraction for significant wind."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            wind_speed="20 mph",
            detailed_forecast="Windy with a high near 60. Northwest wind 20 mph.",
        )

        events = processor.extract_weather_events(period)
        assert len(events) == 1
        assert events[0].event_type == "wind"

    def test_extract_weather_events_wind_insignificant(self, processor):
        """Test weather event extraction for insignificant wind."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            wind_speed="5 mph",
            detailed_forecast="Sunny with a high near 75. Light wind 5 mph.",
        )

        events = processor.extract_weather_events(period)
        # Should not detect wind event for speeds < 15 mph
        wind_events = [e for e in events if e.event_type == "wind"]
        assert len(wind_events) == 0

    def test_extract_temperature_data_daytime(self, processor):
        """Test temperature data extraction for daytime period."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            temperature=75,
        )

        temp_info = processor.extract_temperature_data(period)
        assert "high" in temp_info
        assert temp_info["high"] == "H:75°"
        assert "low" not in temp_info

    def test_extract_temperature_data_nighttime(self, processor):
        """Test temperature data extraction for nighttime period."""
        period = ForecastPeriod(
            name="Tonight",
            start_time="2024-01-01T18:00:00-05:00",
            end_time="2024-01-02T06:00:00-05:00",
            is_daytime=False,
            temperature=55,
        )

        temp_info = processor.extract_temperature_data(period)
        assert "low" in temp_info
        assert temp_info["low"] == "L:55°"
        assert "high" not in temp_info

    def test_extract_temperature_data_no_temp(self, processor):
        """Test temperature data extraction with no temperature."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            temperature=None,
        )

        temp_info = processor.extract_temperature_data(period)
        assert len(temp_info) == 0

    def test_extract_wind_data_success(self, processor):
        """Test wind data extraction."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            wind_speed="10 to 15 mph",
            wind_direction="NW",
        )

        wind_info = processor.extract_wind_data(period)
        assert wind_info == "NW10-15mph"

    def test_extract_wind_data_with_gusts(self, processor):
        """Test wind data extraction with gusts."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            wind_speed="15 mph",
            wind_direction="NW",
            wind_gust="25 mph",
        )

        wind_info = processor.extract_wind_data(period)
        assert wind_info == "NW15mph (G:25mph)"

    def test_extract_wind_data_missing(self, processor):
        """Test wind data extraction with missing data."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            wind_speed=None,
            wind_direction=None,
        )

        wind_info = processor.extract_wind_data(period)
        assert wind_info is None

    def test_extract_precipitation_data(self, processor):
        """Test precipitation data extraction."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            probability_of_precipitation=80,
            weather=[{"precipitation": "rain"}],
        )

        precip_info = processor.extract_precipitation_data(period)
        assert precip_info["probability"] == 80
        assert "rain" in precip_info["types"]

    def test_process_forecast_data(self, processor, sample_api_response):
        """Test complete forecast data processing."""
        forecast_data = processor.process_forecast_data(sample_api_response)

        assert len(forecast_data.periods) == 2
        assert forecast_data.periods[0].name == "Today"
        assert forecast_data.periods[1].name == "Tonight"

    def test_check_significant_wind_true(self, processor):
        """Test significant wind check with significant wind."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            wind_speed="20 mph",
        )

        assert weather_utils.check_significant_wind(period) is True

    def test_check_significant_wind_false(self, processor):
        """Test significant wind check with insignificant wind."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            wind_speed="10 mph",
        )

        assert weather_utils.check_significant_wind(period) is False

    def test_check_significant_wind_no_speed(self, processor):
        """Test significant wind check with no wind speed."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            wind_speed=None,
        )

        assert weather_utils.check_significant_wind(period) is False

    def test_infer_chance_explicit_percentage(self, processor):
        """Test chance inference with explicit percentage."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            probability_of_precipitation=75,
        )

        chance = weather_utils.infer_chance("rain", "rain likely", period)
        assert chance == 75  # Should use explicit percentage

    def test_infer_chance_keyword_based(self, processor):
        """Test chance inference based on keywords."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            probability_of_precipitation=None,
        )

        # Test "likely" keyword
        chance = weather_utils.infer_chance("rain", "rain likely", period)
        assert chance == 70

        # Test "scattered" keyword
        chance = weather_utils.infer_chance("rain", "scattered showers", period)
        assert chance == 40

        # Test "isolated" keyword
        chance = weather_utils.infer_chance("rain", "isolated showers", period)
        assert chance == 20

    def test_infer_chance_snow_blizzard(self, processor):
        """Test chance inference for snow blizzard."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            probability_of_precipitation=None,
        )

        chance = weather_utils.infer_chance("snow", "blizzard conditions", period)
        assert chance == 90

    def test_infer_chance_wind_high(self, processor):
        """Test chance inference for high wind."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            probability_of_precipitation=None,
        )

        chance = weather_utils.infer_chance("wind", "high wind warning", period)
        assert chance == 80

    def test_infer_chance_fog_dense(self, processor):
        """Test chance inference for dense fog."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            probability_of_precipitation=None,
        )

        chance = weather_utils.infer_chance("fog", "dense fog expected", period)
        assert chance == 90

    def test_infer_chance_smoke_heavy(self, processor):
        """Test chance inference for heavy smoke."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            probability_of_precipitation=None,
        )

        chance = weather_utils.infer_chance(
            "smoke", "heavy smoke from wildfires", period
        )
        assert chance == 90

    def test_get_wind_direction_abbr(self, processor):
        """Test wind direction abbreviation conversion."""
        assert weather_utils.get_wind_direction_abbr("north") == "N"
        assert weather_utils.get_wind_direction_abbr("northeast") == "NE"
        assert weather_utils.get_wind_direction_abbr("southwest") == "SW"
        assert weather_utils.get_wind_direction_abbr("variable") == "VAR"
        assert weather_utils.get_wind_direction_abbr("unknown") == "UN"  # First 2 chars
