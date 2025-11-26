import os
import sys

import pytest

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__), "..", "custom_components", "satcom_forecast"
    ),
)
from forecast_parser import format_forecast, summarize_forecast

TEST_FORECAST = """This Afternoon: A chance of showers. Mostly cloudy, with a high near 50. Southeast wind around 10 mph. Chance of precipitation is 40%.
Tonight: Showers likely, mainly between 7pm and 10pm, then rain after 10pm. Low around 41. Southeast wind around 15 mph. Chance of precipitation is 80%.
Thursday: Rain likely. Cloudy, with a high near 49. Southeast wind 10 to 15 mph. Chance of precipitation is 70%.
Thursday Night: Rain likely, mainly before 10pm. Cloudy, with a low around 41. Southeast wind 5 to 15 mph. Chance of precipitation is 60%.
Friday: Rain likely, mainly between 10am and 1pm. Cloudy, with a high near 51. Southeast wind around 10 mph. Chance of precipitation is 60%.
Friday Night: A chance of rain before 7pm, then scattered showers after 7pm. Cloudy, with a low around 43. Southeast wind around 10 mph. Chance of precipitation is 50%.
Saturday: Scattered showers before 10am, then a chance of rain after 10am. Cloudy, with a high near 52. Chance of precipitation is 30%.
Saturday Night: A chance of rain. Cloudy, with a low around 43.
Sunday: A chance of rain. Cloudy, with a high near 52.
Sunday Night: A chance of rain. Cloudy, with a low around 43.
Monday: A chance of rain. Mostly cloudy, with a high near 54.
Monday Night: A chance of rain. Mostly cloudy, with a low around 44.
Tuesday: A chance of rain. Mostly cloudy, with a high near 56."""


