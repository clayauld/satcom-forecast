from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Dict, Optional

from .const import DEFAULT_POLLING_INTERVAL
from .forecast_fetcher_api import fetch_forecast
from .forecast_parser import format_forecast
from .imap_handler import check_imap_for_gps
from .notifier import send_forecast_email
from .split_util import split_message

# ---------------------------------------------------------------------------
# Home-Assistant helper import
# ---------------------------------------------------------------------------

# During normal execution inside Home-Assistant we can import the real
# `DataUpdateCoordinator`.  When the integration is imported in a standalone
# environment (unit-tests, CI, static-analysis) the import is missing.  We guard
# against that and provide a *typed* fallback stub so that `mypy` does not
# complain about unresolved symbols.

if TYPE_CHECKING:
    # Only needed for static analysis; HA is not installed in the test image.
    from homeassistant.helpers.update_coordinator import (
        DataUpdateCoordinator as _HADataUpdateCoordinator,  # pragma: no cover
    )

    DataUpdateCoordinatorBase = _HADataUpdateCoordinator  # alias for typing
else:  # Runtime import with graceful fallback
    try:
        from homeassistant.helpers.update_coordinator import (
            DataUpdateCoordinator as DataUpdateCoordinatorBase,
        )
    except ImportError:  # pragma: no cover

        class DataUpdateCoordinatorBase:
            """Lightweight stub used when Home-Assistant is absent."""

            def __init__(
                self,
                hass: Optional[Any] = None,
                logger: Optional[logging.Logger] = None,
                name: Optional[str] = None,
                update_interval: Optional[timedelta] = None,
            ) -> None:
                self.hass = hass
                self.logger = logger
                self.name = name
                self.update_interval = update_interval

            async def async_config_entry_first_refresh(self) -> None:  # noqa: D401
                return None


# Re-export under the public name expected by the rest of the module.
if TYPE_CHECKING:
    DataUpdateCoordinator = DataUpdateCoordinatorBase
else:
    DataUpdateCoordinator = DataUpdateCoordinatorBase  # type: ignore[misc,assignment,valid-type]

_LOGGER = logging.getLogger(__name__)


