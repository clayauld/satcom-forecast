
import pytest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass
from custom_components.satcom_forecast.forecast_fetcher_api import ForecastFetcherAPI

@dataclass
class MockPeriod:
    name: str
    is_daytime: bool = True
    detailed_forecast: str = "Forecast text"

@pytest.fixture
def fetcher():
    return ForecastFetcherAPI()

def test_filter_periods_by_days_n_plus_one(fetcher):
    """Test that N days request returns N+1 days of forecast."""
    periods = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day in days:
        periods.append(MockPeriod(name=day, is_daytime=True))
        periods.append(MockPeriod(name=f"{day} Night", is_daytime=False))
        
    # Test days=0 (Today) -> Should return 1 day (2 periods: Day + Night)
    # Note: If we start with Day, we get Day + Night.
    # If we start with Night, we might get just Night? The logic handles transitions.
    # Let's assume standard start with Day.
    
    # days=0 -> target_days=1
    result_0 = fetcher._filter_periods_by_days(periods, days=0)
    # Day 1: Monday (Day), Monday Night (Night) -> 2 periods
    assert len(result_0) == 2
    assert result_0[0].name == "Monday"
    assert result_0[1].name == "Monday Night"
    
    # days=1 -> target_days=2
    result_1 = fetcher._filter_periods_by_days(periods, days=1)
    # Day 1: Monday, Monday Night
    # Day 2: Tuesday, Tuesday Night
    # Total 4 periods
    assert len(result_1) == 4
    assert result_1[-1].name == "Tuesday Night"
    
    # days=2 -> target_days=3
    result_2 = fetcher._filter_periods_by_days(periods, days=2)
    assert len(result_2) == 6
    assert result_2[-1].name == "Wednesday Night"

def test_filter_periods_holiday_grouping(fetcher):
    """Test that holidays and their nights are grouped as a single day."""
    periods = [
        MockPeriod(name="Today", is_daytime=True),
        MockPeriod(name="Tonight", is_daytime=False),
        MockPeriod(name="Wednesday", is_daytime=True),
        MockPeriod(name="Wednesday Night", is_daytime=False),
        MockPeriod(name="Thanksgiving Day", is_daytime=True),
        MockPeriod(name="Thursday Night", is_daytime=False),
        MockPeriod(name="Friday", is_daytime=True),
        MockPeriod(name="Friday Night", is_daytime=False),
    ]
    
    # Request 2 days (Today + Wednesday + Thanksgiving) -> target_days=3
    # Wait, days=2 means "Today + 2 days" -> Today, Wed, Thanksgiving.
    # So we expect 3 days.
    
    result = fetcher._filter_periods_by_days(periods, days=2)
    
    # Day 1: Today, Tonight
    # Day 2: Wednesday, Wednesday Night
    # Day 3: Thanksgiving Day, Thursday Night
    # Total 6 periods
    
    assert len(result) == 6
    assert result[4].name == "Thanksgiving Day"
    assert result[5].name == "Thursday Night"
    
    # Verify strict grouping
    # If logic was broken, "Thanksgiving Day" and "Thursday Night" might be split
    # causing it to return fewer periods or cut off early if it counted them as 2 days.
    
    # Let's try days=1 (Today + Wed) -> 4 periods
    result_1 = fetcher._filter_periods_by_days(periods, days=1)
    assert len(result_1) == 4
    assert result_1[-1].name == "Wednesday Night"

def test_filter_periods_start_at_night(fetcher):
    """Test filtering when forecast starts at night (e.g. Tonight)."""
    periods = [
        MockPeriod(name="Tonight", is_daytime=False),
        MockPeriod(name="Wednesday", is_daytime=True),
        MockPeriod(name="Wednesday Night", is_daytime=False),
    ]
    
    # days=0 -> target_days=1
    # Should return just Tonight (Day 1)
    result = fetcher._filter_periods_by_days(periods, days=0)
    assert len(result) == 1
    assert result[0].name == "Tonight"
    
    # days=1 -> target_days=2
    # Day 1: Tonight
    # Day 2: Wednesday, Wednesday Night
    result_2 = fetcher._filter_periods_by_days(periods, days=1)
    assert len(result_2) == 3
    assert result_2[1].name == "Wednesday"
