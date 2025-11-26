"""Test the SatCom Forecast config flow."""

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# Mock FlowResultType since we can't import it
class FlowResultType:
    FORM = "form"
    CREATE_ENTRY = "create_entry"
    ABORT = "abort"


# Define MockConfigFlow class
class MockConfigFlow:
    def __init__(self):
        self.hass = None
        self._credentials = {}
        self._available_folders = []

    def async_show_form(
        self, step_id, data_schema=None, errors=None, description_placeholders=None
    ):
        return {"type": FlowResultType.FORM, "step_id": step_id, "errors": errors or {}}

    def async_create_entry(self, title, data):
        return {"type": FlowResultType.CREATE_ENTRY, "title": title, "data": data}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()


# Setup mocks before importing the module under test
if "homeassistant" not in sys.modules:
    sys.modules["homeassistant"] = MagicMock()

if "homeassistant.config_entries" not in sys.modules:
    sys.modules["homeassistant.config_entries"] = MagicMock()

# Link them
sys.modules["homeassistant"].config_entries = sys.modules[
    "homeassistant.config_entries"
]

sys.modules["homeassistant.config_entries"].ConfigFlow = MockConfigFlow
sys.modules["homeassistant.config_entries"].OptionsFlow = MockConfigFlow
sys.modules["homeassistant.config_entries"].CONN_CLASS_CLOUD_POLL = "cloud_poll"

if "homeassistant.data_entry_flow" not in sys.modules:
    sys.modules["homeassistant.data_entry_flow"] = MagicMock()
    sys.modules["homeassistant.data_entry_flow"].FlowResultType = FlowResultType

# Link data_entry_flow
sys.modules["homeassistant"].data_entry_flow = sys.modules[
    "homeassistant.data_entry_flow"
]

import importlib

import custom_components.satcom_forecast.config_flow

# Now import the module under test
from custom_components.satcom_forecast.const import DOMAIN

importlib.reload(custom_components.satcom_forecast.config_flow)
from custom_components.satcom_forecast.config_flow import (
    SatcomForecastConfigFlow,
    SatcomForecastOptionsFlow,
    get_imap_folders,
    validate_imap_folder,
)


@pytest.fixture
def mock_hass():
    """Mock Home Assistant object."""
    hass = MagicMock()
    hass.config_entries = MagicMock()
    hass.config_entries.flow = MagicMock()
    hass.config_entries.flow.async_init = AsyncMock()
    hass.config_entries.flow.async_configure = AsyncMock()
    hass.async_add_executor_job = AsyncMock()
    hass.config_entries.async_update_entry = MagicMock()
    return hass


@pytest.fixture
def mock_config_entry():
    """Mock ConfigEntry."""
    entry = MagicMock()
    entry.data = {
        "imap_host": "imap.test.com",
        "imap_port": 993,
        "imap_security": "SSL",
        "imap_user": "test@test.com",
        "imap_pass": "password",
        "smtp_host": "smtp.test.com",
        "smtp_port": 587,
        "smtp_user": "test@test.com",
        "smtp_pass": "password",
        "imap_folder": "INBOX",
        "polling_interval": 60,
    }
    entry.entry_id = "test_entry_id"
    return entry


async def test_flow_init(mock_hass):
    """Test flow initialization."""
    flow = SatcomForecastConfigFlow()
    flow.hass = mock_hass

    result = await flow.async_step_user()
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}


async def test_step_user_success(mock_hass):
    """Test user step with valid input."""
    flow = SatcomForecastConfigFlow()
    flow.hass = mock_hass

    user_input = {
        "imap_host": "imap.test.com",
        "imap_port": 993,
        "imap_security": "SSL",
        "imap_user": "test@test.com",
        "imap_pass": "password",
        "smtp_host": "smtp.test.com",
        "smtp_port": 587,
        "smtp_user": "test@test.com",
        "smtp_pass": "password",
    }

    # Mock get_imap_folders to return success
    mock_hass.async_add_executor_job.return_value = (["INBOX", "Sent"], None)

    # Mock async_step_finalize to return a result
    with patch.object(
        flow, "async_step_finalize", new_callable=AsyncMock
    ) as mock_finalize:
        mock_finalize.return_value = {"type": "finalize_called"}

        result = await flow.async_step_user(user_input)

        assert result == {"type": "finalize_called"}
        assert flow._credentials == user_input
        assert flow._available_folders == ["INBOX", "Sent"]


async def test_step_user_connection_error(mock_hass):
    """Test user step with connection error."""
    flow = SatcomForecastConfigFlow()
    flow.hass = mock_hass

    user_input = {
        "imap_host": "imap.test.com",
        "imap_port": 993,
        "imap_security": "SSL",
        "imap_user": "test@test.com",
        "imap_pass": "password",
        "smtp_host": "smtp.test.com",
        "smtp_port": 587,
        "smtp_user": "test@test.com",
        "smtp_pass": "password",
    }

    # Mock get_imap_folders to return error
    mock_hass.async_add_executor_job.return_value = (None, "Connection refused")

    result = await flow.async_step_user(user_input)

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {
        "base": "imap_invalid",
        "imap_host": "Connection refused",
    }


