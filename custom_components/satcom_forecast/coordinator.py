import logging
from datetime import timedelta, datetime
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .imap_handler import check_imap_for_gps
from .forecast_parser import format_forecast
from .notifier import send_forecast_email
from .forecast_fetcher import fetch_forecast
from .split_util import split_message

_LOGGER = logging.getLogger(__name__)

class SatcomForecastCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, config):
        super().__init__(hass, _LOGGER, name="satcom_forecast", update_interval=timedelta(minutes=5))
        self.config = config
        self._data = {
            "last_forecast_time": None,
            "last_sender": None,
            "gps_received_count": 0,
            "last_forecast": None,
            "last_coordinates": None
        }
        self.data = self._data.copy()
        _LOGGER.debug("SatcomForecastCoordinator initialized with config: %s", {k: v if k not in ['imap_pass', 'smtp_pass'] else '***' for k, v in config.items()})

    async def _async_update_data(self):
        """Update coordinator data and process any new GPS requests."""
        _LOGGER.debug("Starting coordinator update cycle")
        
        messages = check_imap_for_gps(
            self.config["imap_host"], self.config["imap_port"],
            self.config["imap_user"], self.config["imap_pass"],
            self.config.get("imap_folder", "INBOX")
        )
        
        _LOGGER.debug("IMAP check completed, found %d messages", len(messages) if messages else 0)
        
        if messages:
            self._data["gps_received_count"] += len(messages)
            _LOGGER.info("Found %d GPS requests to process", len(messages))
        
        for i, msg in enumerate(messages):
            _LOGGER.debug("Processing message %d/%d from %s with coordinates %s, %s", 
                         i+1, len(messages), msg.get("sender", "unknown"), msg.get("lat"), msg.get("lon"))
            
            try:
                # Fetch forecast using the dedicated module
                _LOGGER.debug("Fetching forecast for coordinates %s, %s", msg['lat'], msg['lon'])
                forecast_text = await fetch_forecast(msg['lat'], msg['lon'])
                
                if forecast_text and not forecast_text.startswith("NOAA error"):
                    _LOGGER.debug("Forecast fetched successfully, length: %d characters", len(forecast_text))
                    
                    # Format the forecast based on user preference
                    format_type = msg.get("format") or self.config.get("forecast_format", "summary")
                    _LOGGER.debug("Formatting forecast using format: %s", format_type)
                    
                    forecast = format_forecast(forecast_text, format_type)
                    _LOGGER.debug("Forecast formatted successfully, length: %d characters", len(forecast))
                    
                    # Split message if needed for device constraints
                    device_config = {
                        'device_type': self.config.get('device_type', 'zoleo'),
                        'character_limit': self.config.get('character_limit', 0)
                    }
                    _LOGGER.debug("Device config: %s", device_config)
                    
                    message_parts = split_message(forecast, device_config)
                    _LOGGER.debug("Message split into %d parts", len(message_parts))
                    
                    # Send each part of the forecast
                    success = True
                    for i, part in enumerate(message_parts):
                        _LOGGER.debug("Sending part %d/%d to %s (length: %d chars)", 
                                    i+1, len(message_parts), msg["sender"], len(part))
                        
                        part_success = send_forecast_email(
                            self.config["smtp_host"], self.config["smtp_port"],
                            self.config["smtp_user"], self.config["smtp_pass"],
                            msg["sender"], part,
                            subject=f"NOAA Forecast Update ({i+1}/{len(message_parts)})" if len(message_parts) > 1 else "NOAA Forecast Update"
                        )
                        if not part_success:
                            success = False
                            _LOGGER.error("Failed to send part %d/%d to %s", i+1, len(message_parts), msg["sender"])
                            break
                        else:
                            _LOGGER.debug("Successfully sent part %d/%d to %s", i+1, len(message_parts), msg["sender"])
                    
                    if success:
                        # Update tracking data
                        self._data["last_forecast_time"] = datetime.now().isoformat()
                        self._data["last_sender"] = msg["sender"]
                        self._data["last_forecast"] = forecast
                        self._data["last_coordinates"] = f"{msg['lat']}, {msg['lon']}"
                        
                        _LOGGER.info("Forecast sent successfully to %s for coordinates %s, %s (%d parts)", 
                                   msg["sender"], msg["lat"], msg["lon"], len(message_parts))
                        _LOGGER.debug("Updated coordinator data: %s", self._data)
                    else:
                        _LOGGER.error("Failed to send forecast email to %s", msg["sender"])
                else:
                    _LOGGER.error("Failed to fetch forecast for coordinates %s, %s: %s", 
                                msg["lat"], msg["lon"], forecast_text)
                    
            except Exception as e:
                _LOGGER.error("Forecast dispatch failed for %s: %s", msg.get("sender", "unknown"), e)
                _LOGGER.debug("Exception details:", exc_info=True)
        
        _LOGGER.debug("Coordinator update cycle completed")
        self.data = self._data.copy()
        return self.data