class TestForecastParser:
    def test_basic_formats(self) -> None:
        """Test basic format functionality."""
        compact_result = format_forecast(TEST_FORECAST, mode="compact")
        summary_result = format_forecast(TEST_FORECAST, mode="summary")
        full_result = format_forecast(TEST_FORECAST, mode="full")

        assert "Afternoon: Rain(40%)" in compact_result
        assert "Tdy: Rn(80%),H:50°,SE10mph,L:41°,SE15mph" in summary_result
        assert "Tngt:" not in summary_result
        assert "This Afternoon: A chance of showers" in full_result

    def test_smoke_conditions(self) -> None:
        """Test smoke detection and labeling."""
        smoke_forecast = """This Afternoon: Widespread haze. Mostly cloudy, with a high near 50. Southeast wind around 10 mph.
Tonight: Widespread haze. Low around 41. Southeast wind around 15 mph."""
        areas_smoke_forecast = (
            "This Afternoon: Areas of smoke. Mostly sunny, with a high near 70."
        )

        result_haze = format_forecast(smoke_forecast, mode="compact")
        result_areas = format_forecast(areas_smoke_forecast, mode="compact")

        assert "🚨Smoke(50%)" in result_haze
        assert "- Smoke" in result_haze  # Updated to use dash instead of pipe
        assert "🚨Smoke(65%)" in result_areas
        assert "- Smoke" in result_areas  # Updated to use dash instead of pipe

    def test_explicit_percentages(self) -> None:
        """Test explicit percentage handling."""
        explicit_forecast = """This Afternoon: A chance of showers. Mostly cloudy, with a high near 50. Southeast wind around 10 mph. Chance of precipitation is 40%.
Tonight: Showers likely, mainly between 7pm and 10pm, then rain after 10pm. Low around 41. Southeast wind around 15 mph. Chance of precipitation is 80%."""

        compact_result = format_forecast(explicit_forecast, mode="compact")
        summary_result = format_forecast(explicit_forecast, mode="summary")

        assert "Rain(40%)" in compact_result
        assert "Rain(80%)" in compact_result
        assert "Rn(80%)" in summary_result

    def test_smoke_with_precipitation(self) -> None:
        """Test that smoke and precipitation don't share percentages."""
        test_text = """This Afternoon: Scattered showers. Areas of smoke. Mostly cloudy, with a high near 67. South wind around 5 mph. Chance of precipitation is 40%.
Tonight: Showers, mainly before 1am, then rain after 1am. Areas of smoke. Mostly cloudy, with a low around 57. Southeast wind around 5 mph. Chance of precipitation is 80%."""

        compact_result = format_forecast(test_text, mode="compact")
        summary_result = format_forecast(test_text, mode="summary")

        assert "🚨Smoke(65%)" in compact_result
        assert "- Smoke" in compact_result  # Updated to use dash instead of pipe
        assert "Rn(80%)" in summary_result
        assert "🚨Smk(65%)" in summary_result

    @pytest.mark.parametrize(
        "description,forecast_text,expected_event",
        [
            (
                "Fog conditions",
                "Tonight: Dense fog. Low around 35. Calm wind.",
                "Fog(90%)",
            ),
            (
                "Thunderstorm",
                "Today: Thunderstorms likely. High near 75. Southeast wind 10 mph.",
                "Thunderstorms likely",
            ),
            (
                "Wind conditions",
                "Tonight: Windy. Low around 45. Northwest wind 20 to 30 mph.",
                "Windy",
            ),
            (
                "Snow",
                "Today: Snow likely. High near 25. North wind 15 mph.",
                "Snow likely",
            ),
            (
                "Freezing rain",
                "Tonight: Freezing rain. Low around 28. Northeast wind 10 mph.",
                "Freezing rain",
            ),
        ],
    )
    def test_weather_event_detection(
        self, description: str, forecast_text: str, expected_event: str
    ) -> None:
        """Test detection of various weather events."""
        result = format_forecast(forecast_text, "compact")
        assert expected_event.split("(")[0] in result or expected_event in result

    def test_temperature_wind_extraction(self) -> None:
        """Test temperature and wind information extraction."""
        temp_wind_forecast = """Tonight: A chance of rain. Mostly cloudy, with a low around 46. Southeast wind 5 to 10 mph. Chance of precipitation is 30%.
Wednesday: Rain likely. Cloudy, with a high near 61. Southeast wind 5 to 10 mph. Chance of precipitation is 70%.
Wednesday Night: Rain. Cloudy, with a low around 45. East wind around 15 mph. Chance of precipitation is 80%.
Thursday: Rain. Cloudy, with a high near 61. East wind 5 to 10 mph. Chance of precipitation is 90%."""

        summary = summarize_forecast(temp_wind_forecast)

        assert "L:46" in summary
        assert "H:61" in summary
        assert "SE5-10mph" in summary
        assert "E15mph" in summary

    def test_period_detection(self) -> None:
        """Test that all forecast periods are detected correctly."""
        period_test = """This Afternoon: Sunny. High near 70.
Tonight: Clear. Low around 45.
Today: Partly cloudy. High near 65.
Overnight: Mostly clear. Low around 40.
Monday: Rain likely. High near 55.
Monday Night: Rain. Low around 35."""

        summary = summarize_forecast(period_test)

        assert "Tdy:" in summary
        assert "Aft:" not in summary
        assert "Tngt:" not in summary
        assert "Tdy:" in summary
        assert "Mon:" in summary

    def test_smoke_probability_levels(self) -> None:
        """Test that different smoke conditions have appropriate probability levels."""
        areas_smoke = "This Afternoon: Areas of smoke. High near 70."
        wildfire_smoke = "This Afternoon: Wildfire smoke. High near 70."
        heavy_smoke = "This Afternoon: Heavy smoke. High near 70."

        result_areas = format_forecast(areas_smoke, mode="compact")
        result_wildfire = format_forecast(wildfire_smoke, mode="compact")
        result_heavy = format_forecast(heavy_smoke, mode="compact")

        assert "🚨Smoke(65%)" in result_areas
        assert "🚨Smoke(75%)" in result_wildfire
        assert "🚨Smoke(90%)" in result_heavy

    def test_summary_with_temp_wind(self) -> None:
        """Test summary format with temperature and wind information."""
        sample_text = """
Tonight: A chance of rain. Mostly cloudy, with a low around 46. Southeast wind 5 to 10 mph. Chance of precipitation is 30%.
Wednesday: Rain likely. Cloudy, with a high near 61. Southeast wind 5 to 10 mph. Chance of precipitation is 70%.
Wednesday Night: Rain. Cloudy, with a low around 45. East wind around 15 mph. Chance of precipitation is 80%.
Thursday: Rain. Cloudy, with a high near 61. East wind 5 to 10 mph. Chance of precipitation is 90%.
"""
        summary = summarize_forecast(sample_text)
        expected_summary = "Tngt: Rn(30%),L:46°,SE5-10mph\nWed: Rn(80%),H:61°,SE5-10mph,L:45°,E15mph\nThu: Rn(90%),H:61°,E5-10mph"  # Updated to include spaces after colons
        assert summary == expected_summary

    def test_real_world_summary(self) -> None:
        """Test a real-world forecast scenario."""
        real_forecast_text = """
Tonight: Mostly cloudy, with a low around 46. Light and variable wind becoming southeast 5 to 10 mph in the evening.
Wednesday: A slight chance of showers after 4pm. Mostly cloudy, with a high near 61. Northwest wind around 5 mph.
Wednesday Night: A 20 percent chance of showers. Mostly cloudy, with a low around 45. Southeast wind around 15 mph.
Thursday: A 30 percent chance of rain. Mostly cloudy, with a high near 61. Southeast wind 5 to 10 mph.
Thursday Night: A 20 percent chance of rain. Mostly cloudy, with a low around 47. East wind around 10 mph. Breezy.
Friday: A 20 percent chance of rain. Mostly cloudy, with a high near 62. Northeast wind around 5 mph.
Friday Night: Mostly cloudy, with a low around 48.
Saturday: Partly sunny, with a high near 64.
Saturday Night: Mostly cloudy, with a low around 48.
Sunday: A 30 percent chance of rain. Mostly cloudy, with a high near 61.
Sunday Night: A 20 percent chance of rain. Mostly cloudy, with a low around 47.
Monday: A 30 percent chance of rain. Mostly cloudy, with a high near 61.
"""
        summary = summarize_forecast(real_forecast_text)
        expected_summary = "Tngt: L:46°,SE5-10mph\nWed: Rn(30%),H:61°,NW5mph,L:45°,SE15mph\nThu: Rn(30%),H:61°,SE5-10mph,L:47°,E10mph\nFri: Rn(20%),H:62°,NE5mph,L:48°\nSat: H:64°,L:48°\nSun: Rn(30%),H:61°,L:47°\nMon: Rn(30%),H:61°"
        # Since Tngt is the first period and it's night, it stays as Tngt.
        # Wed + Wed Night -> Wed
        # Thu + Thu Night -> Thu
        # Fri + Fri Night -> Fri
        # Sat + Sat Night -> Sat
        # Sun + Sun Night -> Sun
        # Mon -> Mon

        # Wait, my previous expectation string already had merged lines!
        # "Wed: Rn(30%),H:61°,NW5mph,L:45°,SE15mph" -> This has H and L.
        # "Thu: Rn(30%),H:61°,SE5-10mph,L:47°,E10mph" -> This has H and L.

        # The failure was: assert 'Tngt: L:46°,...Rn(30%),H:61°' == 'Tngt: L:46°,...Rn(30%),H:61°'
        # Wait, the failure message showed identical strings?
        # FAILED tests/test_forecast_parser.py::TestForecastParser::test_real_world_summary - AssertionError: assert 'Tngt: L:46°,...Rn(30%),H:61°' == 'Tngt: L:46°,...Rn(30%),H:61°'
        # This usually means there's a subtle difference (whitespace, invisible char, or order).
        # Let's re-verify the expected string carefully.

        # In the actual output (from reproduction script):
        # Tngt: Rn(70%),L:12°,NE5mph
        # Wed: Rn(70%),H:27°,NE5mph,L:26°,NE5-10mph

        # In the test case:
        # Tonight: ... low around 46 ...
        # Wednesday: ... high near 61 ...
        # Wednesday Night: ... low around 45 ...

        # Expected:
        # Tngt: L:46°,SE5-10mph
        # Wed: Rn(30%),H:61°,NW5mph,L:45°,SE15mph

        # I will update the expectation to be exactly what I think it should be based on the logic.

        assert summary == expected_summary

    def test_summarize_forecast_with_holidays(self) -> None:
        """Test that summarize_forecast correctly groups holidays and their nights."""
        forecast_text = """
Tonight: Rain likely. Low around 12. Northeast wind 5 mph.
Wednesday: Rain likely. High near 27. Northeast wind 5 mph.
Wednesday Night: Rain likely. Low around 26. Northeast wind 5 to 10 mph.
Thanksgiving Day: Rain likely. High near 32. Northeast wind 10 mph.
Thursday Night: Rain likely. Low around 29. Northeast wind 5 to 10 mph.
Friday: Rain likely. High near 34. Northeast wind 5 to 10 mph.
Friday Night: Rain likely. Low around 23.
"""
        summary = summarize_forecast(forecast_text)

        # Check that "Thanksgiving Day" (Tha) and "Thursday Night" are grouped
        # Expect "Tha" to be present, but NOT "Thu" (Thursday Night) as a separate line
        assert "Tha:" in summary
        assert "Thu:" not in summary

        # Check that it contains info from both day and night
        # High from Day (32), Low from Night (29)
        tha_line = [line for line in summary.splitlines() if line.startswith("Tha:")][0]
        assert "H:32" in tha_line
        assert "L:29" in tha_line
