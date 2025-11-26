"""
Weather.gov API Client Module

This module handles all interactions with the Weather.gov API, including
coordinate conversion, forecast data fetching, and error handling.
"""

import asyncio
import json
import logging
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass

import aiohttp

_LOGGER = logging.getLogger(__name__)


@dataclass
class APIResponse:
    """Represents an API response with metadata."""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    response_time: float = 0.0
    cached: bool = False


class APIError(Exception):
    """Custom exception for API-related errors."""
    
    def __init__(self, message: str, error_info=None):
        super().__init__(message)
        self.error_info = error_info


class WeatherGovAPIClient:
    """Client for interacting with the Weather.gov API."""
    
    def __init__(self, 
                 base_url: str = "https://api.weather.gov",
                 user_agent: str = "SatComForecast/1.0 (https://github.com/clayauld/satcom-forecast)",
                 timeout: int = 10,
                 retry_attempts: int = 3,
                 retry_delay: float = 1.0,
                 rate_limit_delay: float = 0.5):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for the Weather.gov API
            user_agent: User-Agent string for API requests
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts for failed requests
            retry_delay: Initial delay between retries in seconds
            rate_limit_delay: Delay between requests to respect rate limits
        """
        self.base_url = base_url.rstrip('/')
        self.user_agent = user_agent
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.rate_limit_delay = rate_limit_delay
        
        self._session: Optional[aiohttp.ClientSession] = None
        self._last_request_time = 0.0
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        
    async def _ensure_session(self):
        """Ensure HTTP session is created."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip, deflate'
            }
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=headers
            )
            
    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
            
    async def _rate_limit(self):
        """Implement rate limiting between requests."""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            _LOGGER.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            await asyncio.sleep(sleep_time)
            
        self._last_request_time = asyncio.get_event_loop().time()
        
    async def _make_request(self, url: str, method: str = "GET") -> APIResponse:
        """
        Make an HTTP request with retry logic and error handling.
        
        Args:
            url: URL to request
            method: HTTP method (GET, POST, etc.)
            
        Returns:
            APIResponse object with response data and metadata
        """
        await self._ensure_session()
        await self._rate_limit()
        
        start_time = asyncio.get_event_loop().time()
        
        for attempt in range(self.retry_attempts):
            try:
                _LOGGER.debug(f"Making {method} request to {url} (attempt {attempt + 1})")
                
                async with self._session.request(method, url) as response:
                    response_time = asyncio.get_event_loop().time() - start_time
                    
                    _LOGGER.debug(f"Response status: {response.status} in {response_time:.2f}s")
                    
                    if response.status == 200:
                        try:
                            data = await response.json()
                            _LOGGER.debug(f"Successfully parsed JSON response ({len(str(data))} chars)")
                            return APIResponse(
                                success=True,
                                data=data,
                                status_code=response.status,
                                response_time=response_time
                            )
                        except json.JSONDecodeError as e:
                            _LOGGER.error(f"Failed to parse JSON response: {e}")
                            return APIResponse(
                                success=False,
                                error=f"Invalid JSON response: {e}",
                                status_code=response.status,
                                response_time=response_time
                            )
                    elif response.status >= 500:
                        # Server error - retry
                        if attempt < self.retry_attempts - 1:
                            wait_time = self.retry_delay * (2 ** attempt)
                            _LOGGER.warning(f"Server error {response.status}, retrying in {wait_time}s")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            return APIResponse(
                                success=False,
                                error=f"Server error: HTTP {response.status}",
                                status_code=response.status,
                                response_time=response_time
                            )
                    else:
                        # Client error - don't retry
                        error_text = await response.text()
                        _LOGGER.error(f"Client error {response.status}: {error_text}")
                        return APIResponse(
                            success=False,
                            error=f"Client error: HTTP {response.status} - {error_text}",
                            status_code=response.status,
                            response_time=response_time
                        )
                        
            except asyncio.TimeoutError:
                if attempt < self.retry_attempts - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    _LOGGER.warning(f"Request timeout, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    response_time = asyncio.get_event_loop().time() - start_time
                    return APIResponse(
                        success=False,
                        error="Request timeout",
                        response_time=response_time
                    )
            except aiohttp.ClientError as e:
                if attempt < self.retry_attempts - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    _LOGGER.warning(f"Client error {e}, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    response_time = asyncio.get_event_loop().time() - start_time
                    return APIResponse(
                        success=False,
                        error=f"Client error: {e}",
                        response_time=response_time
                    )
            except Exception as e:
                response_time = asyncio.get_event_loop().time() - start_time
                _LOGGER.error(f"Unexpected error: {e}")
                return APIResponse(
                    success=False,
                    error=f"Unexpected error: {e}",
                    response_time=response_time
                )
                
        # If we get here, all retries failed
        response_time = asyncio.get_event_loop().time() - start_time
        return APIResponse(
            success=False,
            error="Max retries exceeded",
            response_time=response_time
        )
        
    def _validate_coordinates(self, lat: float, lon: float) -> None:
        """
        Validate coordinate values.
        
        Args:
            lat: Latitude (-90 to 90)
            lon: Longitude (-180 to 180)
            
        Raises:
            APIError: If coordinates are invalid
        """
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            raise APIError("Coordinates must be numeric")
            
        if not (-90 <= lat <= 90):
            raise APIError(f"Latitude must be between -90 and 90, got {lat}")
            
        if not (-180 <= lon <= 180):
            raise APIError(f"Longitude must be between -180 and 180, got {lon}")
            
    def _validate_response(self, response: APIResponse) -> dict:
        """
        Validate API response structure.
        
        Args:
            response: APIResponse object to validate
            
        Returns:
            Validated response data
            
        Raises:
            APIError: If response is invalid
        """
        if not response.success:
            raise APIError(f"API request failed: {response.error}")
            
        if not response.data:
            raise APIError("No data in API response")
            
        if 'properties' not in response.data and 'features' not in response.data:
            raise APIError("Missing 'properties' or 'features' in API response")
            
        return response.data
        
    async def get_gridpoint(self, lat: float, lon: float) -> Tuple[str, int, int, Optional[str]]:
        """
        Convert coordinates to NWS grid point.
        
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate
            
        Returns:
            Tuple of (office, grid_x, grid_y, forecast_url)
            
        Raises:
            APIError: If conversion fails
        """
        self._validate_coordinates(lat, lon)
        
        url = f"{self.base_url}/points/{lat},{lon}"
        _LOGGER.debug(f"Converting coordinates {lat},{lon} to grid point")
        
        response = await self._make_request(url)
        data = self._validate_response(response)
        
        try:
            properties = data['properties']
            office = properties['cwa']
            grid_x = properties['gridX']
            grid_y = properties['gridY']
            forecast_url = properties.get('forecast')
            
            _LOGGER.debug(f"Grid point: office={office}, grid_x={grid_x}, grid_y={grid_y}")
            return office, grid_x, grid_y, forecast_url
            
        except KeyError as e:
            raise APIError(f"Missing required field in grid point response: {e}")
            
    async def get_forecast(self, office: str, grid_x: int, grid_y: int, forecast_url: Optional[str] = None) -> dict:
        """
        Get forecast data for a grid point.
        
        Args:
            office: NWS office code
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate
            forecast_url: Optional direct URL for forecast (overrides construction)
            
        Returns:
            Forecast data dictionary
            
        Raises:
            APIError: If forecast fetch fails
        """
        if forecast_url:
            url = forecast_url
        else:
            url = f"{self.base_url}/gridpoints/{office}/{grid_x},{grid_y}/forecast"
            
        _LOGGER.debug(f"Fetching forecast for {office}/{grid_x},{grid_y} using URL: {url}")
        
        response = await self._make_request(url)
        data = self._validate_response(response)
        
        try:
            properties = data['properties']
            if 'periods' not in properties:
                raise APIError("Missing 'periods' in forecast response")
                
            _LOGGER.debug(f"Retrieved forecast with {len(properties['periods'])} periods")
            return data
            
        except KeyError as e:
            raise APIError(f"Missing required field in forecast response: {e}")
            
    async def get_alerts(self, lat: float, lon: float) -> dict:
        """
        Get weather alerts for coordinates (optional feature).
        
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate
            
        Returns:
            Alerts data dictionary
            
        Raises:
            APIError: If alerts fetch fails
        """
        self._validate_coordinates(lat, lon)
        
        url = f"{self.base_url}/alerts?point={lat},{lon}"
        _LOGGER.debug(f"Fetching alerts for {lat},{lon}")
        
        response = await self._make_request(url)
        data = self._validate_response(response)
        
        _LOGGER.debug(f"Retrieved alerts data")
        return data


# Convenience functions for backward compatibility
async def get_gridpoint(lat: float, lon: float, **kwargs) -> Tuple[str, int, int, Optional[str]]:
    """Get grid point for coordinates using default client settings."""
    async with WeatherGovAPIClient(**kwargs) as client:
        return await client.get_gridpoint(lat, lon)


async def get_forecast(office: str, grid_x: int, grid_y: int, **kwargs) -> dict:
    """Get forecast for grid point using default client settings."""
    async with WeatherGovAPIClient(**kwargs) as client:
        return await client.get_forecast(office, grid_x, grid_y)


async def get_alerts(lat: float, lon: float, **kwargs) -> dict:
    """Get alerts for coordinates using default client settings."""
    async with WeatherGovAPIClient(**kwargs) as client:
        return await client.get_alerts(lat, lon)