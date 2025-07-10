import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DEFAULT_DEBUG, DOMAIN
from .coordinator import SatcomForecastCoordinator

_LOGGER = logging.getLogger(__name__)

# Config schema for the integration - since this uses config entries, we use
# config_entry_only_config_schema
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 2:
        # Version 2 to 3 migration - add default polling interval
        new = {**config_entry.data}
        if "polling_interval" not in new:
            new["polling_interval"] = 5  # Default to 5 minutes
        hass.config_entries.async_update_entry(config_entry, data=new, version=3)
        _LOGGER.debug("Migration to version 3 successful")

    if config_entry.version == 3:
        # Version 3 to 4 migration - add default IMAP security
        new = {**config_entry.data}
        if "imap_security" not in new:
            new["imap_security"] = "SSL"  # Default to SSL for security
        hass.config_entries.async_update_entry(config_entry, data=new, version=4)
        _LOGGER.debug("Migration to version 4 successful")

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
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
    async def set_debug_logging(call: ServiceCall) -> None:
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


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Unregister service
    hass.services.async_remove(DOMAIN, "set_debug_logging")
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the integration when configuration changes."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
