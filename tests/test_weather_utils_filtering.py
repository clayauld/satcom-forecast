"""
Test weather_utils filtering logic.
"""

import pytest

from custom_components.satcom_forecast.api_models import ForecastPeriod
from custom_components.satcom_forecast.weather_utils import filter_periods_by_days


@pytest.fixture
def mock_periods():
    """Create a list of mock forecast periods."""
    return [
        ForecastPeriod(
            name="Today",
            detailed_forecast="Sunny",
            is_daytime=True,
            start_time="2023-01-01T06:00:00",
            end_time="2023-01-01T18:00:00",
        ),
        ForecastPeriod(
            name="Tonight",
            detailed_forecast="Clear",
            is_daytime=False,
            start_time="2023-01-01T18:00:00",
            end_time="2023-01-02T06:00:00",
        ),
        ForecastPeriod(
            name="Tuesday",
            detailed_forecast="Sunny",
            is_daytime=True,
            start_time="2023-01-02T06:00:00",
            end_time="2023-01-02T18:00:00",
        ),
        ForecastPeriod(
            name="Tuesday Night",
            detailed_forecast="Clear",
            is_daytime=False,
            start_time="2023-01-02T18:00:00",
            end_time="2023-01-03T06:00:00",
        ),
        ForecastPeriod(
            name="Wednesday",
            detailed_forecast="Sunny",
            is_daytime=True,
            start_time="2023-01-03T06:00:00",
            end_time="2023-01-03T18:00:00",
        ),
        ForecastPeriod(
            name="Wednesday Night",
            detailed_forecast="Clear",
            is_daytime=False,
            start_time="2023-01-03T18:00:00",
            end_time="2023-01-04T06:00:00",
        ),
    ]


def test_filter_periods_none(mock_periods):
    """Test filtering with days=None (should return all)."""
    result = filter_periods_by_days(mock_periods, None)
    assert len(result) == 6
    assert result == mock_periods


def test_filter_periods_zero(mock_periods):
    """Test filtering with days=0 (should return Today + Tonight)."""
    # days=0 means "Today" (current day)
    # The logic is target_days = days + 1 = 1
    # It collects periods until it sees a transition from Night to Day for the next day
    result = filter_periods_by_days(mock_periods, 0)
    assert len(result) == 2
    assert result[0].name == "Today"
    assert result[1].name == "Tonight"


def test_filter_periods_one(mock_periods):
    """Test filtering with days=1 (should return Today + Tonight + Tuesday + Tuesday Night)."""
    # days=1 means "Today + Tomorrow"
    # target_days = 2
    result = filter_periods_by_days(mock_periods, 1)
    assert len(result) == 4
    assert result[2].name == "Tuesday"
    assert result[3].name == "Tuesday Night"


def test_filter_periods_start_night():
    """Test filtering when forecast starts at night."""
    periods = [
        ForecastPeriod(
            name="Tonight",
            detailed_forecast="Clear",
            is_daytime=False,
            start_time="2023-01-01T18:00:00",
            end_time="2023-01-02T06:00:00",
        ),
        ForecastPeriod(
            name="Tuesday",
            detailed_forecast="Sunny",
            is_daytime=True,
            start_time="2023-01-02T06:00:00",
            end_time="2023-01-02T18:00:00",
        ),
        ForecastPeriod(
            name="Tuesday Night",
            detailed_forecast="Clear",
            is_daytime=False,
            start_time="2023-01-02T18:00:00",
            end_time="2023-01-03T06:00:00",
        ),
        ForecastPeriod(
            name="Wednesday",
            detailed_forecast="Sunny",
            is_daytime=True,
            start_time="2023-01-03T06:00:00",
            end_time="2023-01-03T18:00:00",
        ),
    ]

    # days=0 -> Today (just Tonight in this case)
    result = filter_periods_by_days(periods, 0)
    assert len(result) == 1
    assert result[0].name == "Tonight"

    # days=1 -> Today + Tomorrow (Tonight + Tue + Tue Night)
    result = filter_periods_by_days(periods, 1)
    assert len(result) == 3
    assert result[1].name == "Tuesday"
    assert result[2].name == "Tuesday Night"


def test_filter_periods_more_than_available(mock_periods):
    """Test requesting more days than available."""
    result = filter_periods_by_days(mock_periods, 10)
    assert len(result) == 6
    assert result == mock_periods
