import imaplib
import voluptuous as vol
from homeassistant import config_entries, core
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from .const import DOMAIN, DEFAULT_DEBUG, DEFAULT_POLLING_INTERVAL
import logging

_LOGGER = logging.getLogger(__name__)

def validate_imap_folder(host, port, username, password, folder):
    """Validate that the specified IMAP folder exists."""
    try:
        mail = imaplib.IMAP4_SSL(host, port)
        mail.login(username, password)
        
        # List available folders
        status, folders = mail.list()
        if status != "OK":
            mail.logout()
            return False, "Could not list folders"
        
        # Extract folder names from the list
        available_folders = []
        for f in folders:
            # Parse folder name from IMAP LIST response
            folder_name = f.decode().split('"')[-2] if b'"' in f else f.decode().split()[-1]
            available_folders.append(folder_name)
        
        # Check if the requested folder exists
        if folder not in available_folders:
            mail.logout()
            return False, f"Folder '{folder}' not found. Available folders: {', '.join(available_folders)}"
        
        # Try to select the folder to ensure it's accessible
        status, data = mail.select(folder)
        if status != "OK":
            mail.logout()
            return False, f"Could not access folder '{folder}': {data[0].decode() if data else 'Unknown error'}"
        
        mail.logout()
        return True, None
        
    except Exception as e:
        return False, f"IMAP connection error: {str(e)}"

class SatcomForecastConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 3
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        self._credentials = {}

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input:
            try:
                mail = imaplib.IMAP4_SSL(user_input["imap_host"], user_input["imap_port"])
                mail.login(user_input["imap_user"], user_input["imap_pass"])
                mail.logout()
                self._credentials = user_input
                return await self.async_step_finalize()
            except Exception:
                errors["base"] = "imap_invalid"

        fields = vol.Schema({
            vol.Required("imap_host", default="imap.gmail.com"): str,
            vol.Required("imap_port", default=993): int,
            vol.Required("imap_user"): str,
            vol.Required("imap_pass"): str,
            vol.Required("smtp_host", default="smtp.gmail.com"): str,
            vol.Required("smtp_port", default=587): int,
            vol.Required("smtp_user"): str,
            vol.Required("smtp_pass"): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=fields,
            errors=errors
        )

    async def async_step_finalize(self, user_input=None):
        errors = {}
        
        if user_input:
            # Validate the IMAP folder
            is_valid, error_message = await self.hass.async_add_executor_job(
                validate_imap_folder,
                self._credentials["imap_host"],
                self._credentials["imap_port"],
                self._credentials["imap_user"],
                self._credentials["imap_pass"],
                user_input["imap_folder"]
            )
            
            if not is_valid:
                errors["base"] = "invalid_folder"
                errors["imap_folder"] = error_message
            else:
                return self.async_create_entry(
                    title="SatCom Forecast",
                    data={**self._credentials, **user_input}
                )

        fields = vol.Schema({
            vol.Required("imap_folder", default="INBOX"): str,
            vol.Required("forecast_format", default="summary"): vol.In(["summary", "compact", "full"]),
            vol.Required("device_type", default="zoleo"): vol.In(["zoleo", "inreach"]),
            vol.Optional("character_limit", default=0): int,
            vol.Optional("debug", default=DEFAULT_DEBUG): bool,
            vol.Required("polling_interval", default=DEFAULT_POLLING_INTERVAL): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=1440)
            ),
        })

        return self.async_show_form(
            step_id="finalize",
            data_schema=fields,
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return SatcomForecastOptionsFlow(config_entry)


class SatcomForecastOptionsFlow(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Manage the options."""
        errors = {}
        
        if user_input:
            try:
                # Test IMAP connection if credentials were provided
                if user_input.get("imap_pass") and user_input.get("imap_user"):
                    mail = imaplib.IMAP4_SSL(user_input["imap_host"], user_input["imap_port"])
                    mail.login(user_input["imap_user"], user_input["imap_pass"])
                    mail.logout()
                
                # Validate IMAP folder if it was changed
                current_folder = self.config_entry.data.get("imap_folder", "INBOX")
                new_folder = user_input.get("imap_folder", current_folder)
                
                if new_folder != current_folder:
                    # Get the credentials to use for validation
                    imap_user = user_input.get("imap_user") or self.config_entry.data.get("imap_user")
                    imap_pass = user_input.get("imap_pass") or self.config_entry.data.get("imap_pass")
                    imap_host = user_input.get("imap_host") or self.config_entry.data.get("imap_host")
                    imap_port = user_input.get("imap_port") or self.config_entry.data.get("imap_port")
                    
                    is_valid, error_message = await self.hass.async_add_executor_job(
                        validate_imap_folder,
                        imap_host,
                        imap_port,
                        imap_user,
                        imap_pass,
                        new_folder
                    )
                    
                    if not is_valid:
                        errors["base"] = "invalid_folder"
                        errors["imap_folder"] = error_message
                        return self.async_show_form(
                            step_id="init",
                            data_schema=self._get_schema(user_input),
                            errors=errors
                        )
                
                # Update the config entry with new data, preserving existing passwords if not changed
                data = {**self.config_entry.data}
                for key, value in user_input.items():
                    if value:  # Only update if a value was provided
                        data[key] = value
                
                # Check if polling interval changed
                old_polling = self.config_entry.data.get("polling_interval", DEFAULT_POLLING_INTERVAL)
                new_polling = data.get("polling_interval", DEFAULT_POLLING_INTERVAL)
                polling_changed = old_polling != new_polling
                
                self.hass.config_entries.async_update_entry(self.config_entry, data=data)
                
                # Reload the integration if polling interval changed
                if polling_changed:
                    from . import async_reload_entry
                    await async_reload_entry(self.hass, self.config_entry)
                    _LOGGER.info("Integration reloaded due to polling interval change from %d to %d minutes", old_polling, new_polling)
                
                return self.async_create_entry(title="", data={})
                
            except Exception:
                errors["base"] = "imap_invalid"

        return self.async_show_form(
            step_id="init",
            data_schema=self._get_schema(),
            errors=errors
        )
    
    def _get_schema(self, user_input=None):
        """Get the schema for the options form."""
        # Get current values
        current_data = self.config_entry.data
        
        # Use user_input values if provided, otherwise use current values
        data = {**current_data}
        if user_input:
            data.update(user_input)
        
        # Create schema with current values as defaults
        return vol.Schema({
            vol.Required("imap_host", default=data.get("imap_host", "imap.gmail.com")): str,
            vol.Required("imap_port", default=data.get("imap_port", 993)): int,
            vol.Required("imap_user", default=data.get("imap_user", "")): str,
            vol.Optional("imap_pass"): str,
            vol.Required("smtp_host", default=data.get("smtp_host", "smtp.gmail.com")): str,
            vol.Required("smtp_port", default=data.get("smtp_port", 587)): int,
            vol.Required("smtp_user", default=data.get("smtp_user", "")): str,
            vol.Optional("smtp_pass"): str,
            vol.Required("imap_folder", default=data.get("imap_folder", "INBOX")): str,
            vol.Required("forecast_format", default=data.get("forecast_format", "summary")): vol.In(["summary", "compact", "full"]),
            vol.Required("device_type", default=data.get("device_type", "zoleo")): vol.In(["zoleo", "inreach"]),
            vol.Optional("character_limit", default=data.get("character_limit", 0)): int,
            vol.Optional("debug", default=data.get("debug", DEFAULT_DEBUG)): bool,
            vol.Required("polling_interval", default=data.get("polling_interval", DEFAULT_POLLING_INTERVAL)): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=1440)
            ),
        })
