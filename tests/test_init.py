"""Test the SatCom Forecast init."""
import sys
import asyncio
from unittest.mock import MagicMock, patch

import pytest

# Setup mocks before importing the module under test
if 'homeassistant' not in sys.modules:
    sys.modules['homeassistant'] = MagicMock()

if 'homeassistant.config_entries' not in sys.modules:
    sys.modules['homeassistant.config_entries'] = MagicMock()

if 'homeassistant.core' not in sys.modules:
    sys.modules['homeassistant.core'] = MagicMock()

if 'homeassistant.helpers' not in sys.modules:
    sys.modules['homeassistant.helpers'] = MagicMock()

if 'homeassistant.helpers.config_validation' not in sys.modules:
    sys.modules['homeassistant.helpers.config_validation'] = MagicMock()

# Link mocked modules
sys.modules['homeassistant'].config_entries = sys.modules['homeassistant.config_entries']
sys.modules['homeassistant'].core = sys.modules['homeassistant.core']
sys.modules['homeassistant'].helpers = sys.modules['homeassistant.helpers']
sys.modules['homeassistant'].helpers.config_validation = sys.modules['homeassistant.helpers.config_validation']

# Mock ConfigEntry
class MockConfigEntry:
    def __init__(self, version=1, data=None, entry_id="test_entry"):
        self.version = version
        self.data = data or {}
        self.entry_id = entry_id

sys.modules['homeassistant.config_entries'].ConfigEntry = MockConfigEntry

# Import module under test
import custom_components.satcom_forecast
import importlib
importlib.reload(custom_components.satcom_forecast)
from custom_components.satcom_forecast import (
    async_setup,
    async_setup_entry,
    async_unload_entry,
    async_migrate_entry,
    async_reload_entry,
    DOMAIN,
)

@pytest.fixture
def mock_hass():
    """Mock Home Assistant object."""
    hass = MagicMock()
    hass.data = {}
    hass.config_entries = MagicMock()
    
    def return_future(*args, **kwargs):
        f = asyncio.Future()
        f.set_result(True)
        return f
    hass.config_entries.async_forward_entry_setups = MagicMock(side_effect=return_future)
    
    hass.config_entries.async_update_entry = MagicMock()
    hass.services = MagicMock()
    hass.services.async_register = MagicMock()
    hass.services.async_remove = MagicMock()
    return hass

@pytest.fixture
def mock_coordinator():
    """Mock coordinator."""
    coordinator = MagicMock()
    
    def return_future(*args, **kwargs):
        f = asyncio.Future()
        f.set_result(True)
        return f
    coordinator.async_config_entry_first_refresh = MagicMock(side_effect=return_future)
    
    return coordinator

async def test_async_setup(mock_hass):
    """Test async_setup."""
    assert await async_setup(mock_hass, {}) is True

async def test_async_setup_entry(mock_hass, mock_coordinator):
    """Test async_setup_entry."""
    entry = MockConfigEntry(data={"debug": True})
    
    with patch("custom_components.satcom_forecast.SatcomForecastCoordinator", return_value=mock_coordinator) as mock_coord_cls:
        result = await async_setup_entry(mock_hass, entry)
        
        assert result is True
        mock_coord_cls.assert_called_once_with(mock_hass, entry.data)
        mock_coordinator.async_config_entry_first_refresh.assert_called_once()
        mock_hass.config_entries.async_forward_entry_setups.assert_called_once_with(entry, ["sensor"])
        mock_hass.services.async_register.assert_called_once()
        
        # Verify coordinator is stored in hass.data
        assert mock_hass.data[DOMAIN][entry.entry_id] == mock_coordinator

async def test_async_unload_entry(mock_hass):
    """Test async_unload_entry."""
    entry = MockConfigEntry()
    
    result = await async_unload_entry(mock_hass, entry)
    
    assert result is True
    mock_hass.services.async_remove.assert_called_once_with(DOMAIN, "set_debug_logging")

async def test_async_migrate_entry_v2_to_v3(mock_hass):
    """Test migration from v2 to v3."""
    entry = MockConfigEntry(version=2, data={})
    
    result = await async_migrate_entry(mock_hass, entry)
    
    assert result is True
    mock_hass.config_entries.async_update_entry.assert_called_once()
    call_args = mock_hass.config_entries.async_update_entry.call_args
    assert call_args[1]["version"] == 3
    assert call_args[1]["data"]["polling_interval"] == 5

async def test_async_migrate_entry_v3_to_v4(mock_hass):
    """Test migration from v3 to v4."""
    entry = MockConfigEntry(version=3, data={"polling_interval": 10})
    
    result = await async_migrate_entry(mock_hass, entry)
    
    assert result is True
    mock_hass.config_entries.async_update_entry.assert_called_once()
    call_args = mock_hass.config_entries.async_update_entry.call_args
    assert call_args[1]["version"] == 4
    assert call_args[1]["data"]["imap_security"] == "SSL"

async def test_async_reload_entry(mock_hass):
    """Test async_reload_entry."""
    entry = MockConfigEntry()
    
    def return_future(*args, **kwargs):
        f = asyncio.Future()
        f.set_result(True)
        return f
        
    with patch("custom_components.satcom_forecast.async_unload_entry", side_effect=return_future) as mock_unload, \
         patch("custom_components.satcom_forecast.async_setup_entry", side_effect=return_future) as mock_setup:
        
        await async_reload_entry(mock_hass, entry)
        
        mock_unload.assert_called_once_with(mock_hass, entry)
        mock_setup.assert_called_once_with(mock_hass, entry)
