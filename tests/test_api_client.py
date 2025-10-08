"""
Unit tests for API client module.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
import aiohttp

from custom_components.satcom_forecast.api_client import (
    WeatherGovAPIClient,
    APIError,
    APIResponse
)


class TestWeatherGovAPIClient:
    """Test cases for WeatherGovAPIClient."""
    
    @pytest.fixture
    def client(self):
        """Create a test client instance."""
        return WeatherGovAPIClient(
            base_url="https://api.weather.gov",
            user_agent="TestAgent/1.0",
            timeout=5,
            retry_attempts=2
        )
    
    @pytest.mark.asyncio
    async def test_init(self, client):
        """Test client initialization."""
        assert client.base_url == "https://api.weather.gov"
        assert client.user_agent == "TestAgent/1.0"
        assert client.timeout == 5
        assert client.retry_attempts == 2
    
    @pytest.mark.asyncio
    async def test_validate_coordinates_valid(self, client):
        """Test coordinate validation with valid coordinates."""
        # Should not raise exception
        client._validate_coordinates(40.7128, -74.0060)
        client._validate_coordinates(0, 0)
        client._validate_coordinates(-90, -180)
        client._validate_coordinates(90, 180)
    
    @pytest.mark.asyncio
    async def test_validate_coordinates_invalid(self, client):
        """Test coordinate validation with invalid coordinates."""
        with pytest.raises(APIError, match="Latitude must be between -90 and 90"):
            client._validate_coordinates(91, 0)
        
        with pytest.raises(APIError, match="Longitude must be between -180 and 180"):
            client._validate_coordinates(0, 181)
        
        with pytest.raises(APIError, match="Coordinates must be numeric"):
            client._validate_coordinates("invalid", 0)
    
    @pytest.mark.asyncio
    async def test_validate_response_success(self, client):
        """Test response validation with valid response."""
        response = APIResponse(
            success=True,
            data={"properties": {"test": "data"}},
            status_code=200
        )
        
        result = client._validate_response(response)
        assert result == {"properties": {"test": "data"}}
    
    @pytest.mark.asyncio
    async def test_validate_response_failure(self, client):
        """Test response validation with invalid response."""
        response = APIResponse(success=False, error="Test error")
        
        with pytest.raises(APIError, match="API request failed: Test error"):
            client._validate_response(response)
        
        response = APIResponse(success=True, data={})
        with pytest.raises(APIError, match="No data in API response"):
            client._validate_response(response)
        
        response = APIResponse(success=True, data={"invalid": "structure"})
        with pytest.raises(APIError, match="Missing 'properties' in API response"):
            client._validate_response(response)
    
    @pytest.mark.asyncio
    async def test_get_gridpoint_success(self, client):
        """Test successful grid point conversion."""
        mock_response = APIResponse(
            success=True,
            data={
                "properties": {
                    "cwa": "OKX",
                    "gridX": 32,
                    "gridY": 34
                }
            },
            status_code=200
        )
        
        with patch.object(client, '_make_request', return_value=mock_response):
            office, grid_x, grid_y = await client.get_gridpoint(40.7128, -74.0060)
            
            assert office == "OKX"
            assert grid_x == 32
            assert grid_y == 34
    
    @pytest.mark.asyncio
    async def test_get_gridpoint_missing_field(self, client):
        """Test grid point conversion with missing field."""
        mock_response = APIResponse(
            success=True,
            data={
                "properties": {
                    "cwa": "OKX"
                    # Missing gridX and gridY
                }
            },
            status_code=200
        )
        
        with patch.object(client, '_make_request', return_value=mock_response):
            with pytest.raises(APIError, match="Missing required field in grid point response"):
                await client.get_gridpoint(40.7128, -74.0060)
    
    @pytest.mark.asyncio
    async def test_get_forecast_success(self, client):
        """Test successful forecast retrieval."""
        mock_response = APIResponse(
            success=True,
            data={
                "properties": {
                    "periods": [
                        {
                            "name": "Today",
                            "detailedForecast": "Sunny with a high near 75."
                        }
                    ]
                }
            },
            status_code=200
        )
        
        with patch.object(client, '_make_request', return_value=mock_response):
            result = await client.get_forecast("OKX", 32, 34)
            
            assert "properties" in result
            assert "periods" in result["properties"]
            assert len(result["properties"]["periods"]) == 1
    
    @pytest.mark.asyncio
    async def test_get_forecast_missing_periods(self, client):
        """Test forecast retrieval with missing periods."""
        mock_response = APIResponse(
            success=True,
            data={
                "properties": {
                    "invalid": "data"
                }
            },
            status_code=200
        )
        
        with patch.object(client, '_make_request', return_value=mock_response):
            with pytest.raises(APIError, match="Missing 'periods' in forecast response"):
                await client.get_forecast("OKX", 32, 34)
    
    @pytest.mark.asyncio
    async def test_get_alerts_success(self, client):
        """Test successful alerts retrieval."""
        mock_response = APIResponse(
            success=True,
            data={
                "features": [
                    {
                        "properties": {
                            "event": "Flood Warning",
                            "headline": "Flood Warning for Test Area"
                        }
                    }
                ]
            },
            status_code=200
        )
        
        with patch.object(client, '_make_request', return_value=mock_response):
            result = await client.get_alerts(40.7128, -74.0060)
            
            assert "features" in result
            assert len(result["features"]) == 1
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, client):
        """Test successful HTTP request."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"test": "data"})
        
        mock_session.request.return_value.__aenter__.return_value = mock_response
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            await client._ensure_session()
            result = await client._make_request("https://api.weather.gov/test")
            
            assert result.success is True
            assert result.data == {"test": "data"}
            assert result.status_code == 200
    
    @pytest.mark.asyncio
    async def test_make_request_http_error(self, client):
        """Test HTTP request with error response."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.text = AsyncMock(return_value="Not Found")
        
        mock_session.request.return_value.__aenter__.return_value = mock_response
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            await client._ensure_session()
            result = await client._make_request("https://api.weather.gov/test")
            
            assert result.success is False
            assert "Client error: HTTP 404" in result.error
            assert result.status_code == 404
    
    @pytest.mark.asyncio
    async def test_make_request_timeout(self, client):
        """Test HTTP request with timeout."""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session.request.side_effect = asyncio.TimeoutError()
            mock_session_class.return_value = mock_session
            
            await client._ensure_session()
            result = await client._make_request("https://api.weather.gov/test")
            
            assert result.success is False
            assert "Request timeout" in result.error
    
    @pytest.mark.asyncio
    async def test_make_request_retry_logic(self, client):
        """Test retry logic for server errors."""
        mock_session = AsyncMock()
        
        # First call returns 500, second call returns 200
        mock_response_500 = AsyncMock()
        mock_response_500.status = 500
        
        mock_response_200 = AsyncMock()
        mock_response_200.status = 200
        mock_response_200.json = AsyncMock(return_value={"test": "data"})
        
        mock_session.request.return_value.__aenter__.side_effect = [
            mock_response_500,
            mock_response_200
        ]
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            await client._ensure_session()
            result = await client._make_request("https://api.weather.gov/test")
            
            assert result.success is True
            assert result.data == {"test": "data"}
            assert mock_session.request.call_count == 2
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, client):
        """Test rate limiting functionality."""
        import time
        
        start_time = time.time()
        
        # Mock the session
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"test": "data"})
        mock_session.request.return_value.__aenter__.return_value = mock_response
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            await client._ensure_session()
            
            # Make two requests quickly
            await client._make_request("https://api.weather.gov/test1")
            await client._make_request("https://api.weather.gov/test2")
            
            # Should have taken at least the rate limit delay
            elapsed = time.time() - start_time
            assert elapsed >= client.rate_limit_delay
    
    @pytest.mark.asyncio
    async def test_context_manager(self, client):
        """Test client as context manager."""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            async with client as ctx_client:
                assert ctx_client is client
                assert client._session is not None
            
            # Session should be closed after context
            mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close(self, client):
        """Test manual session close."""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            await client._ensure_session()
            await client.close()
            
            mock_session.close.assert_called_once()
            assert client._session is None


class TestAPIResponse:
    """Test cases for APIResponse dataclass."""
    
    def test_api_response_creation(self):
        """Test APIResponse creation."""
        response = APIResponse(
            success=True,
            data={"test": "data"},
            status_code=200,
            response_time=1.5
        )
        
        assert response.success is True
        assert response.data == {"test": "data"}
        assert response.status_code == 200
        assert response.response_time == 1.5
        assert response.error is None
        assert response.cached is False
    
    def test_api_response_with_error(self):
        """Test APIResponse with error."""
        response = APIResponse(
            success=False,
            error="Test error",
            status_code=404
        )
        
        assert response.success is False
        assert response.error == "Test error"
        assert response.status_code == 404
        assert response.data is None


class TestAPIError:
    """Test cases for APIError exception."""
    
    def test_api_error_creation(self):
        """Test APIError creation."""
        error = APIError("Test error message")
        assert str(error) == "Test error message"
        assert error.error_info is None
    
    def test_api_error_with_info(self):
        """Test APIError with error info."""
        from custom_components.satcom_forecast.api_error_handler import ErrorInfo, ErrorSeverity, ErrorCategory, ErrorContext
        
        context = ErrorContext(operation="test")
        error_info = ErrorInfo(
            error_type="TestError",
            message="Test error",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.API_ERROR,
            context=context
        )
        
        error = APIError("Test error message", error_info)
        assert str(error) == "Test error message"
        assert error.error_info == error_info