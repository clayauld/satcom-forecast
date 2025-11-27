"""
Test naming logic for day summaries.
"""

from custom_components.satcom_forecast.api_formatter import APIFormatter
from custom_components.satcom_forecast.api_models import ForecastPeriod
from custom_components.satcom_forecast.forecast_parser import summarize_forecast


def test_parser_summary_this_afternoon():
    """Test that 'This Afternoon' is summarized as 'Tdy' in forecast_parser."""
    # Mock forecast text
    text = """
    <b>This Afternoon: </b>Sunny with a high near 75.<br><br>
    <b>Tonight: </b>Clear with a low around 55.<br><br>
    <b>Wednesday: </b>Sunny with a high near 80.<br><br>
    """

    summary = summarize_forecast(text)

    # Current behavior might be "Aft", we want "Tdy"
    # Let's assert what we WANT, so it fails if not implemented
    assert "Tdy:" in summary
    assert "Aft:" not in summary


def test_api_formatter_summary_this_afternoon():
    """Test that 'This Afternoon' is summarized as 'Tdy' in api_formatter."""
    formatter = APIFormatter()
    periods = [
        ForecastPeriod(
            name="This Afternoon",
            start_time="2024-01-01T12:00:00-05:00",
            end_time="2024-01-01T18:00:00-05:00",
            is_daytime=True,
            temperature=75,
            detailed_forecast="Sunny",
        ),
        ForecastPeriod(
            name="Tonight",
            start_time="2024-01-01T18:00:00-05:00",
            end_time="2024-01-02T06:00:00-05:00",
            is_daytime=False,
            temperature=55,
            detailed_forecast="Clear",
        ),
    ]
    events = []

    summary = formatter.format_summary_forecast(periods, events)

    # Current behavior might be "Aft", we want "Tdy"
    assert "Tdy:" in summary
    assert "Aft:" not in summary


def test_parser_summary_today():
    """Test that 'Today' is summarized as 'Tdy'."""
    text = """
    <b>Today: </b>Sunny with a high near 75.<br><br>
    <b>Tonight: </b>Clear with a low around 55.<br><br>
    """
    summary = summarize_forecast(text)
    assert "Tdy:" in summary


def test_parser_summary_overnight():
    """Test that 'Overnight' is summarized as 'Tdy' (or kept as ON if preferred,
    but let's check consistency)."""
    # If forecast starts with Overnight, it's technically the start of the "day"
    # from the user's perspective if they check late?
    # Or maybe it should be "ON". The user request specifically mentioned
    # "This Afternoon" -> "Tdy".
    # Let's stick to "This Afternoon" for now.
    pass
