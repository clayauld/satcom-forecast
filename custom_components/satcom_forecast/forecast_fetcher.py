import aiohttp
from bs4 import BeautifulSoup
import logging
import os

_LOGGER = logging.getLogger(__name__)

async def fetch_forecast(lat, lon):
    """Fetch NOAA forecast for given coordinates using aiohttp."""
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

    try:
        async with aiohttp.ClientSession() as session:
            _LOGGER.debug("Making HTTP request to NOAA")
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                _LOGGER.debug("NOAA response status: %s", response.status)
                response.raise_for_status()
                content = await response.text()
                _LOGGER.debug("NOAA response content length: %d characters", len(content))

        soup = BeautifulSoup(content, 'html.parser')
        _LOGGER.debug("Parsed HTML with BeautifulSoup")
        
        # Find the forecast div with the specific style
        forecast_div = soup.find("div", style="margin:25px 0px 0px 0px;")
        
        if not forecast_div:
            _LOGGER.warning("Forecast div not found in NOAA response")
            _LOGGER.debug("Available divs with style attributes: %s", 
                         [div.get('style', 'no-style') for div in soup.find_all("div") if div.get('style')])
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
        
        # Get the forecast periods from the table
        tables = forecast_div.find_all("table")
        _LOGGER.debug("Found %d tables in forecast div", len(tables))
        
        if len(tables) >= 2:  # Should have at least 2 tables
            forecast_table = tables[1]  # Second table contains the forecast
            rows = forecast_table.find_all("tr")
            _LOGGER.debug("Found %d rows in forecast table", len(rows))
            
            for i, row in enumerate(rows):
                cells = row.find_all("td")
                _LOGGER.debug("Row %d has %d cells", i+1, len(cells))
                
                for j, cell in enumerate(cells):
                    text = cell.get_text(strip=True)
                    if text and not text.startswith("Visit your local") and not text.startswith("22 Miles"):
                        forecast_text += text + "\n"
                        _LOGGER.debug("Added cell text (row %d, cell %d): %s", i+1, j+1, text[:50] + "..." if len(text) > 50 else text)
        else:
            _LOGGER.debug("Not enough tables found for forecast extraction")

        if not forecast_text.strip():
            _LOGGER.warning("No forecast text extracted from NOAA response")
            return "Unable to extract forecast data from NOAA response."

        # Clean up the text
        forecast_text = forecast_text.strip()
        _LOGGER.debug("Final forecast text length: %d characters", len(forecast_text))
        
        # Optional: log raw output for debugging
        log_path = os.path.join(os.path.dirname(__file__), "forecast_raw_output.txt")
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(forecast_text)
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
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(f"Error fetching forecast: {str(e)}\n")
            _LOGGER.debug("Error logged to: %s", log_path)
        except Exception:
            pass
        return f"NOAA error: {str(e)}"
