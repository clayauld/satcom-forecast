from typing import Any, Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = [
        SatcomSensor(
            coordinator, "last_forecast_time", "Last Forecast Time", "timestamp"
        ),
        SatcomSensor(coordinator, "last_sender", "Last Requester", None),
        SatcomSensor(coordinator, "gps_received_count", "GPS Received Count", "count"),
    ]
    async_add_entities(sensors)


class SatcomSensor(CoordinatorEntity):
    def __init__(
        self,
        coordinator: Any,
        key: str,
        name: str,
        device_class: Optional[str],
    ) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_name = f"SatCom {name}"
        self._attr_unique_id = f"satcom_{key}"
        self._attr_device_class = device_class

    @property
    def state(self) -> Any:
        return self.coordinator.data.get(self._key)
