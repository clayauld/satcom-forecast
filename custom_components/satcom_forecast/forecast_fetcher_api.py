"""
Enhanced Forecast Fetcher with API Support

This module provides a hybrid forecast fetcher that can use either the Weather.gov API
or fall back to HTML scraping, with comprehensive error handling and caching.
"""

import logging
import asyncio
from typing import Optional, Dict, Any, Tuple

from .api_client import WeatherGovAPIClient, APIError
from .api_data_processor import APIDataProcessor
from .api_config import get_config, is_api_enabled, is_fallback_enabled
from .api_cache import get_gridpoint_cache, get_forecast_cache
from .api_models import ForecastData, ProcessedForecast

# Import existing HTML fetcher for fallback
from .forecast_fetcher import fetch_forecast as fetch_forecast_html

_LOGGER = logging.getLogger(__name__)


class ForecastFetcherAPI:
    """Enhanced forecast fetcher with API support and fallback capabilities."""
    
    def __init__(self):
        self.config = get_config()
        self.data_processor = APIDataProcessor()
        self.gridpoint_cache = get_gridpoint_cache()
        self.forecast_cache = get_forecast_cache()
        
    async def fetch_forecast_api(self, lat: float, lon: float, days: Optional[int] = None) -> str:
        """
        Fetch forecast using the Weather.gov API.
        
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate
            days: Number of days to include (1-7, None for all available)
            
        Returns:
            Formatted forecast text
            
        Raises:
            APIError: If API request fails
        """
        _LOGGER.debug(f"Fetching forecast via API for coordinates: {lat}, {lon}")
        
        try:
            # Get grid point information
            office, grid_x, grid_y = await self._get_gridpoint(lat, lon)
            
            # Get forecast data
            forecast_data = await self._get_forecast(office, grid_x, grid_y)
            
            # Process the forecast data
            processed_data = self.data_processor.process_forecast_data(forecast_data)
            
            # Convert to text format compatible with existing parser
            forecast_text = self._convert_to_text_format(processed_data, days)
            
            _LOGGER.info(f"Successfully fetched forecast via API for {lat}, {lon}")
            return forecast_text
            
        except Exception as e:
            _LOGGER.error(f"API forecast fetch failed: {e}")
            raise APIError(f"Failed to fetch forecast via API: {e}")
            
    async def fetch_forecast_hybrid(self, 
                                   lat: float, 
                                   lon: float, 
                                   days: Optional[int] = None,
                                   mode: str = 'auto') -> str:
        """
        Fetch forecast using hybrid mode (API with HTML fallback).
        
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate
            days: Number of days to include (1-7, None for all available)
            mode: Fetch mode ('api', 'html', 'auto')
            
        Returns:
            Formatted forecast text
        """
        _LOGGER.debug(f"Fetching forecast in hybrid mode: {mode}")
        
        # Determine which method to use
        use_api = False
        if mode == 'api':
            use_api = True
        elif mode == 'html':
            use_api = False
        elif mode == 'auto':
            use_api = is_api_enabled()
        else:
            _LOGGER.warning(f"Unknown mode '{mode}', defaulting to auto")
            use_api = is_api_enabled()
            
        if use_api:
            try:
                return await self.fetch_forecast_api(lat, lon, days)
            except APIError as e:
                if is_fallback_enabled():
                    _LOGGER.warning(f"API failed, falling back to HTML: {e}")
                    return await fetch_forecast_html(lat, lon, days)
                else:
                    _LOGGER.error(f"API failed and fallback disabled: {e}")
                    raise
        else:
            _LOGGER.debug("Using HTML scraping mode")
            return await fetch_forecast_html(lat, lon, days)
            
    async def _get_gridpoint(self, lat: float, lon: float) -> Tuple[str, int, int]:
        """
        Get grid point information for coordinates.
        
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate
            
        Returns:
            Tuple of (office, grid_x, grid_y)
        """
        # Check cache first
        cache_key = f"gridpoint_{lat}_{lon}"
        cached_data = await self.gridpoint_cache.get(cache_key)
        
        if cached_data:
            _LOGGER.debug("Using cached grid point data")
            return cached_data['office'], cached_data['grid_x'], cached_data['grid_y']
            
        # Fetch from API
        api_config = self.config.get_api_config_dict()
        async with WeatherGovAPIClient(**api_config) as client:
            office, grid_x, grid_y = await client.get_gridpoint(lat, lon)
            
        # Cache the result
        cache_data = {
            'office': office,
            'grid_x': grid_x,
            'grid_y': grid_y
        }
        await self.gridpoint_cache.set(cache_key, cache_data)
        
        return office, grid_x, grid_y
        
    async def _get_forecast(self, office: str, grid_x: int, grid_y: int) -> Dict[str, Any]:
        """
        Get forecast data for a grid point.
        
        Args:
            office: NWS office code
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate
            
        Returns:
            Forecast data dictionary
        """
        # Check cache first
        cache_key = f"forecast_{office}_{grid_x}_{grid_y}"
        cached_data = await self.forecast_cache.get(cache_key)
        
        if cached_data:
            _LOGGER.debug("Using cached forecast data")
            return cached_data
            
        # Fetch from API
        api_config = self.config.get_api_config_dict()
        async with WeatherGovAPIClient(**api_config) as client:
            forecast_data = await client.get_forecast(office, grid_x, grid_y)
            
        # Cache the result
        await self.forecast_cache.set(cache_key, forecast_data)
        
        return forecast_data
        
    def _convert_to_text_format(self, forecast_data: ForecastData, days: Optional[int] = None) -> str:
        """
        Convert processed forecast data to text format compatible with existing parser.
        
        Args:
            forecast_data: Processed forecast data
            days: Number of days to include
            
        Returns:
            Formatted forecast text
        """
        text_parts = []
        
        # Add location information if available
        if forecast_data.location:
            text_parts.append(forecast_data.location)
            
        # Add forecast periods
        periods_to_include = forecast_data.periods
        if days is not None:
            # Filter periods based on days parameter
            periods_to_include = self._filter_periods_by_days(forecast_data.periods, days)
            
        for period in periods_to_include:
            period_text = f"{period.name}: {period.detailed_forecast}"
            text_parts.append(period_text)
            
        return "\n".join(text_parts)
        
    def _filter_periods_by_days(self, periods: list, days: int) -> list:
        """
        Filter forecast periods based on days parameter.
        
        Args:
            periods: List of forecast periods
            days: Number of days to include
            
        Returns:
            Filtered list of periods
        """
        if days is None or days <= 0:
            return periods
            
        # Group periods by day
        day_groups = {}
        for period in periods:
            day_name = self._get_day_name(period.name)
            if day_name not in day_groups:
                day_groups[day_name] = []
            day_groups[day_name].append(period)
            
        # Select the first N days
        selected_days = list(day_groups.keys())[:days]
        filtered_periods = []
        
        for day in selected_days:
            filtered_periods.extend(day_groups[day])
            
        return filtered_periods
        
    def _get_day_name(self, period_name: str) -> str:
        """
        Extract day name from period name.
        
        Args:
            period_name: Period name (e.g., "Monday Night", "Today")
            
        Returns:
            Day name (e.g., "Monday", "Today")
        """
        # Handle special cases
        if period_name in ["Today", "Tonight", "This Afternoon", "Overnight"]:
            return "Today"
            
        # Remove "Night" suffix
        if period_name.endswith(" Night"):
            return period_name[:-6]
            
        return period_name
        
    def validate_coordinates(self, lat: float, lon: float) -> bool:
        """
        Validate coordinate values.
        
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate
            
        Returns:
            True if coordinates are valid
        """
        try:
            if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
                return False
                
            if not (-90 <= lat <= 90):
                return False
                
            if not (-180 <= lon <= 180):
                return False
                
            return True
        except Exception:
            return False
            
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            'gridpoint_cache': self.gridpoint_cache.get_stats(),
            'forecast_cache': self.forecast_cache.get_stats()
        }
        
    async def clear_caches(self):
        """Clear all caches."""
        await self.gridpoint_cache.clear()
        await self.forecast_cache.clear()
        _LOGGER.info("Cleared all caches")


