import imaplib
import voluptuous as vol
from homeassistant import config_entries, core
from .const import DOMAIN, DEFAULT_DEBUG

class SatcomForecastConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2
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
        if user_input:
            return self.async_create_entry(
                title="SatCom Forecast",
                data={**self._credentials, **user_input}
            )

        fields = vol.Schema({
            vol.Required("imap_folder", default="Forecasts"): str,
            vol.Required("forecast_format", default="summary"): vol.In(["summary", "compact", "full"]),
            vol.Required("device_type", default="zoleo"): vol.In(["zoleo", "inreach"]),
            vol.Optional("character_limit", default=0): int,
            vol.Optional("debug", default=DEFAULT_DEBUG): bool,
        })

        return self.async_show_form(
            step_id="finalize",
            data_schema=fields,
            errors={}
        )
