"""Tests for full forecast format functionality."""

import pytest
import sys
import os

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "custom_components"))

# Import the functions we need directly from the modules
try:
    from satcom_forecast.forecast_parser import format_full_forecast
    from satcom_forecast.split_util import split_message

    HAS_HA = True
except ImportError:
    # If Home Assistant is not available, skip these tests
    HAS_HA = False


class TestFullFormat:
    """Test full forecast format functionality."""

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_full_format_complete_forecast(self):
        """Test that full format preserves complete forecast information."""
        sample_forecast = """Tonight: Rain showers likely, mainly before 7am. Low around 52. Southeast wind 5 mph. Chance of precipitation is 80%.
Showers likely, mainly before 7am.
Tuesday: Rain showers likely, mainly before 7am. High near 64. Southeast wind 5 mph. Chance of precipitation is 60%.
Showers likely, mainly before 7am
Tuesday Night: Partly cloudy, with a low around 47. West wind 5 mph.
Wednesday: Partly sunny, with a high near 63. East wind 5 mph."""

        # Format the full forecast
        full_result = format_full_forecast(sample_forecast)

        # Should contain all the original information
        assert "Tonight:" in full_result, "Should contain Tonight period"
        assert "Tuesday:" in full_result, "Should contain Tuesday period"
        assert "Tuesday Night:" in full_result, "Should contain Tuesday Night period"
        assert "Wednesday:" in full_result, "Should contain Wednesday period"

        # Should contain detailed weather information
        assert (
            "Rain showers likely" in full_result
        ), "Should contain precipitation details"
        assert "Low around 52" in full_result, "Should contain temperature information"
        assert "Southeast wind 5 mph" in full_result, "Should contain wind information"
        assert (
            "Chance of precipitation is 80%" in full_result
        ), "Should contain precipitation chance"

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_full_format_preserves_structure(self):
        """Test that full format preserves the original forecast structure."""
        sample_forecast = """Tonight: Rain showers likely, mainly before 7am. Low around 52. Southeast wind 5 mph. Chance of precipitation is 80%.
Showers likely, mainly before 7am.
Tuesday: Rain showers likely, mainly before 7am. High near 64. Southeast wind 5 mph. Chance of precipitation is 60%."""

        # Format the full forecast
        full_result = format_full_forecast(sample_forecast)

        # Should preserve newlines between periods
        lines = full_result.split("\n")
        period_lines = [
            line
            for line in lines
            if ":" in line
            and any(
                period in line
                for period in [
                    "Tonight",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                ]
            )
        ]

        # Should have multiple period lines
        assert (
            len(period_lines) >= 2
        ), f"Expected at least 2 period lines, got {len(period_lines)}"

        # Each period should start with a period name followed by colon
        for line in period_lines:
            assert re.match(
                r"^[A-Za-z ]+:", line
            ), f"Period line should start with period name and colon: {line}"

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_full_format_no_abbreviations(self):
        """Test that full format doesn't use abbreviations like compact or summary formats."""
        sample_forecast = """Tonight: Rain showers likely, mainly before 7am. Low around 52. Southeast wind 5 mph. Chance of precipitation is 80%.
Tuesday: Rain showers likely, mainly before 7am. High near 64. Southeast wind 5 mph. Chance of precipitation is 60%."""

        # Format the full forecast
        full_result = format_full_forecast(sample_forecast)

        # Should not contain abbreviated terms
        assert (
            "Rn(" not in full_result
        ), "Full format should not use abbreviated precipitation terms"
        assert (
            "Tngt:" not in full_result
        ), "Full format should not use abbreviated period names"
        assert (
            "H:" not in full_result
        ), "Full format should not use abbreviated temperature indicators"
        assert (
            "L:" not in full_result
        ), "Full format should not use abbreviated temperature indicators"

        # Should contain full terms
        assert "Rain" in full_result, "Full format should use full precipitation terms"
        assert "Tonight:" in full_result, "Full format should use full period names"
        assert (
            "High near" in full_result or "Low around" in full_result
        ), "Full format should use full temperature descriptions"

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_full_format_splitting(self):
        """Test that full format is correctly detected and split by the split_message function."""
        sample_forecast = """Tonight: Rain showers likely, mainly before 7am. Low around 52. Southeast wind 5 mph. Chance of precipitation is 80%.
Tuesday: Rain showers likely, mainly before 7am. High near 64. Southeast wind 5 mph. Chance of precipitation is 60%.
Tuesday Night: Partly cloudy, with a low around 47. West wind 5 mph.
Wednesday: Partly sunny, with a high near 63. East wind 5 mph."""

        # Format the full forecast
        full_result = format_full_forecast(sample_forecast)

        # Split the message
        parts = split_message(full_result, device_type="zoleo")

        # Should be split into multiple parts (due to character limits)
        assert len(parts) >= 1, "Should have at least one part"

        # Each part should contain complete period entries (not split mid-period)
        for part in parts:
            # Count period lines in this part
            period_lines = [
                line
                for line in part.split("\n")
                if ":" in line
                and any(
                    period in line
                    for period in [
                        "Tonight",
                        "Tuesday",
                        "Wednesday",
                        "Thursday",
                        "Friday",
                        "Saturday",
                    ]
                )
            ]

            # Each period line should be complete (start with period name and colon)
            for line in period_lines:
                assert re.match(
                    r"^[A-Za-z ]+:", line
                ), f"Period line should be complete: {line}"

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_full_format_weather_events(self):
        """Test that full format properly includes detailed weather event information."""
        sample_forecast = """Tonight: Rain showers likely, mainly before 7am. Low around 52. Southeast wind 5 mph. Chance of precipitation is 80%.
Showers likely, mainly before 7am.
Tuesday: Rain showers likely, mainly before 7am. High near 64. Southeast wind 5 mph. Chance of precipitation is 60%."""

        # Format the full forecast
        full_result = format_full_forecast(sample_forecast)

        # Should contain detailed weather information
        assert (
            "Rain showers likely" in full_result
        ), "Should contain detailed precipitation information"
        assert (
            "Showers likely, mainly before 7am" in full_result
        ), "Should contain detailed timing information"
        assert (
            "Chance of precipitation is 80%" in full_result
        ), "Should contain detailed probability information"
        assert (
            "Southeast wind 5 mph" in full_result
        ), "Should contain detailed wind information"

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_full_format_period_separation(self):
        """Test that periods are properly separated and don't run together."""
        sample_forecast = """Tonight: Rain showers likely, mainly before 7am. Low around 52. Southeast wind 5 mph. Chance of precipitation is 80%.
Tuesday: Rain showers likely, mainly before 7am. High near 64. Southeast wind 5 mph. Chance of precipitation is 60%.
Tuesday Night: Partly cloudy, with a low around 47. West wind 5 mph."""

        # Format the full forecast
        full_result = format_full_forecast(sample_forecast)

        # Split into lines
        lines = full_result.split("\n")

        # Find period lines
        period_lines = [
            line
            for line in lines
            if ":" in line
            and any(
                period in line
                for period in [
                    "Tonight",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                ]
            )
        ]

        # Should have 3 period lines (Tonight, Tuesday, Tuesday Night)
        assert (
            len(period_lines) == 3
        ), f"Expected 3 period lines, got {len(period_lines)}"

        # Check that each period is properly formatted
        assert "Tonight:" in period_lines[0], "First line should be Tonight"
        assert "Tuesday:" in period_lines[1], "Second line should be Tuesday"
        assert "Tuesday Night:" in period_lines[2], "Third line should be Tuesday Night"

        # Check that periods don't run together (no period names in the middle of lines)
        for line in period_lines:
            # Should not have multiple period names in one line
            period_count = sum(
                1
                for period in [
                    "Tonight",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                ]
                if period in line
            )
            assert (
                period_count == 1
            ), f"Line should contain exactly one period name: {line}"

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_full_format_vs_compact_format(self):
        """Test that full format provides more detail than compact format."""
        sample_forecast = """Tonight: Rain showers likely, mainly before 7am. Low around 52. Southeast wind 5 mph. Chance of precipitation is 80%.
Showers likely, mainly before 7am.
Tuesday: Rain showers likely, mainly before 7am. High near 64. Southeast wind 5 mph. Chance of precipitation is 60%."""

        # Format both formats
        from satcom_forecast.forecast_parser import format_compact_forecast

        full_result = format_full_forecast(sample_forecast)
        compact_result = format_compact_forecast(sample_forecast)

        # Full format should be longer (more detailed)
        assert len(full_result) > len(
            compact_result
        ), "Full format should be more detailed than compact format"

        # Full format should contain more detailed information
        assert (
            "Chance of precipitation is 80%" in full_result
        ), "Full format should contain detailed probability"
        assert (
            "Showers likely, mainly before 7am" in full_result
        ), "Full format should contain detailed timing"

        # Compact format should be more concise
        assert (
            "Rain(80%)" in compact_result
        ), "Compact format should use abbreviated precipitation"
        assert len(compact_result) < len(
            full_result
        ), "Compact format should be shorter than full format"


# Import re for regex matching
import re
