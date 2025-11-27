
import asyncio
import aiohttp
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

USER_AGENT = "SatComForecast/1.0 (https://github.com/clayauld/satcom-forecast)"

async def fetch_url(session, url):
    print(f"Fetching {url}...")
    try:
        async with session.get(url) as response:
            print(f"Status: {response.status}")
            if response.status == 200:
                return await response.json()
            else:
                text = await response.text()
                print(f"Error body: {text[:200]}...")
                return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

async def test_location(session, lat, lon, name):
    print(f"\n--- Testing {name} ({lat}, {lon}) ---")
    
    # 1. Get Points
    points_url = f"https://api.weather.gov/points/{lat},{lon}"
    points_data = await fetch_url(session, points_url)
    
    if not points_data:
        print("Failed to get points data.")
        return

    properties = points_data.get('properties', {})
    forecast_url = properties.get('forecast')
    cwa = properties.get('cwa')
    gridX = properties.get('gridX')
    gridY = properties.get('gridY')
    
    print(f"Gridpoint: {cwa}/{gridX},{gridY}")
    print(f"Forecast URL from API: {forecast_url}")
    
    constructed_url = f"https://api.weather.gov/gridpoints/{cwa}/{gridX},{gridY}/forecast"
    print(f"Constructed URL:       {constructed_url}")
    
    if forecast_url != constructed_url:
        print("WARNING: Constructed URL does not match API provided URL!")
    
    # 2. Get Forecast using the link provided by API
    if forecast_url:
        forecast_data = await fetch_url(session, forecast_url)
        if forecast_data:
            periods = forecast_data.get('properties', {}).get('periods', [])
            print(f"Success! Retrieved {len(periods)} periods.")
        else:
            print("Failed to retrieve forecast.")

async def main():
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'application/json'
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        # Test User's Location
        await test_location(session, 61.40804, -148.44403, "User Location (Alaska)")
        
        # Test Reference Location (Kansas) - known to work usually
        await test_location(session, 39.7456, -97.0892, "Reference Location (Kansas)")

if __name__ == "__main__":
    asyncio.run(main())
