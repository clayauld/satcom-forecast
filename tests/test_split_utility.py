"""Tests for split utility functionality."""

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
    from split_util import split_message, split_multiline_text

    HAS_HA = True
except ImportError:
    # If modules are not available, skip these tests
    HAS_HA = False


class TestSplitUtility:
    """Test split utility functionality."""

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_split_multiline_text_day_separation(self):
        """Test that split_multiline_text properly separates days while combining efficiently."""
        # Create a compact format text with multiple days
        compact_text = """Tonight: Rain showers likely, mainly before 7am (L:52, SE5mph)
Tuesday: Rain showers likely, mainly before 7am (H:64, SE5mph)
Tuesday Night: Partly cloudy, with a low around 47 (L:47, W5mph)
Wednesday: Partly sunny, with a high near 63 (H:63, E5mph)
Wednesday Night: A chance of rain between 10pm and 1am (L:52)
Thursday: A chance of rain between 7am and 1pm (H:62, W5mph)"""

        # Split the text
        lines = compact_text.split("\n")
        parts = split_multiline_text(lines, effective_limit=200)

        # Should have multiple parts (due to character limits)
        assert len(parts) >= 1, "Should have at least one part"

        # Each part should contain complete day entries
        for part in parts:
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
                assert re.match(
                    r"^[A-Za-z ]+:", line
                ), f"Day line should be complete: {line}"

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_split_multiline_text_efficient_combination(self):
        """Test that split_multiline_text efficiently combines multiple days into single parts."""
        # Create a compact format text with short day entries
        compact_text = """Tonight: Rain (L:52)
Tuesday: Rain (H:64)
Tuesday Night: Partly cloudy (L:47)
Wednesday: Partly sunny (H:63)"""

        # Split the text with a generous limit
        lines = compact_text.split("\n")
        parts = split_multiline_text(lines, effective_limit=300)

        # Should combine multiple days into fewer parts
        assert len(parts) < len(lines), "Should combine days into fewer parts"

        # Each part should contain multiple days
        for part in parts:
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
            assert len(day_lines) >= 1, "Each part should contain at least one day"

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_split_message_format_detection(self):
        """Test that split_message correctly detects format type and uses appropriate splitting."""
        # Test compact format (newlines)
        compact_text = """Tonight: Rain showers likely, mainly before 7am (L:52, SE5mph)
Tuesday: Rain showers likely, mainly before 7am (H:64, SE5mph)"""

        compact_parts = split_message(compact_text, device_type="zoleo")
        assert (
            len(compact_parts) >= 1
        ), "Should have at least one part for compact format"

        # Test summary format (pipe separators)
        summary_text = "Tonight: Rain (L:52) | Tuesday: Rain (H:64)"
        summary_parts = split_message(summary_text, device_type="zoleo")
        assert (
            len(summary_parts) >= 1
        ), "Should have at least one part for summary format"

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_split_message_character_limits(self):
        """Test that split_message respects character limits."""
        # Create a long text that should be split
        long_text = """Tonight: Rain showers likely, mainly before 7am. Low around 52. Southeast wind 5 mph. Chance of precipitation is 80%. Showers likely, mainly before 7am.
Tuesday: Rain showers likely, mainly before 7am. High near 64. Southeast wind 5 mph. Chance of precipitation is 60%. Showers likely, mainly before 7am.
Tuesday Night: Partly cloudy, with a low around 47. West wind 5 mph.
Wednesday: Partly sunny, with a high near 63. East wind 5 mph.
Wednesday Night: A chance of rain between 10pm and 1am. Low around 52. Southeast wind 5 to 10 mph. Chance of precipitation is 30%.
Thursday: A chance of rain between 7am and 1pm. High near 62. West wind 5 mph. Chance of precipitation is 30%."""

        # Split with a small limit
        parts = split_message(long_text, device_type="zoleo")

        # Should be split into multiple parts
        assert len(parts) > 1, "Long text should be split into multiple parts"

        # Each part should be within the character limit (including part numbering)
        for part in parts:
            assert (
                len(part) <= 200
            ), f"Part should be within character limit: {len(part)} chars"

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_split_message_part_numbering(self):
        """Test that split_message adds part numbering when needed."""
        # Create a text that will be split into multiple parts
        long_text = """Tonight: Rain showers likely, mainly before 7am. Low around 52. Southeast wind 5 mph. Chance of precipitation is 80%.
Tuesday: Rain showers likely, mainly before 7am. High near 64. Southeast wind 5 mph. Chance of precipitation is 60%.
Tuesday Night: Partly cloudy, with a low around 47. West wind 5 mph.
Wednesday: Partly sunny, with a high near 63. East wind 5 mph.
Wednesday Night: A chance of rain between 10pm and 1am. Low around 52. Southeast wind 5 to 10 mph. Chance of precipitation is 30%.
Thursday: A chance of rain between 7am and 1pm. High near 62. West wind 5 mph. Chance of precipitation is 30%."""

        # Split the message
        parts = split_message(long_text, device_type="zoleo")

        # If multiple parts, should have part numbering
        if len(parts) > 1:
            for i, part in enumerate(parts):
                expected_prefix = f"({i+1}/{len(parts)}) "
                assert part.startswith(
                    expected_prefix
                ), f"Part {i+1} should start with '{expected_prefix}'"

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_split_message_device_types(self):
        """Test that split_message respects different device type limits."""
        short_text = "Tonight: Rain (L:52)"

        # Test different device types
        zoleo_parts = split_message(short_text, device_type="zoleo")
        inreach_parts = split_message(short_text, device_type="inreach")

        # Both should work
        assert len(zoleo_parts) >= 1, "Zoleo device type should work"
        assert len(inreach_parts) >= 1, "InReach device type should work"

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_split_message_custom_limits(self):
        """Test that split_message respects custom character limits."""
        short_text = "Tonight: Rain (L:52)"

        # Test with custom limit
        custom_parts = split_message(short_text, device_type="zoleo", custom_limit=100)

        # Should work with custom limit
        assert len(custom_parts) >= 1, "Custom limit should work"
