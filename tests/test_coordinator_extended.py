"""Extended tests for coordinator functionality."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "custom_components"))

# Import as package to support relative imports
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from custom_components.satcom_forecast.coordinator import SatcomForecastCoordinator
except ImportError as e:
    pytest.fail(f"Could not import coordinator: {e}")


class TestCoordinatorExtended:
    """Extended tests for coordinator."""

    @pytest.fixture
    def mock_hass(self):
        """Mock Home Assistant object."""
        hass = MagicMock()
        return hass

    @pytest.fixture
    def config(self):
        """Test configuration."""
        return {
            "imap_host": "imap.test.com",
            "imap_port": 993,
            "imap_user": "user",
            "imap_pass": "pass",
            "smtp_host": "smtp.test.com",
            "smtp_port": 587,
            "smtp_user": "user",
            "smtp_pass": "pass",
            "polling_interval": 5,
            "default_days": 3,
            "device_type": "zoleo",
        }

    @patch("custom_components.satcom_forecast.coordinator.check_imap_for_gps")
    @patch("custom_components.satcom_forecast.coordinator.fetch_forecast")
    @patch("custom_components.satcom_forecast.coordinator.send_forecast_email")
    @patch("custom_components.satcom_forecast.coordinator.format_forecast")
    @patch("custom_components.satcom_forecast.coordinator.split_message")
    async def test_update_success(
        self,
        mock_split,
        mock_format,
        mock_send,
        mock_fetch,
        mock_check_imap,
        mock_hass,
        config,
    ):
        """Test successful update cycle."""
        coordinator = SatcomForecastCoordinator(mock_hass, config)

        # Setup mocks
        mock_check_imap.return_value = [
            {
                "lat": "34.5",
                "lon": "-118.2",
                "sender": "test@example.com",
                "format": "compact",
                "days": None,
            }
        ]
        mock_fetch.return_value = "Forecast text"
        mock_format.return_value = "Formatted forecast"
        mock_split.return_value = ["Part 1", "Part 2"]
        mock_send.return_value = True

        # Run update
        await coordinator._async_update_data()

        # Verify calls
        mock_check_imap.assert_called_once()
        mock_fetch.assert_called_with("34.5", "-118.2", 3)
        mock_format.assert_called_with("Forecast text", "compact", 3)
        mock_split.assert_called()
        assert mock_send.call_count == 2

        # Verify data update
        assert coordinator.data["gps_received_count"] == 1
        assert coordinator.data["last_sender"] == "test@example.com"
        assert coordinator.data["last_forecast"] == "Formatted forecast"

    @patch("custom_components.satcom_forecast.coordinator.check_imap_for_gps")
    async def test_update_no_messages(self, mock_check_imap, mock_hass, config):
        """Test update with no messages."""
        coordinator = SatcomForecastCoordinator(mock_hass, config)
        mock_check_imap.return_value = []

        await coordinator._async_update_data()

        assert coordinator.data["gps_received_count"] == 0

    @patch("custom_components.satcom_forecast.coordinator.check_imap_for_gps")
    @patch("custom_components.satcom_forecast.coordinator.fetch_forecast")
    async def test_update_fetch_fail(
        self, mock_fetch, mock_check_imap, mock_hass, config
    ):
        """Test update where forecast fetch fails."""
        coordinator = SatcomForecastCoordinator(mock_hass, config)

        mock_check_imap.return_value = [
            {"lat": "34.5", "lon": "-118.2", "sender": "test@example.com"}
        ]
        mock_fetch.return_value = "NWS error: Failed"

        await coordinator._async_update_data()

        # Should not update last_forecast
        assert coordinator.data["last_forecast"] is None

    @patch("custom_components.satcom_forecast.coordinator.check_imap_for_gps")
    @patch("custom_components.satcom_forecast.coordinator.fetch_forecast")
    @patch("custom_components.satcom_forecast.coordinator.send_forecast_email")
    @patch("custom_components.satcom_forecast.coordinator.format_forecast")
    @patch("custom_components.satcom_forecast.coordinator.split_message")
    async def test_update_send_fail(
        self,
        mock_split,
        mock_format,
        mock_send,
        mock_fetch,
        mock_check_imap,
        mock_hass,
        config,
    ):
        """Test update where sending email fails."""
        coordinator = SatcomForecastCoordinator(mock_hass, config)

        mock_check_imap.return_value = [
            {"lat": "34.5", "lon": "-118.2", "sender": "test@example.com"}
        ]
        mock_fetch.return_value = "Forecast"
        mock_format.return_value = "Formatted"
        mock_split.return_value = ["Part 1"]
        mock_send.return_value = False

        await coordinator._async_update_data()

        # Should not update last_forecast if send failed
        assert coordinator.data["last_forecast"] is None

    @patch("custom_components.satcom_forecast.coordinator.check_imap_for_gps")
    @patch("custom_components.satcom_forecast.coordinator.fetch_forecast")
    @patch("custom_components.satcom_forecast.coordinator.send_forecast_email")
    @patch("custom_components.satcom_forecast.coordinator.format_forecast")
    @patch("custom_components.satcom_forecast.coordinator.split_message")
    async def test_days_override(
        self,
        mock_split,
        mock_format,
        mock_send,
        mock_fetch,
        mock_check_imap,
        mock_hass,
        config,
    ):
        """Test days override logic."""
        coordinator = SatcomForecastCoordinator(mock_hass, config)

        mock_check_imap.return_value = [
            {
                "lat": "34.5",
                "lon": "-118.2",
                "sender": "test@example.com",
                "days": 5,
            }
        ]
        mock_fetch.return_value = "Forecast"
        mock_format.return_value = "Formatted"
        mock_split.return_value = ["Part 1"]
        mock_send.return_value = True

        await coordinator._async_update_data()

        mock_fetch.assert_called_with("34.5", "-118.2", 5)
        mock_format.assert_called_with(
            "Forecast", "summary", 5
        )  # Default format is summary

    @patch("custom_components.satcom_forecast.coordinator.check_imap_for_gps")
    @patch("custom_components.satcom_forecast.coordinator.fetch_forecast")
    @patch("custom_components.satcom_forecast.coordinator.send_forecast_email")
    @patch("custom_components.satcom_forecast.coordinator.format_forecast")
    @patch("custom_components.satcom_forecast.coordinator.split_message")
    async def test_character_limit_config(
        self,
        mock_split,
        mock_format,
        mock_send,
        mock_fetch,
        mock_check_imap,
        mock_hass,
        config,
    ):
        """Test character limit configuration."""
        config["character_limit"] = "100"
        coordinator = SatcomForecastCoordinator(mock_hass, config)

        mock_check_imap.return_value = [
            {"lat": "34.5", "lon": "-118.2", "sender": "test@example.com"}
        ]
        mock_fetch.return_value = "Forecast"
        mock_format.return_value = "Formatted"
        mock_split.return_value = ["Part 1"]
        mock_send.return_value = True

        await coordinator._async_update_data()

        mock_split.assert_called_with(
            "Formatted", device_type="zoleo", custom_limit=100
        )

    @patch("custom_components.satcom_forecast.coordinator.check_imap_for_gps")
    @patch("custom_components.satcom_forecast.coordinator.fetch_forecast")
    @patch("custom_components.satcom_forecast.coordinator.send_forecast_email")
    @patch("custom_components.satcom_forecast.coordinator.format_forecast")
    @patch("custom_components.satcom_forecast.coordinator.split_message")
    async def test_character_limit_invalid(
        self,
        mock_split,
        mock_format,
        mock_send,
        mock_fetch,
        mock_check_imap,
        mock_hass,
        config,
    ):
        """Test invalid character limit configuration."""
        config["character_limit"] = "invalid"
        coordinator = SatcomForecastCoordinator(mock_hass, config)

        mock_check_imap.return_value = [
            {"lat": "34.5", "lon": "-118.2", "sender": "test@example.com"}
        ]
        mock_fetch.return_value = "Forecast"
        mock_format.return_value = "Formatted"
        mock_split.return_value = ["Part 1"]
        mock_send.return_value = True

        await coordinator._async_update_data()

        mock_split.assert_called_with(
            "Formatted", device_type="zoleo", custom_limit=None
        )
