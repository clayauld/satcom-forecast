import logging
import os

import aiofiles
import aiohttp
from bs4 import BeautifulSoup

# Try relative import first, fall back to absolute import for testing
try:
    from .forecast_parser import parse_forecast_periods
except ImportError:
    from forecast_parser import parse_forecast_periods

_LOGGER = logging.getLogger(__name__)


async def fetch_forecast(lat, lon, days=None):
    """Fetch NOAA forecast for given coordinates using aiohttp.

    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        days: Number of days to include in forecast (1-7, None for all available)
    """
    url = (
        f"https://forecast.weather.gov/MapClick.php"
        f"?lat={lat}&lon={lon}&unit=0&lg=english&FcstType=text&TextType=1"
    )
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36"
        )
    }

    _LOGGER.debug("Fetching forecast for coordinates: %s, %s", lat, lon)
    _LOGGER.debug("NOAA URL: %s", url)
    _LOGGER.debug("Days parameter: %s (None = all available)", days)

    try:
        async with aiohttp.ClientSession() as session:
            _LOGGER.debug("Making HTTP request to NOAA")
            async with session.get(
                url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                _LOGGER.debug("NOAA response status: %s", response.status)
                response.raise_for_status()
                content = await response.text()
                _LOGGER.debug(
                    "NOAA response content length: %d characters", len(content)
                )

        soup = BeautifulSoup(content, "html.parser")
        _LOGGER.debug("Parsed HTML with BeautifulSoup")

        # Find the forecast div with the specific style
        forecast_div = soup.find("div", style="margin:25px 0px 0px 0px;")

        if not forecast_div:
            _LOGGER.warning("Forecast div not found in NOAA response")
            _LOGGER.debug(
                "Available divs with style attributes: %s",
                [
                    div.get("style", "no-style")
                    for div in soup.find_all("div")
                    if div.get("style")
                ],
            )
            return "Unable to retrieve forecast data."

        _LOGGER.debug("Found forecast div, extracting content")

        # Extract the forecast text from the table structure
        forecast_text = ""

        # Get the location and issue info
        location_info = forecast_div.find("font", size="3")
        if location_info:
            location_text = location_info.get_text().strip()
            forecast_text += location_text + "\n"
            _LOGGER.debug("Found location info: %s", location_text)
        else:
            _LOGGER.debug("No location info found")

        # Get the forecast periods using the new parser
        forecast_html = str(forecast_div)
        periods = parse_forecast_periods(forecast_html, days)

        if periods:
            _LOGGER.debug("Successfully parsed %d forecast periods", len(periods))
            for period in periods:
                forecast_text += f"{period['day']}: {period['content']}\n"
        else:
            _LOGGER.warning("No forecast periods parsed from HTML")
            return "Unable to extract forecast data from NOAA response."

        # Clean up the text
        forecast_text = forecast_text.strip()
        _LOGGER.debug("Final forecast text length: %d characters", len(forecast_text))
        _LOGGER.debug(
            "Final forecast text preview: %s",
            forecast_text[:200] + "..." if len(forecast_text) > 200 else forecast_text,
        )

        # Optional: log raw output for debugging
        log_path = os.path.join(os.path.dirname(__file__), "forecast_raw_output.txt")
        try:
            async with aiofiles.open(log_path, "w", encoding="utf-8") as f:
                await f.write(forecast_text)
            _LOGGER.debug("Forecast raw output written to: %s", log_path)
        except Exception as e:
            _LOGGER.debug("Could not write forecast log: %s", e)

        return forecast_text

    except aiohttp.ClientError as e:
        _LOGGER.error("HTTP error fetching forecast: %s", e)
        _LOGGER.debug("HTTP error details:", exc_info=True)
        return f"NOAA error: Could not fetch forecast - {str(e)}"
    except Exception as e:
        _LOGGER.error("Error fetching forecast: %s", e)
        _LOGGER.debug("Exception details:", exc_info=True)
        log_path = os.path.join(os.path.dirname(__file__), "forecast_error.log")
        try:
            async with aiofiles.open(log_path, "w", encoding="utf-8") as f:
                await f.write(f"Error fetching forecast: {str(e)}\n")
            _LOGGER.debug("Error logged to: %s", log_path)
        except Exception:
            pass
        return f"NOAA error: {str(e)}"
