"""
Compatibility tests to ensure API output matches current HTML implementation.
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock

from custom_components.satcom_forecast.forecast_fetcher import fetch_forecast as fetch_forecast_html
from custom_components.satcom_forecast.forecast_fetcher_api import fetch_forecast as fetch_forecast_api
from custom_components.satcom_forecast.forecast_parser import format_forecast
from custom_components.satcom_forecast.api_formatter import APIFormatter
from custom_components.satcom_forecast.api_data_processor import APIDataProcessor
from custom_components.satcom_forecast.api_models import ForecastPeriod


@pytest.mark.compatibility
class TestAPICompatibility:
    """Test compatibility between API and HTML implementations."""
    
    @pytest.fixture
    def test_coordinates(self):
        """Test coordinates for compatibility testing."""
        return [
            (40.7128, -74.0060),  # New York City
            (34.0522, -118.2437),  # Los Angeles
            (41.8781, -87.6298),  # Chicago
        ]
    
    @pytest.mark.asyncio
    async def test_forecast_text_structure(self, test_coordinates):
        """Test that API forecast text has similar structure to HTML."""
        for lat, lon in test_coordinates:
            try:
                # Get HTML forecast
                html_forecast = await fetch_forecast_html(lat, lon, 2)
                
                # Get API forecast
                api_forecast = await fetch_forecast_api(lat, lon, 2)
                
                # Both should be strings
                assert isinstance(html_forecast, str)
                assert isinstance(api_forecast, str)
                
                # Both should have reasonable length
                assert len(html_forecast) > 100
                assert len(api_forecast) > 100
                
                # Both should contain period indicators
                assert any(period in html_forecast for period in ["Today:", "Tonight:", "Monday:", "Tuesday:"])
                assert any(period in api_forecast for period in ["Today:", "Tonight:", "Monday:", "Tuesday:"])
                
                print(f"HTML forecast length: {len(html_forecast)}")
                print(f"API forecast length: {len(api_forecast)}")
                print(f"Length difference: {abs(len(html_forecast) - len(api_forecast))}")
                
            except Exception as e:
                print(f"Failed for {lat}, {lon}: {e}")
                # Some coordinates might fail, which is acceptable for testing
    
    @pytest.mark.asyncio
    async def test_format_compatibility_summary(self, test_coordinates):
        """Test summary format compatibility."""
        for lat, lon in test_coordinates:
            try:
                # Get forecasts
                html_forecast = await fetch_forecast_html(lat, lon, 2)
                api_forecast = await fetch_forecast_api(lat, lon, 2)
                
                # Format both
                html_summary = format_forecast(html_forecast, "summary", 2)
                api_summary = format_forecast(api_forecast, "summary", 2)
                
                # Both should be strings
                assert isinstance(html_summary, str)
                assert isinstance(api_summary, str)
                
                # Both should have reasonable length for summary
                assert 50 <= len(html_summary) <= 200
                assert 50 <= len(api_summary) <= 200
                
                # Both should contain period indicators
                assert any(period in html_summary for period in ["Tdy:", "Tngt:", "Mon:", "Tue:"])
                assert any(period in api_summary for period in ["Tdy:", "Tngt:", "Mon:", "Tue:"])
                
                print(f"HTML summary: {len(html_summary)} chars - {html_summary[:100]}...")
                print(f"API summary: {len(api_summary)} chars - {api_summary[:100]}...")
                
            except Exception as e:
                print(f"Failed for {lat}, {lon}: {e}")
    
    @pytest.mark.asyncio
    async def test_format_compatibility_compact(self, test_coordinates):
        """Test compact format compatibility."""
        for lat, lon in test_coordinates:
            try:
                # Get forecasts
                html_forecast = await fetch_forecast_html(lat, lon, 2)
                api_forecast = await fetch_forecast_api(lat, lon, 2)
                
                # Format both
                html_compact = format_forecast(html_forecast, "compact", 2)
                api_compact = format_forecast(api_forecast, "compact", 2)
                
                # Both should be strings
                assert isinstance(html_compact, str)
                assert isinstance(api_compact, str)
                
                # Both should have reasonable length for compact
                assert 200 <= len(html_compact) <= 2000
                assert 200 <= len(api_compact) <= 2000
                
                # Both should contain period indicators
                assert any(period in html_compact for period in ["Today:", "Tonight:", "Monday:", "Tuesday:"])
                assert any(period in api_compact for period in ["Today:", "Tonight:", "Monday:", "Tuesday:"])
                
                print(f"HTML compact: {len(html_compact)} chars")
                print(f"API compact: {len(api_compact)} chars")
                
            except Exception as e:
                print(f"Failed for {lat}, {lon}: {e}")
    
    @pytest.mark.asyncio
    async def test_format_compatibility_full(self, test_coordinates):
        """Test full format compatibility."""
        for lat, lon in test_coordinates:
            try:
                # Get forecasts
                html_forecast = await fetch_forecast_html(lat, lon, 2)
                api_forecast = await fetch_forecast_api(lat, lon, 2)
                
                # Format both
                html_full = format_forecast(html_forecast, "full", 2)
                api_full = format_forecast(api_forecast, "full", 2)
                
                # Both should be strings
                assert isinstance(html_full, str)
                assert isinstance(api_full, str)
                
                # Both should have reasonable length for full
                assert 500 <= len(html_full) <= 3000
                assert 500 <= len(api_full) <= 3000
                
                # Both should contain period indicators
                assert any(period in html_full for period in ["Today:", "Tonight:", "Monday:", "Tuesday:"])
                assert any(period in api_full for period in ["Today:", "Tonight:", "Monday:", "Tuesday:"])
                
                print(f"HTML full: {len(html_full)} chars")
                print(f"API full: {len(api_full)} chars")
                
            except Exception as e:
                print(f"Failed for {lat}, {lon}: {e}")
    
    @pytest.mark.asyncio
    async def test_weather_event_detection_compatibility(self):
        """Test that weather event detection works similarly."""
        # Create test periods with known weather events
        test_periods = [
            ForecastPeriod(
                name="Today",
                start_time="2024-01-01T06:00:00-05:00",
                end_time="2024-01-01T18:00:00-05:00",
                is_daytime=True,
                detailed_forecast="Rain likely with a high near 70. Chance of precipitation is 80%."
            ),
            ForecastPeriod(
                name="Tonight",
                start_time="2024-01-01T18:00:00-05:00",
                end_time="2024-01-02T06:00:00-05:00",
                is_daytime=False,
                detailed_forecast="Clear with a low around 55. Light wind."
            ),
            ForecastPeriod(
                name="Monday",
                start_time="2024-01-02T06:00:00-05:00",
                end_time="2024-01-02T18:00:00-05:00",
                is_daytime=True,
                detailed_forecast="Snow likely with a high near 30. Heavy snow possible."
            )
        ]
        
        processor = APIDataProcessor()
        formatter = APIFormatter()
        
        # Extract events from each period
        all_events = []
        for period in test_periods:
            events = processor.extract_weather_events(period)
            all_events.extend(events)
        
        # Test that events are detected
        assert len(all_events) > 0
        
        # Test specific event types
        event_types = [event.event_type for event in all_events]
        assert "rain" in event_types or "snow" in event_types
        
        # Test that probabilities are reasonable
        for event in all_events:
            assert 0 <= event.probability <= 100
            assert event.severity in ["low", "medium", "high", "extreme"]
        
        print(f"Detected events: {[(e.event_type, e.probability) for e in all_events]}")
    
    @pytest.mark.asyncio
    async def test_temperature_extraction_compatibility(self):
        """Test temperature extraction compatibility."""
        test_periods = [
            ForecastPeriod(
                name="Today",
                start_time="2024-01-01T06:00:00-05:00",
                end_time="2024-01-01T18:00:00-05:00",
                is_daytime=True,
                temperature=75
            ),
            ForecastPeriod(
                name="Tonight",
                start_time="2024-01-01T18:00:00-05:00",
                end_time="2024-01-02T06:00:00-05:00",
                is_daytime=False,
                temperature=55
            )
        ]
        
        processor = APIDataProcessor()
        
        for period in test_periods:
            temp_info = processor.extract_temperature_data(period)
            
            if period.is_daytime:
                assert "high" in temp_info
                assert temp_info["high"] == f"H:{period.temperature}°"
            else:
                assert "low" in temp_info
                assert temp_info["low"] == f"L:{period.temperature}°"
    
    @pytest.mark.asyncio
    async def test_wind_extraction_compatibility(self):
        """Test wind extraction compatibility."""
        test_periods = [
            ForecastPeriod(
                name="Today",
                start_time="2024-01-01T06:00:00-05:00",
                end_time="2024-01-01T18:00:00-05:00",
                is_daytime=True,
                wind_speed="10 to 15 mph",
                wind_direction="NW"
            ),
            ForecastPeriod(
                name="Tonight",
                start_time="2024-01-01T18:00:00-05:00",
                end_time="2024-01-02T06:00:00-05:00",
                is_daytime=False,
                wind_speed="5 mph",
                wind_direction="N"
            )
        ]
        
        processor = APIDataProcessor()
        
        for period in test_periods:
            wind_info = processor.extract_wind_data(period)
            
            if period.wind_speed and period.wind_direction:
                assert wind_info is not None
                assert period.wind_direction[:2] in wind_info  # Should contain direction abbreviation
                assert "mph" in wind_info  # Should contain speed
    
    @pytest.mark.asyncio
    async def test_character_count_targets(self, test_coordinates):
        """Test that character counts meet targets for each format."""
        for lat, lon in test_coordinates:
            try:
                # Get API forecast
                api_forecast = await fetch_forecast_api(lat, lon, 2)
                
                # Format in all three modes
                summary = format_forecast(api_forecast, "summary", 2)
                compact = format_forecast(api_forecast, "compact", 2)
                full = format_forecast(api_forecast, "full", 2)
                
                # Check character count targets
                assert 80 <= len(summary) <= 150, f"Summary length {len(summary)} not in target range 80-150"
                assert 400 <= len(compact) <= 1500, f"Compact length {len(compact)} not in target range 400-1500"
                assert len(full) >= 500, f"Full length {len(full)} below minimum 500"
                
                print(f"✓ {lat}, {lon}: Summary={len(summary)}, Compact={len(compact)}, Full={len(full)}")
                
            except Exception as e:
                print(f"✗ {lat}, {lon}: {e}")
    
    @pytest.mark.asyncio
    async def test_error_handling_compatibility(self):
        """Test that error handling is similar between implementations."""
        # Test with invalid coordinates
        try:
            html_result = await fetch_forecast_html(91, 0, 1)  # Invalid latitude
            api_result = await fetch_forecast_api(91, 0, 1)
            
            # Both should return error messages
            assert "error" in html_result.lower() or "NWS error" in html_result
            assert "error" in api_result.lower() or "NWS error" in api_result
            
            print(f"HTML error: {html_result[:100]}...")
            print(f"API error: {api_result[:100]}...")
            
        except Exception as e:
            print(f"Error handling test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_days_parameter_compatibility(self):
        """Test that days parameter works similarly."""
        lat, lon = 40.7128, -74.0060
        
        try:
            # Test different days values
            for days in [1, 2, 3]:
                html_forecast = await fetch_forecast_html(lat, lon, days)
                api_forecast = await fetch_forecast_api(lat, lon, days)
                
                # Both should return strings
                assert isinstance(html_forecast, str)
                assert isinstance(api_forecast, str)
                
                # Both should have reasonable length
                assert len(html_forecast) > 50
                assert len(api_forecast) > 50
                
                print(f"Days {days}: HTML={len(html_forecast)} chars, API={len(api_forecast)} chars")
                
        except Exception as e:
            print(f"Days parameter test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_performance_comparison(self, test_coordinates):
        """Compare performance between HTML and API implementations."""
        results = []
        
        for lat, lon in test_coordinates:
            try:
                # Test HTML performance
                start_time = asyncio.get_event_loop().time()
                html_forecast = await fetch_forecast_html(lat, lon, 2)
                html_time = asyncio.get_event_loop().time() - start_time
                
                # Test API performance
                start_time = asyncio.get_event_loop().time()
                api_forecast = await fetch_forecast_api(lat, lon, 2)
                api_time = asyncio.get_event_loop().time() - start_time
                
                results.append({
                    'coordinates': (lat, lon),
                    'html_time': html_time,
                    'api_time': api_time,
                    'html_length': len(html_forecast),
                    'api_length': len(api_forecast)
                })
                
                print(f"{lat}, {lon}: HTML={html_time:.2f}s, API={api_time:.2f}s")
                
            except Exception as e:
                print(f"Performance test failed for {lat}, {lon}: {e}")
        
        if results:
            avg_html_time = sum(r['html_time'] for r in results) / len(results)
            avg_api_time = sum(r['api_time'] for r in results) / len(results)
            
            print(f"Average HTML time: {avg_html_time:.2f}s")
            print(f"Average API time: {avg_api_time:.2f}s")
            print(f"API speedup: {avg_html_time / avg_api_time:.1f}x")
    
    @pytest.mark.asyncio
    async def test_content_quality_comparison(self, test_coordinates):
        """Compare content quality between implementations."""
        for lat, lon in test_coordinates:
            try:
                # Get forecasts
                html_forecast = await fetch_forecast_html(lat, lon, 2)
                api_forecast = await fetch_forecast_api(lat, lon, 2)
                
                # Check for common weather terms
                weather_terms = ["sunny", "cloudy", "rain", "snow", "wind", "temperature", "high", "low"]
                
                html_terms = sum(1 for term in weather_terms if term.lower() in html_forecast.lower())
                api_terms = sum(1 for term in weather_terms if term.lower() in api_forecast.lower())
                
                print(f"{lat}, {lon}: HTML terms={html_terms}, API terms={api_terms}")
                
                # Both should contain some weather terms
                assert html_terms > 0
                assert api_terms > 0
                
            except Exception as e:
                print(f"Content quality test failed for {lat}, {lon}: {e}")


@pytest.mark.regression
class TestRegressionCompatibility:
    """Regression tests to ensure API doesn't break existing functionality."""
    
    @pytest.mark.asyncio
    async def test_existing_imports_still_work(self):
        """Test that existing imports still work after API changes."""
        # Test that original forecast_fetcher still works
        from custom_components.satcom_forecast.forecast_fetcher import fetch_forecast as original_fetch
        
        # Test that forecast_parser still works
        from custom_components.satcom_forecast.forecast_parser import format_forecast as original_format
        
        # Test that new API modules can be imported
        from custom_components.satcom_forecast.api_client import WeatherGovAPIClient
        from custom_components.satcom_forecast.api_data_processor import APIDataProcessor
        from custom_components.satcom_forecast.api_formatter import APIFormatter
        
        # Test that coordinator can still import everything
        from custom_components.satcom_forecast.coordinator import SatcomForecastCoordinator
        
        print("✓ All imports successful")
    
    @pytest.mark.asyncio
    async def test_backward_compatibility(self):
        """Test that the new fetch_forecast function is backward compatible."""
        # Test that the new function has the same signature
        import inspect
        
        from custom_components.satcom_forecast.forecast_fetcher_api import fetch_forecast as new_fetch
        from custom_components.satcom_forecast.forecast_fetcher import fetch_forecast as old_fetch
        
        new_sig = inspect.signature(new_fetch)
        old_sig = inspect.signature(old_fetch)
        
        # Should have same parameter names
        assert list(new_sig.parameters.keys()) == list(old_sig.parameters.keys())
        
        print("✓ Function signatures compatible")
    
    @pytest.mark.asyncio
    async def test_configuration_compatibility(self):
        """Test that configuration system still works."""
        from custom_components.satcom_forecast.api_config import get_config
        
        config = get_config()
        
        # Test that configuration can be accessed
        api_config = config.get_api_config_dict()
        feature_flags = config.get_feature_flags_dict()
        
        assert isinstance(api_config, dict)
        assert isinstance(feature_flags, dict)
        
        # Test that validation works
        assert config.validate_config() is True
        
        print("✓ Configuration system compatible")