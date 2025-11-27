"""Tests for compact forecast format functionality."""

import os
import re
import sys

import pytest

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "custom_components"))

# Import functions directly from module files to avoid Home Assistant dependencies
try:
    # Import directly from the module files
    sys.path.insert(
        0,
        os.path.join(
            os.path.dirname(__file__), "..", "custom_components", "satcom_forecast"
        ),
    )
    from forecast_parser import format_compact_forecast
    from split_util import split_message

    HAS_HA = True
except ImportError:
    # If modules are not available, skip these tests
    HAS_HA = False


class TestCompactFormat:
    """Test compact forecast format functionality."""

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_compact_format_newlines(self):
        """Test that compact format preserves newlines between days."""
        sample_forecast = """Tonight: Rain showers likely, mainly before 7am. Low around 52. Southeast wind 5 mph. Chance of precipitation is 80%.
Showers likely, mainly before 7am.
Tuesday: Rain showers likely, mainly before 7am. High near 64. Southeast wind 5 mph. Chance of precipitation is 60%.
Showers likely, mainly before 7am
Tuesday Night: Partly cloudy, with a low around 47. West wind 5 mph.
Wednesday: Partly sunny, with a high near 63. East wind 5 mph.
Wednesday Night: A chance of rain between 10pm and 1am. Low around 52. Southeast wind 5 to 10 mph. Chance of precipitation is 30%.
A chance of rain between 10pm and 1am
Thursday: A chance of rain between 7am and 1pm. High near 62. West wind 5 mph. Chance of precipitation is 30%.
A chance of rain between 7am and 1pm
Thursday Night: Mostly cloudy, with a low around 49.
Friday: A chance of rain after 10am. High near 65. Chance of precipitation is 30%.
A chance of rain after 10am
Friday Night: A chance of rain. Low around 50. Chance of precipitation is 30%.
A chance of rain
Saturday: A chance of rain. High near 63. Chance of precipitation is 30%.
A chance of rain
Saturday Night: A chance of rain. Low around 50. Chance of precipitation is 30%.
A chance of rain"""

        # Format the compact forecast
        compact_result = format_compact_forecast(sample_forecast)

        # Check that each day is on its own line
        lines = compact_result.split("\n")
        day_lines = [
            line
            for line in lines
            if ":" in line
            and any(
                day in line
                for day in [
                    "Tonight",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                ]
            )
        ]

        # Should have multiple day lines
        assert (
            len(day_lines) >= 6
        ), f"Expected at least 6 day lines, got {len(day_lines)}"

        # Each day should start with a day name followed by colon
        for line in day_lines:
            assert re.match(
                r"^[A-Za-z ]+:", line
            ), f"Day line should start with day name and colon: {line}"

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_compact_format_no_pipe_separators(self):
        """Test that compact format doesn't use pipe separators that would trigger summary format detection."""
        sample_forecast = """Tonight: Rain showers likely, mainly before 7am. Low around 52. Southeast wind 5 mph. Chance of precipitation is 80%.
Tuesday: Rain showers likely, mainly before 7am. High near 64. Southeast wind 5 mph. Chance of precipitation is 60%."""

        # Format the compact forecast
        compact_result = format_compact_forecast(sample_forecast)

        # Should not contain pipe separators (|)
        assert (
            " | " not in compact_result
        ), "Compact format should not contain pipe separators"

        # Should contain newlines between days
        assert (
            "\n" in compact_result
        ), "Compact format should contain newlines between days"

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_compact_format_splitting(self):
        """Test that compact format is correctly detected and split by the split_message function."""
        sample_forecast = """Tonight: Rain showers likely, mainly before 7am. Low around 52. Southeast wind 5 mph. Chance of precipitation is 80%.
Tuesday: Rain showers likely, mainly before 7am. High near 64. Southeast wind 5 mph. Chance of precipitation is 60%.
Tuesday Night: Partly cloudy, with a low around 47. West wind 5 mph.
Wednesday: Partly sunny, with a high near 63. East wind 5 mph."""

        # Format the compact forecast
        compact_result = format_compact_forecast(sample_forecast)

        # Split the message
        parts = split_message(compact_result, device_type="zoleo")

        # Should be split into multiple parts (due to character limits)
        assert len(parts) >= 1, "Should have at least one part"

        # Each part should contain complete day entries (not split mid-day)
        for part in parts:
            # Count day lines in this part
            day_lines = [
                line
                for line in part.split("\n")
                if ":" in line
                and any(
                    day in line
                    for day in [
                        "Tonight",
                        "Tuesday",
                        "Wednesday",
                        "Thursday",
                        "Friday",
                        "Saturday",
                    ]
                )
            ]

            # Each day line should be complete (start with day name and colon)
            for line in day_lines:
                # Account for part numbering like "(1/2) " at the start
                if line.startswith("(") and ")" in line:
                    # Remove part numbering for the regex check
                    line_without_numbering = (
                        line.split(") ", 1)[1] if ") " in line else line
                    )
                else:
                    line_without_numbering = line
                assert re.match(
                    r"^[A-Za-z ]+:", line_without_numbering
                ), f"Day line should be complete: {line}"

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_compact_format_day_separation(self):
        """Test that days are properly separated and don't run together."""
        sample_forecast = """Tonight: Rain showers likely, mainly before 7am. Low around 52. Southeast wind 5 mph. Chance of precipitation is 80%.
Tuesday: Rain showers likely, mainly before 7am. High near 64. Southeast wind 5 mph. Chance of precipitation is 60%.
Tuesday Night: Partly cloudy, with a low around 47. West wind 5 mph."""

        # Format the compact forecast
        compact_result = format_compact_forecast(sample_forecast)

        # Split into lines
        lines = compact_result.split("\n")

        # Find day lines
        day_lines = [
            line
            for line in lines
            if ":" in line
            and any(
                day in line
                for day in [
                    "Tonight",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                ]
            )
        ]

        # Should have 3 day lines (Tonight, Tuesday, Tuesday Night)
        assert len(day_lines) == 3, f"Expected 3 day lines, got {len(day_lines)}"

        # Check that each day is properly formatted
        assert "Tonight:" in day_lines[0], "First line should be Tonight"
        assert "Tuesday:" in day_lines[1], "Second line should be Tuesday"
        assert "Tuesday Night:" in day_lines[2], "Third line should be Tuesday Night"

        # Check that days don't run together (no day names in the middle of lines)
        for line in day_lines:
            # Should not have multiple day names in one line
            day_count = sum(
                1
                for day in [
                    "Tonight",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                ]
                if day in line
            )
            assert day_count == 1, f"Line should contain exactly one day name: {line}"
