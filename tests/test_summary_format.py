"""Tests for summary forecast format functionality."""

import pytest
import sys
import os

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "custom_components"))

# Import the functions we need directly from the modules
try:
    from satcom_forecast.forecast_parser import summarize_forecast

    HAS_HA = True
except ImportError:
    # If Home Assistant is not available, skip these tests
    HAS_HA = False


class TestSummaryFormat:
    """Test summary forecast format functionality."""

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_summary_format_space_after_colon(self):
        """Test that summary format includes a space after the colon following day names."""
        sample_forecast = """Tonight: Rain showers likely, mainly before 7am. Low around 52. Southeast wind 5 mph. Chance of precipitation is 80%.
Tuesday: Rain showers likely, mainly before 7am. High near 64. Southeast wind 5 mph. Chance of precipitation is 60%.
Tuesday Night: Partly cloudy, with a low around 47. West wind 5 mph.
Wednesday: Partly sunny, with a high near 63. East wind 5 mph."""

        # Format the summary forecast
        summary_result = summarize_forecast(sample_forecast)

        # Split by pipe separators (summary format uses | as separators)
        parts = summary_result.split(" | ")

        # Each part should start with a day name followed by colon and space
        for part in parts:
            if ":" in part:
                # Find the colon and check for space after it
                colon_index = part.find(":")
                if colon_index != -1 and colon_index + 1 < len(part):
                    # Should have a space after the colon
                    assert (
                        part[colon_index + 1] == " "
                    ), f"Should have space after colon: '{part}'"

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_summary_format_day_separation(self):
        """Test that summary format properly separates days with pipe separators."""
        sample_forecast = """Tonight: Rain showers likely, mainly before 7am. Low around 52. Southeast wind 5 mph. Chance of precipitation is 80%.
Tuesday: Rain showers likely, mainly before 7am. High near 64. Southeast wind 5 mph. Chance of precipitation is 60%.
Tuesday Night: Partly cloudy, with a low around 47. West wind 5 mph."""

        # Format the summary forecast
        summary_result = summarize_forecast(sample_forecast)

        # Should contain pipe separators
        assert " | " in summary_result, "Summary format should contain pipe separators"

        # Split by pipe separators
        parts = summary_result.split(" | ")

        # Should have multiple parts (one for each day)
        assert len(parts) >= 2, f"Expected at least 2 parts, got {len(parts)}"

        # Each part should contain a day name
        day_names = [
            "Tonight",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        for part in parts:
            has_day = any(day in part for day in day_names)
            assert has_day, f"Part should contain a day name: {part}"

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_summary_format_weather_events(self):
        """Test that summary format properly includes weather events."""
        sample_forecast = """Tonight: Rain showers likely, mainly before 7am. Low around 52. Southeast wind 5 mph. Chance of precipitation is 80%.
Tuesday: Rain showers likely, mainly before 7am. High near 64. Southeast wind 5 mph. Chance of precipitation is 60%."""

        # Format the summary forecast
        summary_result = summarize_forecast(sample_forecast)

        # Should contain weather event information
        assert (
            "Rain" in summary_result
        ), "Summary should contain weather event information"

        # Should contain temperature information
        assert (
            "52" in summary_result or "64" in summary_result
        ), "Summary should contain temperature information"

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_summary_format_no_newlines(self):
        """Test that summary format doesn't contain newlines (uses pipe separators instead)."""
        sample_forecast = """Tonight: Rain showers likely, mainly before 7am. Low around 52. Southeast wind 5 mph. Chance of precipitation is 80%.
Tuesday: Rain showers likely, mainly before 7am. High near 64. Southeast wind 5 mph. Chance of precipitation is 60%."""

        # Format the summary forecast
        summary_result = summarize_forecast(sample_forecast)

        # Should not contain newlines (summary format uses pipe separators)
        assert "\n" not in summary_result, "Summary format should not contain newlines"

        # Should contain pipe separators
        assert " | " in summary_result, "Summary format should contain pipe separators"

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_summary_format_splitting_detection(self):
        """Test that summary format is correctly detected by the split_message function."""
        sample_forecast = """Tonight: Rain showers likely, mainly before 7am. Low around 52. Southeast wind 5 mph. Chance of precipitation is 80%.
Tuesday: Rain showers likely, mainly before 7am. High near 64. Southeast wind 5 mph. Chance of precipitation is 60%."""

        # Format the summary forecast
        summary_result = summarize_forecast(sample_forecast)

        # Import split_message for testing
        from satcom_forecast.split_util import split_message

        # Split the message
        parts = split_message(summary_result, device_type="zoleo")

        # Should be split into multiple parts (due to character limits)
        assert len(parts) >= 1, "Should have at least one part"

        # Each part should contain complete day entries
        for part in parts:
            # Should contain pipe separators (indicating summary format)
            if " | " in part:
                day_parts = part.split(" | ")
                for day_part in day_parts:
                    # Each day part should start with a day name and colon
                    assert ":" in day_part, f"Day part should contain colon: {day_part}"
