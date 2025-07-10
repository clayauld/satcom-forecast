import imaplib
import logging
from typing import Any, Dict, Optional, Tuple

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DEFAULT_DAYS, DEFAULT_DEBUG, DEFAULT_POLLING_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


def get_imap_folders(
    host: str, port: int, username: str, password: str, security: str = "SSL"
) -> Tuple[Optional[list], Optional[str]]:
    """Get list of available IMAP folders."""
    try:
        if security == "SSL":
            mail = imaplib.IMAP4_SSL(host, port)
        elif security == "STARTTLS":
            mail = imaplib.IMAP4(host, port)
            mail.starttls()
        else:  # None
            mail = imaplib.IMAP4(host, port)

        mail.login(username, password)

        # List available folders
        status, folders = mail.list()
        if status != "OK":
            mail.logout()
            return None, "Could not list folders"

        # Extract folder names from the list
        available_folders = []
        for f in folders:
            # Parse folder name from IMAP LIST response
            if b'"' in f:
                folder_name = f.decode().split('"')[-2]
            else:
                folder_name = f.decode().split()[-1]
            available_folders.append(folder_name)

        mail.logout()
        return available_folders, None

    except Exception as e:
        return None, f"IMAP connection error: {str(e)}"


def validate_imap_folder(
    host: str,
    port: int,
    username: str,
    password: str,
    folder: str,
    security: str = "SSL",
) -> Tuple[bool, Optional[str]]:
    """Validate that the specified IMAP folder exists and is accessible."""
    try:
        if security == "SSL":
            mail = imaplib.IMAP4_SSL(host, port)
        elif security == "STARTTLS":
            mail = imaplib.IMAP4(host, port)
            mail.starttls()
        else:  # None
            mail = imaplib.IMAP4(host, port)

        mail.login(username, password)

        # Try to select the folder to ensure it's accessible
        status, data = mail.select(folder)
        if status != "OK":
            mail.logout()
            error_msg = (
                f"Could not access folder '{folder}': "
                f"{data[0].decode() if data and data[0] else 'Unknown error'}"
            )
            return False, error_msg

        mail.logout()
        return True, None

    except Exception as e:
        return False, f"IMAP connection error: {str(e)}"


class SatcomForecastConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore
    VERSION = 4
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self) -> None:
        self._credentials: Dict[str, Any] = {}
        self._available_folders: list = []

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        errors = {}
        if user_input:
            try:
                # Test IMAP connection and get available folders
                folders, error = await self.hass.async_add_executor_job(
                    get_imap_folders,
                    user_input["imap_host"],
                    user_input["imap_port"],
                    user_input["imap_user"],
                    user_input["imap_pass"],
                    user_input["imap_security"],
                )

                if folders:
                    self._credentials = user_input
                    self._available_folders = folders
                    return await self.async_step_finalize()
                else:
                    errors["base"] = "imap_invalid"
                    if error:
                        errors["imap_host"] = error

            except Exception as e:
                errors["base"] = "imap_invalid"
                errors["imap_host"] = str(e)

        fields = vol.Schema(
            {
                vol.Required("imap_host", default="imap.gmail.com"): str,
                vol.Required("imap_port", default=993): int,
                vol.Required("imap_security", default="SSL"): vol.In(
                    ["None", "STARTTLS", "SSL"]
                ),
                vol.Required("imap_user"): str,
                vol.Required("imap_pass"): str,
                vol.Required("smtp_host", default="smtp.gmail.com"): str,
                vol.Required("smtp_port", default=587): int,
                vol.Required("smtp_user"): str,
                vol.Required("smtp_pass"): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=fields, errors=errors)

    async def async_step_finalize(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        errors = {}

        if user_input:
            # Validate the selected IMAP folder
            is_valid, error_message = await self.hass.async_add_executor_job(
                validate_imap_folder,
                self._credentials["imap_host"],
                self._credentials["imap_port"],
                self._credentials["imap_user"],
                self._credentials["imap_pass"],
                user_input["imap_folder"],
                self._credentials["imap_security"],
            )

            if not is_valid:
                errors["base"] = "invalid_folder"
                errors["imap_folder"] = error_message
            else:
                return self.async_create_entry(
                    title="SatCom Forecast", data={**self._credentials, **user_input}
                )

        # Create folder selection options
        folder_options = {folder: folder for folder in self._available_folders}

        fields = vol.Schema(
            {
                vol.Required("imap_folder", default="INBOX"): vol.In(folder_options),
                vol.Required("forecast_format", default="summary"): vol.In(
                    ["summary", "compact", "full"]
                ),
                vol.Required("device_type", default="zoleo"): vol.In(
                    ["zoleo", "inreach"]
                ),
                vol.Optional("character_limit", default=0): int,
                vol.Optional("debug", default=DEFAULT_DEBUG): bool,
                vol.Required(
                    "polling_interval", default=DEFAULT_POLLING_INTERVAL
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
                vol.Required("default_days", default=DEFAULT_DAYS): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=7)
                ),
            }
        )

        return self.async_show_form(
            step_id="finalize",
            data_schema=fields,
            errors=errors,
            description_placeholders={
                "available_folders": ", ".join(self._available_folders)
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return SatcomForecastOptionsFlow()


class SatcomForecastOptionsFlow(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self) -> None:
        """Initialize options flow."""
        self._available_folders: list = []

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Manage the options."""
        errors = {}

        if user_input:
            try:
                # Test IMAP connection if credentials were provided
                if user_input.get("imap_pass") and user_input.get("imap_user"):
                    # Get the credentials to use for validation
                    imap_user = user_input.get(
                        "imap_user"
                    ) or self.config_entry.data.get("imap_user")
                    imap_pass = user_input.get(
                        "imap_pass"
                    ) or self.config_entry.data.get("imap_pass")
                    imap_host = user_input.get(
                        "imap_host"
                    ) or self.config_entry.data.get("imap_host")
                    imap_port = user_input.get(
                        "imap_port"
                    ) or self.config_entry.data.get("imap_port")
                    imap_security = user_input.get(
                        "imap_security"
                    ) or self.config_entry.data.get("imap_security", "SSL")

                    if imap_security == "SSL":
                        mail = imaplib.IMAP4_SSL(imap_host, imap_port)
                    elif imap_security == "STARTTLS":
                        mail = imaplib.IMAP4(imap_host, imap_port)
                        mail.starttls()
                    else:  # None
                        mail = imaplib.IMAP4(imap_host, imap_port)

                    mail.login(imap_user, imap_pass)
                    mail.logout()

                # Validate IMAP folder if it was changed
                current_folder = self.config_entry.data.get("imap_folder", "INBOX")
                new_folder = user_input.get("imap_folder", current_folder)

                if new_folder != current_folder:
                    # Get the credentials to use for validation
                    imap_user = user_input.get(
                        "imap_user"
                    ) or self.config_entry.data.get("imap_user")
                    imap_pass = user_input.get(
                        "imap_pass"
                    ) or self.config_entry.data.get("imap_pass")
                    imap_host = user_input.get(
                        "imap_host"
                    ) or self.config_entry.data.get("imap_host")
                    imap_port = user_input.get(
                        "imap_port"
                    ) or self.config_entry.data.get("imap_port")
                    imap_security = user_input.get(
                        "imap_security"
                    ) or self.config_entry.data.get("imap_security", "SSL")

                    is_valid, error_message = await self.hass.async_add_executor_job(
                        validate_imap_folder,
                        imap_host,
                        imap_port,
                        imap_user,
                        imap_pass,
                        new_folder,
                        imap_security,
                    )

                    if not is_valid:
                        errors["base"] = "invalid_folder"
                        errors["imap_folder"] = error_message
                        return self.async_show_form(
                            step_id="init",
                            data_schema=self._get_schema(user_input),
                            errors=errors,
                        )

                # Update the config entry with new data, preserving existing
                # passwords if not changed
                data = {**self.config_entry.data}
                for key, value in user_input.items():
                    if value:  # Only update if a value was provided
                        data[key] = value

                # Check if polling interval changed
                old_polling = self.config_entry.data.get(
                    "polling_interval", DEFAULT_POLLING_INTERVAL
                )
                new_polling = data.get("polling_interval", DEFAULT_POLLING_INTERVAL)
                polling_changed = old_polling != new_polling

                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=data
                )

                # Reload the integration if polling interval changed
                if polling_changed:
                    from . import async_reload_entry

                    await async_reload_entry(self.hass, self.config_entry)
                    _LOGGER.info(
                        "Integration reloaded due to polling interval change "
                        "from %d to %d minutes",
                        old_polling,
                        new_polling,
                    )

                return self.async_create_entry(title="", data={})

            except Exception:
                errors["base"] = "imap_invalid"

        return self.async_show_form(
            step_id="init", data_schema=self._get_schema(), errors=errors
        )

    def _get_schema(self, user_input: Optional[Dict[str, Any]] = None) -> vol.Schema:
        """Get the schema for the options form."""
        # Get current values
        current_data = self.config_entry.data

        # Use user_input values if provided, otherwise use current values
        data = {**current_data}
        if user_input:
            data.update(user_input)

        # Create schema with current values as defaults
        return vol.Schema(
            {
                vol.Required(
                    "imap_host", default=data.get("imap_host", "imap.gmail.com")
                ): str,
                vol.Required("imap_port", default=data.get("imap_port", 993)): int,
                vol.Required(
                    "imap_security", default=data.get("imap_security", "SSL")
                ): vol.In(["None", "STARTTLS", "SSL"]),
                vol.Required("imap_user", default=data.get("imap_user", "")): str,
                vol.Optional("imap_pass"): str,
                vol.Required(
                    "smtp_host", default=data.get("smtp_host", "smtp.gmail.com")
                ): str,
                vol.Required("smtp_port", default=data.get("smtp_port", 587)): int,
                vol.Required("smtp_user", default=data.get("smtp_user", "")): str,
                vol.Optional("smtp_pass"): str,
                vol.Required(
                    "imap_folder", default=data.get("imap_folder", "INBOX")
                ): str,
                vol.Required(
                    "forecast_format", default=data.get("forecast_format", "summary")
                ): vol.In(["summary", "compact", "full"]),
                vol.Required(
                    "device_type", default=data.get("device_type", "zoleo")
                ): vol.In(["zoleo", "inreach"]),
                vol.Optional(
                    "character_limit", default=data.get("character_limit", 0)
                ): int,
                vol.Optional("debug", default=data.get("debug", DEFAULT_DEBUG)): bool,
                vol.Required(
                    "polling_interval",
                    default=data.get("polling_interval", DEFAULT_POLLING_INTERVAL),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
                vol.Required(
                    "default_days", default=data.get("default_days", DEFAULT_DAYS)
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=7)),
            }
        )
