import os
import sys

import pytest

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__), "..", "custom_components", "satcom_forecast"
    ),
)
from forecast_parser import format_forecast  # noqa: E402
from split_util import split_message  # noqa: E402

TEST_FORECAST = """This Afternoon: A chance of showers. Mostly cloudy, with a high near 50. Southeast wind around 10 mph. Chance of precipitation is 40%.
Tonight: Showers likely, mainly between 7pm and 10pm, then rain after 10pm. Low around 41. Southeast wind around 15 mph. Chance of precipitation is 80%.
Thursday: Rain likely. Cloudy, with a high near 49. Southeast wind 10 to 15 mph. Chance of precipitation is 70%."""


class TestTextLength:
    """Test text length functionality and character limits."""

    def test_basic_text_lengths(self) -> None:
        """Test that formatted text has reasonable lengths."""
        summary_text = format_forecast(TEST_FORECAST, mode="summary")
        compact_text = format_forecast(TEST_FORECAST, mode="compact")
        full_text = format_forecast(TEST_FORECAST, mode="full")

        # Summary should be shortest
        assert len(summary_text) < len(compact_text)
        assert len(compact_text) < len(full_text)

        # All should have reasonable lengths (not empty, not extremely long)
        assert len(summary_text) > 20
        assert len(compact_text) > 50
        assert len(full_text) > 100

    def test_device_character_limits(self) -> None:
        """Test that text splitting respects device character limits."""
        summary_text = format_forecast(TEST_FORECAST, mode="summary")

        # Test ZOLEO limit (200 chars)
        zoleo_parts = split_message(summary_text, device_type="zoleo")
        for part in zoleo_parts:
            assert len(part) <= 200, f"ZOLEO part exceeds 200 chars: {len(part)} chars"

        # Test InReach limit (160 chars)
        inreach_parts = split_message(summary_text, device_type="inreach")
        for part in inreach_parts:
            assert (
                len(part) <= 160
            ), f"InReach part exceeds 160 chars: {len(part)} chars"

    def test_custom_character_limits(self) -> None:
        """Test custom character limit overrides."""
        summary_text = format_forecast(TEST_FORECAST, mode="summary")

        # Test custom limits
        custom_limits = [50, 100, 150, 300]
        for limit in custom_limits:
            parts = split_message(summary_text, custom_limit=limit)
            for part in parts:
                assert (
                    len(part) <= limit
                ), f"Custom limit {limit} exceeded: {len(part)} chars"

    def test_character_limit_priority(self):
        """Test that custom limits override device type limits."""
        summary_text = format_forecast(TEST_FORECAST, mode="summary")

        # Custom limit should override device type
        parts = split_message(summary_text, device_type="zoleo", custom_limit=100)
        for part in parts:
            assert (
                len(part) <= 100
            ), f"Custom limit should override ZOLEO limit: {len(part)} chars"

        # Custom limit should override InReach
        parts = split_message(summary_text, device_type="inreach", custom_limit=200)
        for part in parts:
            assert (
                len(part) <= 200
            ), f"Custom limit should override InReach limit: {len(part)} chars"

    def test_part_numbering_overhead(self):
        """Test that part numbering is included in character limits."""
        # Create a text that's exactly at the limit
        long_text = "A" * 190  # Just under ZOLEO limit

        parts = split_message(long_text, device_type="zoleo")

        # Should be split into multiple parts with numbering
        if len(parts) > 1:
            for part in parts:
                # Part numbering format: "(1/2) " = 7 chars
                assert (
                    len(part) <= 200
                ), f"Part with numbering exceeds limit: {len(part)} chars"
                assert part.startswith("("), "Part should have numbering prefix"

    def test_edge_case_limits(self):
        """Test edge cases for character limits."""
        summary_text = format_forecast(TEST_FORECAST, mode="summary")

        # Test zero limit (should use default)
        parts_zero = split_message(summary_text, custom_limit=0)
        assert len(parts_zero) > 0, "Zero limit should use default"

        # Test negative limit (should use default)
        parts_negative = split_message(summary_text, custom_limit=-1)
        assert len(parts_negative) > 0, "Negative limit should use default"

        # Test very small limit (but not too small to avoid infinite loops)
        parts_small = split_message(summary_text, custom_limit=50)
        for part in parts_small:
            assert len(part) <= 50, f"Very small limit exceeded: {len(part)} chars"

    def test_different_formats_with_limits(self):
        """Test that all formats work with character limits."""
        formats = ["summary", "compact", "full"]
        limits = [100, 150, 200]

        for format_type in formats:
            formatted_text = format_forecast(TEST_FORECAST, mode=format_type)

            for limit in limits:
                parts = split_message(formatted_text, custom_limit=limit)

                # All parts should respect the limit
                for part in parts:
                    assert (
                        len(part) <= limit
                    ), f"{format_type} format exceeds {limit} limit: {len(part)} chars"

                # Should have at least one part
                assert (
                    len(parts) > 0
                ), f"{format_type} format should produce at least one part"

    def test_text_utilization(self):
        """Test that text splitting maximizes character utilization."""
        summary_text = format_forecast(TEST_FORECAST, mode="summary")

        # Test with a reasonable limit
        parts = split_message(summary_text, custom_limit=150)

        if len(parts) == 1:
            # Single part should use most of the available space
            utilization = len(parts[0]) / 150
            assert (
                utilization > 0.4
            ), f"Low utilization in single part: {utilization:.2%}"
        else:
            # Multiple parts should have good utilization
            total_chars = sum(len(part) for part in parts)
            total_limit = 150 * len(parts)
            utilization = total_chars / total_limit
            assert utilization > 0.4, f"Low utilization across parts: {utilization:.2%}"

    def test_empty_and_short_text(self):
        """Test handling of empty and very short text."""
        # Empty text
        empty_parts = split_message("", device_type="zoleo")
        assert len(empty_parts) == 1, "Empty text should produce one part"
        assert empty_parts[0] == "", "Empty text part should be empty string"

        # Very short text
        short_text = "Short"
        short_parts = split_message(short_text, device_type="zoleo")
        assert len(short_parts) == 1, "Short text should produce one part"
        assert short_parts[0] == short_text, "Short text should remain unchanged"

    @pytest.mark.parametrize(
        "device_type,expected_limit",
        [
            ("zoleo", 200),
            ("inreach", 160),
            ("unknown", 200),  # Should default to ZOLEO
        ],
    )
    def test_device_type_defaults(self, device_type: str, expected_limit: int) -> None:
        """Test that device types have correct default limits."""
        summary_text = format_forecast(TEST_FORECAST, mode="summary")

        parts = split_message(summary_text, device_type=device_type)

        for part in parts:
            assert (
                len(part) <= expected_limit
            ), f"{device_type} should respect {expected_limit} limit: {len(part)} chars"

    def test_mixed_format_splitting(self):
        """Test splitting with different text formats."""
        # Test summary format (pipe-separated)
        summary_text = format_forecast(TEST_FORECAST, mode="summary")
        summary_parts = split_message(summary_text, custom_limit=100)

        # Test compact format (newline-separated)
        compact_text = format_forecast(TEST_FORECAST, mode="compact")
        compact_parts = split_message(compact_text, custom_limit=100)

        # Both should respect limits
        for part in summary_parts:
            assert (
                len(part) <= 100
            ), f"Summary format part exceeds limit: {len(part)} chars"

        for part in compact_parts:
            assert (
                len(part) <= 100
            ), f"Compact format part exceeds limit: {len(part)} chars"