async def test_step_finalize_success(mock_hass):
    """Test finalize step with valid input."""
    flow = SatcomForecastConfigFlow()
    flow.hass = mock_hass
    flow._credentials = {
        "imap_host": "imap.test.com",
        "imap_port": 993,
        "imap_security": "SSL",
        "imap_user": "test@test.com",
        "imap_pass": "password",
    }
    flow._available_folders = ["INBOX"]

    user_input = {
        "imap_folder": "INBOX",
        "forecast_format": "summary",
        "device_type": "zoleo",
        "polling_interval": 60,
        "default_days": 3,
    }

    # Mock validate_imap_folder to return success
    mock_hass.async_add_executor_job.return_value = (True, None)

    # Since we are using MockConfigFlow, async_create_entry is already defined there
    result = await flow.async_step_finalize(user_input)

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "SatCom Forecast"


async def test_step_finalize_invalid_folder(mock_hass):
    """Test finalize step with invalid folder."""
    flow = SatcomForecastConfigFlow()
    flow.hass = mock_hass
    flow._credentials = {
        "imap_host": "imap.test.com",
        "imap_port": 993,
        "imap_security": "SSL",
        "imap_user": "test@test.com",
        "imap_pass": "password",
    }
    flow._available_folders = ["INBOX"]

    user_input = {
        "imap_folder": "Invalid",
        "forecast_format": "summary",
        "device_type": "zoleo",
        "polling_interval": 60,
        "default_days": 3,
    }

    # Mock validate_imap_folder to return error
    mock_hass.async_add_executor_job.return_value = (False, "Folder not found")

    result = await flow.async_step_finalize(user_input)

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {
        "base": "invalid_folder",
        "imap_folder": "Folder not found",
    }


def test_get_imap_folders():
    """Test get_imap_folders function."""
    with patch("imaplib.IMAP4_SSL") as mock_imap:
        mock_instance = mock_imap.return_value
        mock_instance.list.return_value = (
            "OK",
            [b'(\\HasNoChildren) "/" "INBOX"', b'(\\HasNoChildren) "/" "Sent"'],
        )

        folders, error = get_imap_folders("host", 993, "user", "pass", "SSL")
        assert folders == ["INBOX", "Sent"]
        assert error is None

        mock_instance.list.return_value = ("NO", [])
        folders, error = get_imap_folders("host", 993, "user", "pass", "SSL")
        assert folders is None
        assert error == "Could not list folders"


def test_validate_imap_folder():
    """Test validate_imap_folder function."""
    with patch("imaplib.IMAP4_SSL") as mock_imap:
        mock_instance = mock_imap.return_value
        mock_instance.select.return_value = ("OK", [b"1"])

        valid, error = validate_imap_folder("host", 993, "user", "pass", "INBOX", "SSL")
        assert valid is True
        assert error is None

        mock_instance.select.return_value = ("NO", [b"Folder not found"])
        valid, error = validate_imap_folder(
            "host", 993, "user", "pass", "Invalid", "SSL"
        )
        assert valid is False
        assert "Folder not found" in error


async def test_options_flow_init(mock_hass, mock_config_entry):
    """Test options flow initialization."""
    flow = SatcomForecastOptionsFlow()
    flow.hass = mock_hass
    flow.config_entry = mock_config_entry

    result = await flow.async_step_init()
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"


async def test_options_flow_update(mock_hass, mock_config_entry):
    """Test options flow update."""
    flow = SatcomForecastOptionsFlow()
    flow.hass = mock_hass
    flow.config_entry = mock_config_entry

    user_input = {
        "polling_interval": 30,
        "imap_folder": "INBOX",
    }

    # Mock validate_imap_folder (since folder didn't change, it shouldn't be called, but just in case)
    mock_hass.async_add_executor_job.return_value = (True, None)

    # Since we are using MockConfigFlow, async_create_entry is already defined there
    # But we need to mock async_reload_entry import inside the method
    # The method does: from . import async_reload_entry
    # We can mock sys.modules['custom_components.satcom_forecast'] to have async_reload_entry

    async def mock_reload(*args, **kwargs):
        pass

    with patch(
        "custom_components.satcom_forecast.async_reload_entry", side_effect=mock_reload
    ) as mock_reload_mock:
        result = await flow.async_step_init(user_input)

        assert result["type"] == FlowResultType.CREATE_ENTRY
        # Verify update was called
        mock_hass.config_entries.async_update_entry.assert_called()
        mock_reload_mock.assert_called_once()
