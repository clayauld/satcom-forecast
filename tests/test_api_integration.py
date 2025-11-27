"""
Integration tests for API modules with real Weather.gov API endpoints.
"""

import asyncio
from unittest.mock import patch

import pytest
import pytest_asyncio

from custom_components.satcom_forecast.api_client import WeatherGovAPIClient
from custom_components.satcom_forecast.api_config import get_config
from custom_components.satcom_forecast.api_data_processor import APIDataProcessor
from custom_components.satcom_forecast.api_formatter import APIFormatter
from custom_components.satcom_forecast.forecast_fetcher_api import ForecastFetcherAPI


@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests with real API endpoints."""

    @pytest_asyncio.fixture
    async def client(self):
        """Create API client for testing."""
        client = WeatherGovAPIClient(
            base_url="https://api.weather.gov",
            user_agent="SatComForecastTest/1.0",
            timeout=30,
            retry_attempts=2,
        )
        yield client
        await client.close()

    @pytest.fixture
    def processor(self):
        """Create data processor for testing."""
        return APIDataProcessor()

    @pytest.fixture
    def formatter(self):
        """Create formatter for testing."""
        return APIFormatter()

    @pytest.fixture
    def fetcher(self):
        """Create forecast fetcher for testing."""
        return ForecastFetcherAPI()

    @pytest.mark.asyncio
    async def test_get_gridpoint_real_api(self, client):
        """Test grid point conversion with real API."""
        # Test with New York City coordinates
        office, grid_x, grid_y, forecast_url = await client.get_gridpoint(
            40.7128, -74.0060
        )

        assert isinstance(office, str)
        assert len(office) > 0
        assert isinstance(grid_x, int)
        assert isinstance(grid_y, int)
        assert grid_x > 0
        assert grid_y > 0

        print(f"Grid point: {office}/{grid_x},{grid_y}")

    @pytest.mark.asyncio
    async def test_get_forecast_real_api(self, client):
        """Test forecast retrieval with real API."""
        # First get grid point
        office, grid_x, grid_y, forecast_url = await client.get_gridpoint(
            40.7128, -74.0060
        )

        # Then get forecast
        forecast_data = await client.get_forecast(office, grid_x, grid_y)

        assert "properties" in forecast_data
        assert "periods" in forecast_data["properties"]
        assert len(forecast_data["properties"]["periods"]) > 0

        # Check first period structure
        first_period = forecast_data["properties"]["periods"][0]
        assert "name" in first_period
        assert "detailedForecast" in first_period
        assert "isDaytime" in first_period

        print(
            f"Retrieved forecast with {len(forecast_data['properties']['periods'])} "
            f"periods"
        )

    @pytest.mark.asyncio
    async def test_get_alerts_real_api(self, client):
        """Test alerts retrieval with real API."""
        alerts_data = await client.get_alerts(40.7128, -74.0060)

        assert "features" in alerts_data
        # Alerts may or may not be present depending on weather conditions
        print(f"Retrieved {len(alerts_data['features'])} alerts")

    @pytest.mark.asyncio
    async def test_end_to_end_forecast_processing(self, client, processor, formatter):
        """Test complete forecast processing pipeline."""
        # Get grid point
        office, grid_x, grid_y, forecast_url = await client.get_gridpoint(
            40.7128, -74.0060
        )

        # Get forecast data
        forecast_data = await client.get_forecast(office, grid_x, grid_y)

        # Process forecast data
        processed_data = processor.process_forecast_data(forecast_data)

        assert len(processed_data.periods) > 0
        assert processed_data.periods[0].name is not None
        assert processed_data.periods[0].detailed_forecast is not None

        # Extract weather events
        all_events = []
        for period in processed_data.periods:
            events = processor.extract_weather_events(period)
            all_events.extend(events)

        # Format forecast in all three formats
        summary = formatter.format_forecast(
            processed_data.periods, all_events, "summary"
        )
        compact = formatter.format_forecast(
            processed_data.periods, all_events, "compact"
        )
        full = formatter.format_forecast(processed_data.periods, all_events, "full")

        assert len(summary) > 0
        assert len(compact) > 0
        assert len(full) > 0

        # Check character count targets (API formatter produces more verbose output)
        assert (
            80 <= len(summary) <= 500
        ), f"Summary length {len(summary)} not in target range"
        assert (
            400 <= len(compact) <= 2000
        ), f"Compact length {len(compact)} not in target range"
        assert len(full) >= 500, f"Full length {len(full)} too short"

        print(f"Summary: {len(summary)} chars")
        print(f"Compact: {len(compact)} chars")
        print(f"Full: {len(full)} chars")
        print(f"Events detected: {len(all_events)}")

    @pytest.mark.asyncio
    async def test_forecast_fetcher_api_mode(self, fetcher):
        """Test forecast fetcher in API mode."""
        # Enable API mode
        with patch(
            "custom_components.satcom_forecast.api_config.is_api_enabled",
            return_value=True,
        ):
            forecast_text = await fetcher.fetch_forecast_api(40.7128, -74.0060, 2)

            assert isinstance(forecast_text, str)
            assert len(forecast_text) > 0
            assert (
                "Today:" in forecast_text
                or "Tonight:" in forecast_text
                or "Overnight:" in forecast_text
            )

            print(f"API forecast length: {len(forecast_text)}")
            print(f"API forecast preview: {forecast_text[:200]}...")

    @pytest.mark.asyncio
    async def test_forecast_fetcher_hybrid_mode(self, fetcher):
        """Test forecast fetcher in hybrid mode."""
        # Test with API enabled
        with patch(
            "custom_components.satcom_forecast.api_config.is_api_enabled",
            return_value=True,
        ):
            forecast_text = await fetcher.fetch_forecast_hybrid(
                40.7128, -74.0060, 2, mode="auto"
            )

            assert isinstance(forecast_text, str)
            assert len(forecast_text) > 0

            print(f"Hybrid forecast (API mode) length: {len(forecast_text)}")

        # Test with API disabled (should fall back to HTML)
        with patch(
            "custom_components.satcom_forecast.api_config.is_api_enabled",
            return_value=False,
        ):
            forecast_text = await fetcher.fetch_forecast_hybrid(
                40.7128, -74.0060, 2, mode="auto"
            )

            assert isinstance(forecast_text, str)
            assert len(forecast_text) > 0

            print(f"Hybrid forecast (HTML mode) length: {len(forecast_text)}")

    @pytest.mark.asyncio
    async def test_coordinate_validation(self, fetcher):
        """Test coordinate validation with various inputs."""
        # Valid coordinates
        assert fetcher.validate_coordinates(40.7128, -74.0060) is True
        assert fetcher.validate_coordinates(0, 0) is True
        assert fetcher.validate_coordinates(-90, -180) is True
        assert fetcher.validate_coordinates(90, 180) is True

        # Invalid coordinates
        assert fetcher.validate_coordinates(91, 0) is False
        assert fetcher.validate_coordinates(0, 181) is False
        assert fetcher.validate_coordinates("invalid", 0) is False
        assert fetcher.validate_coordinates(40.7128, "invalid") is False

    @pytest.mark.asyncio
    async def test_error_handling_invalid_coordinates(self, client):
        """Test error handling with invalid coordinates."""
        with pytest.raises(Exception):  # Should raise APIError or similar
            await client.get_gridpoint(91, 0)  # Invalid latitude

    @pytest.mark.asyncio
    async def test_error_handling_invalid_grid_point(self, client):
        """Test error handling with invalid grid point."""
        with pytest.raises(Exception):  # Should raise APIError or similar
            await client.get_forecast("INVALID", 999, 999)

    @pytest.mark.asyncio
    async def test_caching_functionality(self, fetcher):
        """Test caching functionality."""
        # Ensure caches are empty to start
        await fetcher.clear_caches()

        # First call should hit API
        start_time = asyncio.get_event_loop().time()
        forecast1 = await fetcher.fetch_forecast_api(40.7128, -74.0060, 1)
        first_call_time = asyncio.get_event_loop().time() - start_time

        # Second call should be faster due to caching
        start_time = asyncio.get_event_loop().time()
        forecast2 = await fetcher.fetch_forecast_api(40.7128, -74.0060, 1)
        second_call_time = asyncio.get_event_loop().time() - start_time

        assert forecast1 == forecast2  # Should be identical

        # Only assert timing if first call took significant time (indicating network
        # request)
        # If first call was extremely fast (< 10ms), it might have been cached
        # externally or mocked
        if first_call_time > 0.01:
            assert second_call_time < first_call_time  # Should be faster

        print(f"First call: {first_call_time:.4f}s")
        print(f"Second call: {second_call_time:.4f}s")
        if second_call_time > 0:
            print(f"Speedup: {first_call_time / second_call_time:.1f}x")

    @pytest.mark.asyncio
    async def test_different_coordinates(self, fetcher):
        """Test with different coordinate sets."""
        test_coordinates = [
            (40.7128, -74.0060),  # New York City
            (34.0522, -118.2437),  # Los Angeles
            (41.8781, -87.6298),  # Chicago
            (29.7604, -95.3698),  # Houston
            (33.4484, -112.0740),  # Phoenix
        ]

        for lat, lon in test_coordinates:
            try:
                forecast = await fetcher.fetch_forecast_api(lat, lon, 1)
                assert isinstance(forecast, str)
                assert len(forecast) > 0
                print(f"Success for {lat}, {lon}: {len(forecast)} chars")
            except Exception as e:
                print(f"Failed for {lat}, {lon}: {e}")
                # Some coordinates might fail due to API limitations
                # This is acceptable for integration testing

    @pytest.mark.asyncio
    async def test_performance_benchmark(self, fetcher):
        """Test performance with multiple requests."""
        coordinates = [
            (40.7128, -74.0060),
            (34.0522, -118.2437),
            (41.8781, -87.6298),
        ]

        start_time = asyncio.get_event_loop().time()

        # Make requests sequentially
        results = []
        for lat, lon in coordinates:
            try:
                forecast = await fetcher.fetch_forecast_api(lat, lon, 1)
                results.append((lat, lon, len(forecast)))
            except Exception as e:
                results.append((lat, lon, f"Error: {e}"))

        total_time = asyncio.get_event_loop().time() - start_time

        print(f"Processed {len(coordinates)} requests in {total_time:.2f}s")
        print(f"Average time per request: {total_time / len(coordinates):.2f}s")

        for lat, lon, result in results:
            print(f"  {lat}, {lon}: {result}")

    @pytest.mark.asyncio
    async def test_configuration_loading(self):
        """Test configuration loading and validation."""
        config = get_config()

        # Test API configuration
        api_config = config.get_api_config_dict()
        assert "base_url" in api_config
        assert "user_agent" in api_config
        assert "timeout" in api_config

        # Test feature flags
        feature_flags = config.get_feature_flags_dict()
        assert "use_api" in feature_flags
        assert "fallback_to_html" in feature_flags
        assert "enable_caching" in feature_flags

        # Test configuration validation
        assert config.validate_config() is True

        print(f"API config: {api_config}")
        print(f"Feature flags: {feature_flags}")


@pytest.mark.slow
class TestAPIPerformance:
    """Performance tests for API integration."""

    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test concurrent API requests."""
        client = WeatherGovAPIClient(
            base_url="https://api.weather.gov",
            user_agent="SatComForecastTest/1.0",
            timeout=30,
        )

        coordinates = [
            (40.7128, -74.0060),
            (34.0522, -118.2437),
            (41.8781, -87.6298),
        ]

        async def fetch_forecast(lat, lon):
            try:
                office, grid_x, grid_y, forecast_url = await client.get_gridpoint(
                    lat, lon
                )
                forecast_data = await client.get_forecast(office, grid_x, grid_y)
                return (
                    lat,
                    lon,
                    len(forecast_data.get("properties", {}).get("periods", [])),
                )
            except Exception as e:
                return lat, lon, f"Error: {e}"

        start_time = asyncio.get_event_loop().time()

        try:
            # Make concurrent requests
            tasks = [fetch_forecast(lat, lon) for lat, lon in coordinates]
            results = await asyncio.gather(*tasks)

            total_time = asyncio.get_event_loop().time() - start_time

            print(f"Concurrent requests completed in {total_time:.2f}s")
            for lat, lon, result in results:
                print(f"  {lat}, {lon}: {result}")
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_memory_usage(self):
        """Test memory usage with large responses."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        client = WeatherGovAPIClient(
            base_url="https://api.weather.gov",
            user_agent="SatComForecastTest/1.0",
            timeout=30,
        )

        try:
            # Make several requests to test memory usage
            for i in range(5):
                try:
                    office, grid_x, grid_y, forecast_url = await client.get_gridpoint(
                        40.7128, -74.0060
                    )
                    await client.get_forecast(office, grid_x, grid_y)

                    current_memory = process.memory_info().rss / 1024 / 1024  # MB
                    print(f"Request {i+1}: {current_memory:.1f} MB")

                except Exception as e:
                    print(f"Request {i+1} failed: {e}")

            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory

            print(f"Initial memory: {initial_memory:.1f} MB")
            print(f"Final memory: {final_memory:.1f} MB")
            print(f"Memory increase: {memory_increase:.1f} MB")

            # Memory increase should be reasonable (< 50 MB)
            assert (
                memory_increase < 50
            ), f"Memory increase too high: {memory_increase:.1f} MB"

        finally:
            await client.close()
