# Forecast Format Comparison

This document shows the three different forecast formats available in the SatCom Forecast integration, with examples and use cases.

## 📍 Test Locations
**Primary Test:** 61.408, -148.444 (22 Miles ESE Butte, AK)  
**Multi-Region Test:** Fairbanks AK, Anchorage AK, Miami FL, Chicago IL, Boston MA, Los Angeles CA  
**Date:** June 2025  
**Weather:** Various conditions including rain, thunderstorms, fog, wind, smoke, and extreme events

---

## 🌧️ SUMMARY Format

**Purpose:** Time-based weather summary showing when significant events occur with probabilities  
**Best for:** Users who need actionable weather information for planning  
**Length:** 80-150 characters  
**Parts:** 1 email (ZOLEO device)

### Example Output:
```
Ton:Rn(40%),L:46°,SE5-10mph | Tue:Rn(40%),H:61°,SE5-10mph,L:45°,E15mph | Wed:Rn(50%),H:61°,E5-10mph
```

### What the user receives:

**Email:**
```
Subject: NOAA Forecast Update
Body: Ton:Rn(40%),L:46°,SE5-10mph | Tue:Rn(40%),H:61°,SE5-10mph,L:45°,E15mph | Wed:Rn(50%),H:61°,E5-10mph
```

### Key Features:
- ✅ **Time-Based Format**: Shows exactly when weather events are expected
- ✅ **Probability Included**: Each event shows its likelihood percentage
- ✅ **Pipe Separators**: Clean visual separation between time periods
- ✅ **Extreme Event Highlighting**: 🚨 for extreme events (blizzard, tornado, smoke, etc.)
- ✅ **Multi-Season Weather Detection**: Rain, snow, sleet, freezing rain, wind, hail, thunderstorms, fog, smoke
- ✅ **Smart inference** when percentages aren't explicitly stated
- ✅ **Single Message Delivery**: Always fits in one email
- ✅ **Prioritized Events**: Shows most significant weather conditions first
- ✅ **Temperature Information**: High/low temperatures with degree symbols (°)
- ✅ **Wind Information**: Direction and speed for significant wind events (15+ mph)

### Weather Event Detection:
- **Rain/Precipitation**: Rain, showers, drizzle, sprinkles
- **Snow**: Snow, blizzard, flurries, snowfall
- **Sleet/Freezing Rain**: Sleet, freezing rain, ice, icy
- **Wind**: Windy, gusts, high wind, breezy (only for 15+ mph)
- **Thunderstorms**: Thunderstorm, t-storm, severe thunderstorm
- **Fog**: Fog, foggy, haze, mist, dense fog, patchy fog
- **Smoke**: Smoke, smoky, wildfire smoke, fire smoke, smoke from fires
- **Extreme Events**: Blizzard, ice storm, tornado, hurricane, severe thunderstorm, high wind warning, flood warning, dense fog, smoke

### Precipitation Inference Logic:
- **Rain likely/Showers likely**: 70%
- **Scattered rain/showers**: 40%
- **Isolated rain/showers**: 20%
- **Chance of rain**: 30%
- **General rain/showers**: 50%
- **Drizzle/Sprinkles**: 25%
- **Blizzard**: 90%
- **Heavy snow**: 70%
- **Snow flurries**: 30%
- **Fog conditions**: 60-90% depending on type
- **Smoke conditions**: 70-90% depending on intensity

### Multi-Region Examples:
- **Fairbanks, AK:** `Ton:🚨Smoke(90%),Rn(80%),ThSt(80%),Fg(80%) | Tue:Rn(50%),Fg(50%) | Tue:Rn(50%),Fg(50%) | Wed:Rn(60%),ThSt(60%),Fg(60%) | Wed:Rn(60%),ThSt(60%)`
- **Miami, FL:** `Ton:Rn(30%),ThSt(30%) | Tue:Rn(30%),🚨Wnd(80%),ThSt(30%) | Tue:Rn(30%),ThSt(30%) | Wed:Rn(70%),ThSt(70%) | Wed:Rn(30%),ThSt(30%)`
- **Los Angeles, CA:** `Ton:Fg(60%),PFg(60%) | Tue:Fg(60%),PFg(60%) | Tue:Fg(60%),PFg(60%) | Wed:Fg(60%),PFg(60%) | Wed:Fg(60%),PFg(60%) | Thu:Fg(60%),PFg(60%)`

---

## 📋 COMPACT Format

