import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers import config_validation as cv
import voluptuous as vol
from .const import DOMAIN, DEFAULT_DEBUG
from .coordinator import SatcomForecastCoordinator

_LOGGER = logging.getLogger(__name__)

# Config schema for the integration - since this uses config entries, we use config_entry_only_config_schema
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    # Set up debug logging if enabled
    debug_enabled = entry.data.get("debug", DEFAULT_DEBUG)
    if debug_enabled:
        logging.getLogger("custom_components.satcom_forecast").setLevel(logging.DEBUG)
        _LOGGER.debug("Debug logging enabled for SatCom Forecast integration")
    
    coordinator = SatcomForecastCoordinator(hass, entry.data)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    
    # Register service
    async def set_debug_logging(call: ServiceCall):
        """Enable or disable debug logging."""
        enabled = call.data.get("enabled", False)
        logger = logging.getLogger("custom_components.satcom_forecast")
        
        if enabled:
            logger.setLevel(logging.DEBUG)
            _LOGGER.info("Debug logging enabled for SatCom Forecast integration")
        else:
            logger.setLevel(logging.INFO)
            _LOGGER.info("Debug logging disabled for SatCom Forecast integration")
    
    hass.services.async_register(DOMAIN, "set_debug_logging", set_debug_logging)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    # Unregister service
    hass.services.async_remove(DOMAIN, "set_debug_logging")
    return True