class SatcomForecastCoordinator(DataUpdateCoordinatorBase):  # type: ignore[misc,valid-type]
    """Periodically polls an IMAP inbox for GPS requests and dispatches NWS
    forecasts back to the requesting sender.
    """

    def __init__(self, hass: Any, config: Dict[str, Any]) -> None:  # noqa: D401
        # Get polling interval from config, default to 5 minutes
        polling_interval = config.get("polling_interval", DEFAULT_POLLING_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            name="satcom_forecast",
            update_interval=timedelta(minutes=polling_interval),
        )
        self.config: Dict[str, Any] = config

        # Coordinator data that will be exposed to HA entities
        self._data: Dict[str, Any] = {
            "last_forecast_time": None,
            "last_sender": None,
            "gps_received_count": 0,
            "last_forecast": None,
            "last_coordinates": None,
        }
        self.data: Dict[str, Any] = self._data.copy()
        _LOGGER.debug(
            "SatcomForecastCoordinator initialized with config: %s",
            {
                k: v if k not in ["imap_pass", "smtp_pass"] else "***"
                for k, v in config.items()
            },
        )
        _LOGGER.info("Polling interval set to %d minutes", polling_interval)

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update coordinator data and process any new GPS requests."""
        _LOGGER.debug("Starting coordinator update cycle")

        messages = await check_imap_for_gps(
            self.config["imap_host"],
            self.config["imap_port"],
            self.config["imap_user"],
            self.config["imap_pass"],
            self.config.get("imap_folder", "INBOX"),
            self.config.get("imap_security", "SSL"),
        )

        _LOGGER.debug(
            "IMAP check completed, found %d messages", len(messages) if messages else 0
        )

        if messages:
            self._data["gps_received_count"] += len(messages)
            _LOGGER.info("Found %d GPS requests to process", len(messages))

        for i, msg in enumerate(messages):
            _LOGGER.debug(
                "Processing message %d/%d from %s with coordinates %s, %s",
                i + 1,
                len(messages),
                msg.get("sender", "unknown"),
                msg.get("lat"),
                msg.get("lon"),
            )

            try:
                # Fetch forecast using the dedicated module
                _LOGGER.debug(
                    "Fetching forecast for coordinates %s, %s", msg["lat"], msg["lon"]
                )

                # Determine number of days to include
                days = msg.get("days")
                if days is None:
                    days = self.config.get("default_days", 3)

                _LOGGER.debug(
                    "Using %d days for forecast (override: %s, default: %s)",
                    days,
                    msg.get("days"),
                    self.config.get("default_days", 3),
                )
                _LOGGER.debug(
                    "Config default_days value: %s", self.config.get("default_days")
                )
                _LOGGER.debug("Message days override: %s", msg.get("days"))

                forecast_text = await fetch_forecast(msg["lat"], msg["lon"], days)

                if forecast_text and not forecast_text.startswith("NWS error"):
                    _LOGGER.debug(
                        "Forecast fetched successfully, length: %d characters",
                        len(forecast_text),
                    )

                    # Format the forecast based on user preference
                    format_type = msg.get("format") or self.config.get(
                        "forecast_format", "summary"
                    )
                    _LOGGER.debug("Formatting forecast using format: %s", format_type)

                    forecast = format_forecast(forecast_text, str(format_type), days)
                    _LOGGER.debug(
                        "Forecast formatted successfully, length: %d characters",
                        len(forecast),
                    )

                    # Determine target device type and optional custom character limit
                    device_type = self.config.get("device_type", "zoleo")
                    # Character limit may come from YAML/ConfigEntry as a string;
                    # attempt to cast to int and fall back to None if it fails.
                    character_limit_raw = self.config.get("character_limit")
                    try:
                        character_limit = (
                            int(character_limit_raw)
                            if character_limit_raw is not None
                            else None
                        )
                    except (TypeError, ValueError):
                        _LOGGER.warning(
                            "Invalid character_limit value '%s' (type %s); falling back to default",  # noqa: E501
                            character_limit_raw,
                            type(character_limit_raw).__name__,
                        )
                        character_limit = None

                    _LOGGER.debug(
                        "Using split_message with device_type='%s', character_limit=%s",
                        device_type,
                        character_limit,
                    )

                    # Pass parameters explicitly to avoid type mismatches
                    message_parts = split_message(
                        forecast,
                        device_type=device_type,
                        custom_limit=character_limit if character_limit else None,
                    )
                    _LOGGER.debug("Message split into %d parts", len(message_parts))

                    # Send each part of the forecast
                    success = True
                    for i, part in enumerate(message_parts):
                        _LOGGER.debug(
                            "Sending part %d/%d to %s (length: %d chars)",
                            i + 1,
                            len(message_parts),
                            msg["sender"],
                            len(part),
                        )

                        part_success = await send_forecast_email(
                            self.config["smtp_host"],
                            self.config["smtp_port"],
                            self.config["smtp_user"],
                            self.config["smtp_pass"],
                            msg["sender"],
                            part,
                            subject=(
                                f"NWS Forecast Update ({i+1}/{len(message_parts)})"
                                if len(message_parts) > 1
                                else "NWSForecast Update"
                            ),
                        )
                        if not part_success:
                            success = False
                            _LOGGER.error(
                                "Failed to send part %d/%d to %s",
                                i + 1,
                                len(message_parts),
                                msg["sender"],
                            )
                            break
                        else:
                            _LOGGER.debug(
                                "Successfully sent part %d/%d to %s",
                                i + 1,
                                len(message_parts),
                                msg["sender"],
                            )

                    if success:
                        # Update tracking data
                        self._data["last_forecast_time"] = datetime.now().isoformat()
                        self._data["last_sender"] = msg["sender"]
                        self._data["last_forecast"] = forecast
                        self._data["last_coordinates"] = f"{msg['lat']}, {msg['lon']}"

                        _LOGGER.info(
                            "Forecast sent successfully to %s for coordinates %s, %s (%d parts)",
                            msg["sender"],
                            msg["lat"],
                            msg["lon"],
                            len(message_parts),
                        )
                        _LOGGER.debug("Updated coordinator data: %s", self._data)
                    else:
                        _LOGGER.error(
                            "Failed to send forecast email to %s", msg["sender"]
                        )
                else:
                    _LOGGER.error(
                        "Failed to fetch forecast for coordinates %s, %s: %s",
                        msg["lat"],
                        msg["lon"],
                        forecast_text,
                    )

            except Exception as e:
                _LOGGER.error(
                    "Forecast dispatch failed for %s: %s",
                    msg.get("sender", "unknown"),
                    e,
                )
                _LOGGER.debug("Exception details:", exc_info=True)

        _LOGGER.debug("Coordinator update cycle completed")
        self.data = self._data.copy()
        return self.data
