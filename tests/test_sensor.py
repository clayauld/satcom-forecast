"""Tests for sensor functionality."""

import os
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "custom_components"))

# Mock Home Assistant modules
sys.modules["homeassistant"] = MagicMock()
sys.modules["homeassistant.config_entries"] = MagicMock()
sys.modules["homeassistant.core"] = MagicMock()
sys.modules["homeassistant.helpers"] = MagicMock()
sys.modules["homeassistant.helpers.entity_platform"] = MagicMock()
sys.modules["homeassistant.helpers.update_coordinator"] = MagicMock()


# Define CoordinatorEntity stub
class MockCoordinatorEntity:
    def __init__(self, coordinator):
        self.coordinator = coordinator


sys.modules["homeassistant.helpers.update_coordinator"].CoordinatorEntity = (
    MockCoordinatorEntity
)

# Import sensor module
try:
    sys.path.insert(
        0,
        os.path.join(
            os.path.dirname(__file__), "..", "custom_components", "satcom_forecast"
        ),
    )
    # We need to import as package or handle relative imports
    # sensor.py imports .const
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from custom_components.satcom_forecast.sensor import SatcomSensor, async_setup_entry
except ImportError as e:
    pytest.fail(f"Could not import sensor: {e}")


class TestSensor:
    """Tests for sensor."""

    async def test_async_setup_entry(self):
        """Test async_setup_entry."""
        hass = MagicMock()
        entry = MagicMock()
        entry.entry_id = "test_entry"
        async_add_entities = MagicMock()

        # Mock coordinator in hass.data
        coordinator = MagicMock()
        hass.data = {"satcom_forecast": {"test_entry": coordinator}}

        await async_setup_entry(hass, entry, async_add_entities)

        async_add_entities.assert_called_once()
        args = async_add_entities.call_args[0][0]
        assert len(args) == 3
        assert isinstance(args[0], SatcomSensor)

    def test_sensor_state(self):
        """Test sensor state property."""
        coordinator = MagicMock()
        coordinator.data = {
            "last_forecast_time": "2023-01-01",
            "last_sender": "user@example.com",
            "gps_received_count": 5,
        }

        sensor = SatcomSensor(
            coordinator, "last_forecast_time", "Last Forecast Time", "timestamp"
        )
        assert sensor.state == "2023-01-01"
        assert sensor._attr_name == "SatCom Last Forecast Time"
        assert sensor._attr_unique_id == "satcom_last_forecast_time"
        assert sensor._attr_device_class == "timestamp"

        sensor2 = SatcomSensor(
            coordinator, "gps_received_count", "GPS Received Count", "count"
        )
        assert sensor2.state == 5
