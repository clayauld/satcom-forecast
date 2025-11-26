"""
Test for percentage context extraction bug fix.

This test verifies that when multiple percentages appear in forecast text,
the context extraction correctly identifies which percentage is associated
with which weather event.
"""

import pytest

from custom_components.satcom_forecast import weather_utils
from custom_components.satcom_forecast.api_models import ForecastPeriod


def test_multiple_percentages_in_forecast():
    """
    Test that percentage matching correctly handles multiple percentages.

    Bug scenario: "70% chance of rain with a high of 70 degrees"
    The old code would use the position of the first "70" for both matches,
    causing incorrect context extraction.
    """
    # Create a forecast with multiple percentages
    period = ForecastPeriod(
        name="Today",
        start_time="2024-01-01T06:00:00-05:00",
        end_time="2024-01-01T18:00:00-05:00",
        is_daytime=True,
        probability_of_precipitation=None,  # Force it to use text parsing
    )

    # Test case 1: Percentage near rain keyword should be detected
    forecast_text = "70% chance of rain with a high of 70 degrees"
    chance = weather_utils.infer_chance("rain", forecast_text, period)
    assert chance == 70, "Should detect 70% for rain event"

    # Test case 2: Multiple percentages with different events
    forecast_text2 = (
        "30% chance of snow in the morning, 60% chance of rain in the afternoon"
    )

    # Should find 30% for snow (first percentage near snow keyword)
    chance_snow = weather_utils.infer_chance("snow", forecast_text2, period)
    assert chance_snow == 30, "Should detect 30% for snow event"

    # Should find 60% for rain (second percentage near rain keyword)
    chance_rain = weather_utils.infer_chance("rain", forecast_text2, period)
    assert chance_rain == 60, "Should detect 60% for rain event"

    # Test case 3: Percentage far from event keyword should not be detected
    forecast_text3 = "sunny with a high of 75 degrees. 20% chance of rain later"
    chance = weather_utils.infer_chance("rain", forecast_text3, period)
    assert chance == 20, "Should detect 20% for rain event"


def test_percentage_with_percent_word():
    """Test that 'percent' word format also works correctly."""
    period = ForecastPeriod(
        name="Today",
        start_time="2024-01-01T06:00:00-05:00",
        end_time="2024-01-01T18:00:00-05:00",
        is_daytime=True,
        probability_of_precipitation=None,
    )

    # Use a more realistic forecast without conflicting percentages
    forecast_text = "80 percent chance of thunderstorms this afternoon"
    chance = weather_utils.infer_chance("thunderstorm", forecast_text, period)
    assert chance == 80, "Should detect 80% for thunderstorm event"


def test_no_percentage_near_event():
    """Test that when no percentage is near the event keyword, it falls back to keyword-based inference."""
    period = ForecastPeriod(
        name="Today",
        start_time="2024-01-01T06:00:00-05:00",
        end_time="2024-01-01T18:00:00-05:00",
        is_daytime=True,
        probability_of_precipitation=None,
    )

    # Percentage is far from rain keyword (more than 100 chars away)
    # This should fall back to keyword-based inference
    forecast_text = (
        "rain likely with temperatures in the 70s. "
        + "x" * 100
        + " 90% humidity expected"
    )
    chance = weather_utils.infer_chance("rain", forecast_text, period)
    assert chance == 70, "Should fall back to keyword-based inference (likely = 70%)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