# Convenience functions for backward compatibility
async def fetch_forecast_api(lat: float, lon: float, days: Optional[int] = None) -> str:
    """Fetch forecast using API with default settings."""
    fetcher = ForecastFetcherAPI()
    return await fetcher.fetch_forecast_api(lat, lon, days)


async def fetch_forecast_hybrid(lat: float, 
                               lon: float, 
                               days: Optional[int] = None,
                               mode: str = 'auto') -> str:
    """Fetch forecast using hybrid mode with default settings."""
    fetcher = ForecastFetcherAPI()
    return await fetcher.fetch_forecast_hybrid(lat, lon, days, mode)


# Main function that replaces the original fetch_forecast
async def fetch_forecast(lat: float, lon: float, days: Optional[int] = None) -> str:
    """
    Main forecast fetch function with automatic mode selection.
    
    This function replaces the original fetch_forecast function and automatically
    chooses between API and HTML modes based on configuration.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        days: Number of days to include (1-7, None for all available)
        
    Returns:
        Formatted forecast text
    """
    fetcher = ForecastFetcherAPI()
    
    # Validate coordinates
    if not fetcher.validate_coordinates(lat, lon):
        _LOGGER.error(f"Invalid coordinates: {lat}, {lon}")
        return f"NWS error: Invalid coordinates {lat}, {lon}"
        
    try:
        return await fetcher.fetch_forecast_hybrid(lat, lon, days, mode='auto')
    except Exception as e:
        _LOGGER.error(f"Forecast fetch failed: {e}")
        return f"NWS error: {str(e)}"