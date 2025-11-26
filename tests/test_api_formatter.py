"""
Unit tests for API formatter module.
"""

import pytest
from unittest.mock import Mock

from custom_components.satcom_forecast.api_formatter import APIFormatter
from custom_components.satcom_forecast.api_models import ForecastPeriod, WeatherEvent
from custom_components.satcom_forecast import weather_utils


class TestAPIFormatter:
    """Test cases for APIFormatter."""
    
    @pytest.fixture
    def formatter(self):
        """Create a test formatter instance."""
        return APIFormatter()
    
    @pytest.fixture
    def sample_periods(self):
        """Sample forecast periods for testing."""
        return [
            ForecastPeriod(
                name="Today",
                start_time="2024-01-01T06:00:00-05:00",
                end_time="2024-01-01T18:00:00-05:00",
                is_daytime=True,
                temperature=75,
                temperature_unit="F",
                wind_speed="10 to 15 mph",
                wind_direction="NW",
                short_forecast="Sunny",
                detailed_forecast="Sunny with a high near 75. Northwest wind 10 to 15 mph.",
                probability_of_precipitation=0
            ),
            ForecastPeriod(
                name="Tonight",
                start_time="2024-01-01T18:00:00-05:00",
                end_time="2024-01-02T06:00:00-05:00",
                is_daytime=False,
                temperature=55,
                temperature_unit="F",
                wind_speed="5 to 10 mph",
                wind_direction="NW",
                short_forecast="Clear",
                detailed_forecast="Clear with a low around 55. Northwest wind 5 to 10 mph.",
                probability_of_precipitation=0
            )
        ]
    
    @pytest.fixture
    def sample_events(self):
        """Sample weather events for testing."""
        return [
            WeatherEvent(
                event_type="rain",
                probability=70,
                severity="high",
                description="Rain likely",
                keywords=["rain", "likely"]
            )
        ]
    
    def test_format_forecast_summary(self, formatter, sample_periods, sample_events):
        """Test summary format formatting."""
        result = formatter.format_forecast(sample_periods, sample_events, "summary")
        
        assert isinstance(result, str)
        assert len(result) > 0
        # Summary should be relatively short
        assert len(result) < 500
    
    def test_format_forecast_compact(self, formatter, sample_periods, sample_events):
        """Test compact format formatting."""
        result = formatter.format_forecast(sample_periods, sample_events, "compact")
        
        assert isinstance(result, str)
        assert len(result) > 0
        # Compact should be medium length
        assert 50 <= len(result) <= 1500
    
    def test_format_forecast_full(self, formatter, sample_periods, sample_events):
        """Test full format formatting."""
        # Multiply periods to ensure enough length
        long_periods = sample_periods * 5
        result = formatter.format_forecast(long_periods, sample_events, "full")
        
        assert isinstance(result, str)
        assert len(result) > 0
        # Full should be longer
        assert len(result) >= 500
    
    def test_format_forecast_unknown_mode(self, formatter, sample_periods, sample_events):
        """Test formatting with unknown mode (should default to summary)."""
        result = formatter.format_forecast(sample_periods, sample_events, "unknown")
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_filter_periods_by_days(self, formatter, sample_periods):
        """Test filtering periods by days parameter."""
        # Test with days=1 (should include only first day)
        filtered = formatter._filter_periods_by_days(sample_periods, 1)
        assert len(filtered) == 2  # Today and Tonight are same day
        
        # Test with days=None (should include all)
        filtered = formatter._filter_periods_by_days(sample_periods, None)
        assert len(filtered) == 2
        
        # Test with days=0 (should include all)
        filtered = formatter._filter_periods_by_days(sample_periods, 0)
        assert len(filtered) == 2
    
    def test_get_day_name(self, formatter):
        """Test day name extraction."""
        assert formatter._get_day_name("Today") == "Today"
        assert formatter._get_day_name("Tonight") == "Today"
        assert formatter._get_day_name("Monday") == "Monday"
        assert formatter._get_day_name("Monday Night") == "Monday"
        assert formatter._get_day_name("This Afternoon") == "Today"
        assert formatter._get_day_name("Overnight") == "Today"
    
    def test_get_base_period_name(self, formatter):
        """Test base period name extraction."""
        assert formatter._get_base_period_name("Today") == "Today"
        assert formatter._get_base_period_name("Monday Night") == "Monday"
        assert formatter._get_base_period_name("Tuesday") == "Tuesday"
    
    def test_shorten_period_name(self, formatter):
        """Test period name shortening."""
        assert formatter._shorten_period_name("This Afternoon") == "Aft"
        assert formatter._shorten_period_name("Today") == "Tdy"
        assert formatter._shorten_period_name("Tonight") == "Tngt"
        assert formatter._shorten_period_name("Overnight") == "ON"
        assert formatter._shorten_period_name("Monday") == "Mon"
        assert formatter._shorten_period_name("Tuesday") == "Tue"
        assert formatter._shorten_period_name("Wednesday") == "Wed"
        assert formatter._shorten_period_name("Thursday") == "Thu"
        assert formatter._shorten_period_name("Friday") == "Fri"
        assert formatter._shorten_period_name("Saturday") == "Sat"
        assert formatter._shorten_period_name("Sunday") == "Sun"
        assert formatter._shorten_period_name("Unknown") == "Unk"  # First 3 chars
    
    def test_detect_period_events_rain(self, formatter, sample_events):
        """Test weather event detection for rain."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            detailed_forecast="Rain likely with a high near 70. Chance of precipitation is 80%."
        )
        
        events = formatter._detect_period_events(period, sample_events)
        assert len(events) == 1
        assert "Rn(80%)" in events[0]  # Should use explicit percentage
    
    def test_detect_period_events_snow(self, formatter, sample_events):
        """Test weather event detection for snow."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            detailed_forecast="Snow likely with a high near 30."
        )
        
        events = formatter._detect_period_events(period, sample_events)
        assert len(events) == 1
        assert "Snw(70%)" in events[0]  # "likely" should give 70%
    
    def test_detect_period_events_wind_significant(self, formatter, sample_events):
        """Test weather event detection for significant wind."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            wind_speed="20 mph",
            detailed_forecast="Windy with a high near 60. Northwest wind 20 mph."
        )
        
        events = formatter._detect_period_events(period, sample_events)
        wind_events = [e for e in events if "Wnd" in e]
        assert len(wind_events) == 1
    
    def test_detect_period_events_wind_insignificant(self, formatter, sample_events):
        """Test weather event detection for insignificant wind."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            wind_speed="5 mph",
            detailed_forecast="Sunny with a high near 75. Light wind 5 mph."
        )
        
        events = formatter._detect_period_events(period, sample_events)
        wind_events = [e for e in events if "Wnd" in e]
        assert len(wind_events) == 0  # Should not detect wind for < 15 mph
    
    def test_extract_temperature_info_daytime(self, formatter):
        """Test temperature info extraction for daytime."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            temperature=75
        )
        
        temp_info = weather_utils.extract_temperature_info(period)
        assert "H:75°" in temp_info
    
    def test_extract_temperature_info_nighttime(self, formatter):
        """Test temperature info extraction for nighttime."""
        period = ForecastPeriod(
            name="Tonight",
            start_time="2024-01-01T18:00:00-05:00",
            end_time="2024-01-02T06:00:00-05:00",
            is_daytime=False,
            temperature=55
        )
        
        temp_info = weather_utils.extract_temperature_info(period)
        assert "L:55°" in temp_info
    
    def test_extract_wind_info_success(self, formatter):
        """Test wind info extraction."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            wind_speed="10 to 15 mph",
            wind_direction="NW"
        )
        
        wind_info = weather_utils.extract_wind_info(period)
        assert wind_info == ["NW10-15mph"]
    
    def test_extract_wind_info_with_gusts(self, formatter):
        """Test wind info extraction with gusts."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            wind_speed="15 mph",
            wind_direction="NW",
            wind_gust="25 mph"
        )
        
        wind_info = weather_utils.extract_wind_info(period)
        assert wind_info == ["NW15mph (G:25mph)"]
    
    def test_extract_wind_info_missing(self, formatter):
        """Test wind info extraction with missing data."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            wind_speed=None,
            wind_direction=None
        )
        
        wind_info = weather_utils.extract_wind_info(period)
        assert wind_info == []
    
    def test_check_significant_wind_true(self, formatter):
        """Test significant wind check."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            wind_speed="20 mph"
        )
        
        assert weather_utils.check_significant_wind(period) is True
    
    def test_check_significant_wind_false(self, formatter):
        """Test insignificant wind check."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            wind_speed="10 mph"
        )
        
        assert weather_utils.check_significant_wind(period) is False
    
    def test_infer_chance_explicit_percentage(self, formatter):
        """Test chance inference with explicit percentage."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            probability_of_precipitation=75
        )
        
        chance = weather_utils.infer_chance("rain", "rain likely", period)
        assert chance == 75  # Should use explicit percentage
    
    def test_infer_chance_keyword_based(self, formatter):
        """Test chance inference based on keywords."""
        period = ForecastPeriod(
            name="Today",
            start_time="2024-01-01T06:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            probability_of_precipitation=None
        )
        
        # Test various keywords
        assert weather_utils.infer_chance("rain", "rain likely", period) == 70
        assert weather_utils.infer_chance("rain", "scattered showers", period) == 40
        assert weather_utils.infer_chance("rain", "isolated showers", period) == 20
        assert weather_utils.infer_chance("snow", "blizzard conditions", period) == 90
        assert weather_utils.infer_chance("wind", "high wind warning", period) == 80
        assert weather_utils.infer_chance("fog", "dense fog expected", period) == 90
        assert weather_utils.infer_chance("smoke", "heavy smoke from wildfires", period) == 90
    
    def test_get_wind_direction_abbr(self, formatter):
        """Test wind direction abbreviation conversion."""
        assert weather_utils.get_wind_direction_abbr("north") == "N"
        assert weather_utils.get_wind_direction_abbr("northeast") == "NE"
        assert weather_utils.get_wind_direction_abbr("southwest") == "SW"
        assert weather_utils.get_wind_direction_abbr("variable") == "VAR"
        assert weather_utils.get_wind_direction_abbr("unknown") == "UN"  # First 2 chars
    
    def test_clean_forecast_text(self, formatter):
        """Test forecast text cleaning."""
        text = "Sunny  with   a  high  near  75.  Northwest  wind  10  to  15  mph."
        cleaned = formatter._clean_forecast_text(text)
        assert "  " not in cleaned  # Should normalize spaces
        assert cleaned == "Sunny with a high near 75. Northwest wind 10 to 15 mph."
    
    def test_clean_forecast_for_display(self, formatter):
        """Test forecast text cleaning for display."""
        text = "Sunny with a high near 75. Northwest wind 10 to 15 mph. Chance of precipitation is 0%."
        cleaned = formatter._clean_forecast_for_display(text)
        
        # Should remove temperature and wind patterns
        assert "high near 75" not in cleaned
        assert "Northwest wind 10 to 15 mph" not in cleaned
        assert "Chance of precipitation is 0%" not in cleaned
        assert "Sunny" in cleaned  # Should keep the main description
    
    def test_merge_period_events(self, formatter):
        """Test merging period events."""
        existing = ["Rn(50%)", "Wnd(30%)"]
        new = ["Rn(70%)", "ThSt(40%)"]
        
        merged = formatter._merge_period_events(existing, new)
        
        # Should keep higher probability for rain
        assert "Rn(70%)" in merged
        # Should keep existing wind
        assert "Wnd(30%)" in merged
        # Should add new thunderstorm
        assert "ThSt(40%)" in merged
        # Should not have duplicate rain
        # Should not have duplicate rain
        rain_events = [e for e in merged if e.startswith("Rn")]
        assert len(rain_events) == 1
    
    def test_format_summary_forecast_no_events(self, formatter):
        """Test summary format with no weather events."""
        periods = [
            ForecastPeriod(
                name="Today",
                start_time="2024-01-01T06:00:00-05:00",
                end_time="2024-01-01T18:00:00-05:00",
                is_daytime=True,
                detailed_forecast="Sunny with a high near 75."
            )
        ]
        events = []
        
        result = formatter.format_summary_forecast(periods, events)
        assert result == "No significant weather expected."
    
    def test_format_compact_forecast_with_events(self, formatter):
        """Test compact format with weather events."""
        periods = [
            ForecastPeriod(
                name="Today",
                start_time="2024-01-01T06:00:00-05:00",
                end_time="2024-01-01T18:00:00-05:00",
                is_daytime=True,
                temperature=75,
                wind_speed="15 mph",
                wind_direction="NW",
                detailed_forecast="Rain likely with a high near 75. Northwest wind 15 mph."
            )
        ]
        events = [
            WeatherEvent(
                event_type="rain",
                probability=70,
                severity="high",
                description="Rain likely",
                keywords=["rain", "likely"]
            )
        ]
        
        result = formatter.format_compact_forecast(periods, events)
        
        assert "Today:" in result
        assert "Rn(70%)" in result
        assert "75" in result
        assert "NW15mph" in result
        assert "Rain likely" in result
    
    def test_format_full_forecast_truncation(self, formatter):
        """Test full format with truncation for long content."""
        # Create a very long forecast
        long_forecast = "This is a very long forecast. " * 100  # ~3000 chars
        periods = [
            ForecastPeriod(
                name="Today",
                start_time="2024-01-01T06:00:00-05:00",
                end_time="2024-01-01T18:00:00-05:00",
                is_daytime=True,
                detailed_forecast=long_forecast
            )
        ]
        events = []
        
        result = formatter.format_full_forecast(periods, events)
        
        # Should be truncated to around 2000 characters
        assert len(result) <= 2000
        assert result.endswith("...") or len(result) < 2000