**Purpose:** Brief weather summary with event indicators for each time period  
**Best for:** Users who want a quick overview with weather event highlights  
**Length:** 400-1500 characters  
**Parts:** 2-5 emails (ZOLEO device)

### Example Output:
```
Tonight: 🚨Smoke(90%), Rain(80%), Thunderstorm(80%) (L:46, SE5-10mph) | Smoke from nearby wildfires. Showers and possibly a thunderstorm before 10pm
Tuesday: Rain(50%), Fog(70%) (H:61, E5-10mph) | A chance of rain with foggy conditions
Tuesday Night: Rain (L:45, E15mph) | Scattered showers
Wednesday: 🚨Smoke(85%), Rain(60%), Thunderstorm(60%) (H:61, E5-10mph) | Heavy smoke conditions with showers likely
```

### What the user receives:

**Email 1/2:**
```
Subject: NOAA Forecast Update (1/2)
Body: (1/2) Tonight: 🚨Smoke(90%), Rain(80%), Thunderstorm(80%) (L:46, SE5-10mph) | Smoke from nearby wildfires. Showers and possibly a thunderstorm before 10pm | Tuesday: Rain(50%), Fog(70%) (H:61, E5-10mph) | A chance of rain with foggy conditions
```

**Email 2/2:**
```
Subject: NOAA Forecast Update (2/2)
Body: (2/2) Tuesday Night: Rain (L:45, E15mph) | Scattered showers | Wednesday: 🚨Smoke(85%), Rain(60%), Thunderstorm(60%) (H:61, E5-10mph) | Heavy smoke conditions with showers likely
```

### Key Features:
- ✅ **Weather Event Indicators**: Shows detected weather events as prefixes with probabilities
- ✅ **Extreme Event Highlighting**: 🚨 for extreme events
- ✅ Uses pipe separators for easy reading
- ✅ Includes temperature information (H:64°, L:45°)
- ✅ Includes wind information (direction and speed)
- ✅ Takes first sentence of each forecast
- ✅ **Enhanced Detection**: Same logic as Summary format
- ✅ **Fog Detection**: Properly identifies fog, patchy fog, haze, mist
- ✅ **Smoke Detection**: Detects wildfire smoke and smoke conditions
- ✅ **Wind Filtering**: Only shows wind events for significant speeds (15+ mph)

### Event Indicator Examples:
- `Tonight: Rain(80%), Thunderstorm(80%) | [forecast text]`
- `Wednesday: 🚨Smoke(90%), 🚨Blizzard(90%), Snow(70%) | [forecast text]`
- `Friday: Wnd(60%) | [forecast text]` (only for 15+ mph)
- `Tuesday: Fog(70%), Patchy Fog(60%) | [forecast text]`

---

## 📄 FULL Format

**Purpose:** Complete detailed forecast information  
**Best for:** Users who want comprehensive weather details  
**Length:** 1100-2000+ characters  
**Parts:** 6+ emails (ZOLEO device)

### Example Output:
```
Tonight: Scattered showers. Mostly cloudy, with a low around 40. Southwest wind around 5 mph becoming calm. Chance of precipitation is 40%.
Tuesday: Scattered showers. Partly sunny, with a high near 51. Calm wind becoming south around 5 mph. Chance of precipitation is 40%.
Tuesday Night: Scattered showers. Mostly cloudy, with a low around 42. South wind around 5 mph. Chance of precipitation is 50%.
Wednesday: Scattered showers. Cloudy, with a high near 52. South wind 5 to 10 mph. Chance of precipitation is 50%.
Wednesday Night: A chance of rain. Mostly cloudy, with a low around 41. Southeast wind around 10 mph. Chance of precipitation is 40%.
Thursday: A chance of rain. Cloudy, with a high near 52. Chance of precipitation is 50%.
Thursday Night: A chance of rain. Cloudy, with a low around 42.
Friday: A chance of rain. Cloudy, with a high near 54.
Friday Night: A chance of rain. Cloudy, with a low around 42.
Saturday: A chance of rain. Cloudy, with a high near 54.
Saturday Night: A chance of rain. Cloudy, with a low around 43.
Sunday: Rain likely. Cloudy, with a high near 52.
```

### What the user receives:
6+ separate emails with detailed forecast information for each time period.

### Key Features:
- ✅ Complete weather descriptions
- ✅ Temperature highs and lows
- ✅ Wind information
- ✅ Detailed precipitation chances
- ✅ Cloud cover information
- ✅ Full NOAA forecast text
- ✅ **All weather events visible** in the raw forecast text
- ✅ **Smart Truncation**: Cuts at sentence boundaries when needed
- ✅ **No Mid-Sentence Cuts**: Always shows complete sentences

---

## 📊 Format Comparison Summary

| Format | Length | Parts | Focus | Best Use Case |
|--------|--------|-------|-------|---------------|
| **SUMMARY** | 80-150 chars | 1 | Time-Based Weather Events + Probabilities + Temp/Wind | Quick planning around significant weather |
| **COMPACT** | 400-1500 chars | 2-5 | Quick Overview + Event Indicators + Temp/Wind | General weather awareness with highlights |
| **FULL** | 1100-2000+ chars | 6+ | Complete Details | Detailed trip planning |

## 🎯 Recommendations

### Choose SUMMARY if:
- You're primarily concerned about significant weather events
- You want the shortest possible message (single email)
- You're planning outdoor activities
- You have limited satellite communication time
- You need actionable weather data with timing
- You want to know when events will occur
- You need probability information for each event
- You want temperature and wind information in a concise format

### Choose COMPACT if:
- You want a quick weather overview
- You need temperature information
- You want a balance of detail and brevity
- You're checking general conditions
- You want weather event indicators with probabilities
- You prefer pipe-separated format
- You want to see forecast descriptions
- You need wind information for significant events

### Choose FULL if:
- You need complete weather details
- You're planning extended outdoor activities
- You want wind and cloud information
- You have plenty of satellite communication time
- You want the raw NOAA forecast text
- You need comprehensive meteorological data

## 🔧 How to Request Different Formats

Users can request specific formats by including the format name in their email:

- `61.408, -148.444 summary` → Summary format
- `61.408, -148.444 compact` → Compact format  
- `61.408, -148.444 full` → Full format
- `61.408, -148.444` → Default format (summary)

The integration will automatically detect the requested format and process accordingly.

## 🆕 Recent Improvements

### Enhanced Summary Format (June 2025)
The Summary format has been completely redesigned for better usability:

- **Time-Based Format**: Shows exactly when weather events occur
- **Probability Included**: Each event shows its likelihood percentage
- **Pipe Separators**: Clean visual separation between time periods
- **Single Message Delivery**: Always fits in one email (under 200 characters)
- **Prioritized Events**: Shows most significant weather conditions first
- **Temperature Information**: High/low temperatures with degree symbols (°)
- **Wind Information**: Direction and speed for significant wind events

### Enhanced Compact Format (June 2025)
The Compact format has been improved with:

- **Increased Character Limit**: Now supports 1500 characters for longer forecasts
- **Probability Display**: Shows percentages for all weather events
- **Temperature Formatting**: High/low temperatures with degree symbols (°)
- **Wind Information**: Direction and speed for significant wind events
- **Warning Indicators**: 🚨 for extreme events next to event names only

### Fixed FULL Format (June 2025)
The FULL format has been improved to prevent truncation issues:

- **Increased Character Limit**: Now supports 2000+ characters
- **Smart Truncation**: Cuts at sentence boundaries when needed
- **No Mid-Sentence Cuts**: Always shows complete sentences
- **Better Readability**: Complete meteorological information

### Enhanced Weather Detection (All Formats)
All three formats now use the same enhanced weather detection logic:

- **Multi-Season Support**: Rain, snow, sleet, freezing rain, wind, hail, thunderstorms
- **Fog Detection**: Fog, patchy fog, dense fog, haze, mist
- **Smoke Detection**: Wildfire smoke, smoke conditions, smoke from fires
- **Extreme Event Detection**: Blizzard, ice storm, tornado, hurricane, severe thunderstorm, high wind warning, flood warning, dense fog, smoke
- **Smart Inference**: Provides meaningful percentages when NOAA doesn't specify them
- **Visual Highlighting**: Extreme events marked with 🚨
- **Wind Filtering**: Only shows wind events for significant speeds (15+ mph)

### Multi-Region Testing
The system has been tested across diverse weather conditions:

- **Alaska (Fairbanks)**: Summer conditions with rain, thunderstorms, fog, wildfire smoke
- **Alaska (Anchorage)**: Coastal conditions with rain, fog, moderate temperatures
- **Florida (Miami)**: Hurricane season with wind, rain, thunderstorms
- **Illinois (Chicago)**: Spring conditions with rain, thunderstorms
- **Massachusetts (Boston)**: Summer heat wave with rain, thunderstorms
- **California (Los Angeles)**: Spring conditions with fog, patchy fog

This provides much more actionable information for users planning outdoor activities across all seasons and weather conditions, with the Summary format now being the most efficient for single-message delivery. 