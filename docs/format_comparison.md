# Forecast Format Comparison

This document shows the three different forecast formats available in the SatCom Forecast integration, with examples and use cases.

## 📍 Test Locations
**Primary Test:** 61.408, -148.444 (22 Miles ESE Butte, AK)  
**Multi-Region Test:** Fairbanks AK, Anchorage AK, Miami FL, Chicago IL, Boston MA, Los Angeles CA  
**Date:** June 23, 2025  
**Weather:** Various conditions including rain, thunderstorms, fog, wind, and extreme events

---

## 🌧️ SUMMARY Format

**Purpose:** Time-based weather summary showing when significant events occur with probabilities  
**Best for:** Users who need actionable weather information for planning  
**Length:** 80-150 characters  
**Parts:** 1 email (ZOLEO device)

### Example Output:
```
Ton:Rain(40%) | Tue:Rain(40%) | Tue:Rain(50%) | Wed:Rain(50%) | Wed:Rain(40%) | Thu:Rain(50%)
```

### What the user receives:

**Email:**
```
Subject: NOAA Forecast Update
Body: Ton:Rain(40%) | Tue:Rain(40%) | Tue:Rain(50%) | Wed:Rain(50%) | Wed:Rain(40%) | Thu:Rain(50%)
```

### Key Features:
- ✅ **Time-Based Format**: Shows exactly when weather events are expected
- ✅ **Probability Included**: Each event shows its likelihood percentage
- ✅ **Pipe Separators**: Clean visual separation between time periods
- ✅ **Extreme Event Highlighting**: 🚨 for extreme events (blizzard, tornado, etc.)
- ✅ **Multi-Season Weather Detection**: Rain, snow, sleet, freezing rain, wind, hail, thunderstorms, fog
- ✅ **Smart inference** when percentages aren't explicitly stated
- ✅ **Single Message Delivery**: Always fits in one email
- ✅ **Prioritized Events**: Shows most significant weather conditions first

### Weather Event Detection:
- **Rain/Precipitation**: Rain, showers, drizzle, sprinkles
- **Snow**: Snow, blizzard, flurries, snowfall
- **Sleet/Freezing Rain**: Sleet, freezing rain, ice, icy
- **Wind**: Windy, gusts, high wind, breezy
- **Thunderstorms**: Thunderstorm, t-storm, severe thunderstorm
- **Fog**: Fog, foggy, haze, mist, dense fog, patchy fog
- **Extreme Events**: Blizzard, ice storm, tornado, hurricane, severe thunderstorm, high wind warning, flood warning, dense fog

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

### Multi-Region Examples:
- **Fairbanks, AK:** `Ton:Rain(80%),Thunderstorm(80%),Fog(80%) | Tue:Rain(50%),Fog(50%) | Tue:Rain(50%),Fog(50%) | Wed:Rain(60%),Thunderstorm(60%),Fog(60%) | Wed:Rain(60%),Thunderstorm(60%)`
- **Miami, FL:** `Ton:Rain(30%),Thunderstorm(30%) | Tue:Rain(30%),Wind(80%),Thunderstorm(30%) | Tue:Rain(30%),Thunderstorm(30%) | Wed:Rain(70%),Thunderstorm(70%) | Wed:Rain(30%),Thunderstorm(30%)`
- **Los Angeles, CA:** `Ton:Fog(60%),Patchyfog(60%) | Tue:Fog(60%),Patchyfog(60%) | Tue:Fog(60%),Patchyfog(60%) | Wed:Fog(60%),Patchyfog(60%) | Wed:Fog(60%),Patchyfog(60%) | Thu:Fog(60%),Patchyfog(60%)`

---

## 📋 COMPACT Format

**Purpose:** Brief weather summary with event indicators for each time period  
**Best for:** Users who want a quick overview with weather event highlights  
**Length:** 400-1000 characters  
**Parts:** 2-5 emails (ZOLEO device)

### Example Output:
```
Tonight: Rain, Thunderstorm | Showers and possibly a thunderstorm before 10pm, then showers likely | Tuesday: Rain | Scattered showers | Tuesday Night: Rain | Scattered showers | Wednesday: Rain, Thunderstorm | Showers likely, with thunderstorms also possible after 10am
```

### What the user receives:

**Email 1/2:**
```
Subject: NOAA Forecast Update (1/2)
Body: (1/2) Tonight: Rain, Thunderstorm | Showers and possibly a thunderstorm before 10pm, then showers likely | Tuesday: Rain | Scattered showers | Tuesday Night: Rain | Scattered showers | Wednesday: Rain, Thunderstorm | Showers likely, with thunderstorms also possible after 10am | Thur
```

**Email 2/2:**
```
Subject: NOAA Forecast Update (2/2)
Body: (2/2) sday Night: Rain, Thunderstorm | Scattered showers and thunderstorms | Friday: Rain, Thunderstorm | Isolated showers, with thunderstorms also possible after 4pm | Friday Night: Rain, Thunderstorm | Isolated showers and thunderstorms | Saturday: Rain, Thunderstorm | Isolated showers and thunderstorms | Saturday Night: Rain, Thunderstorm | Scattered showers and thunderstorms | Sunday: Rain | Scattered showers
```

### Key Features:
- ✅ **Weather Event Indicators**: Shows detected weather events as prefixes
- ✅ **Extreme Event Highlighting**: 🚨 for extreme events
- ✅ Uses pipe separators for easy reading
- ✅ Includes temperature information (Hi/Lo)
- ✅ Converts precipitation percentages to readable format
- ✅ Takes first sentence of each forecast
- ✅ **Enhanced Detection**: Same logic as Summary format
- ✅ **Fog Detection**: Properly identifies fog, patchy fog, haze, mist

### Event Indicator Examples:
- `Tonight: Rain, Thunderstorm | [forecast text]`
- `Wednesday: 🚨Blizzard, Snow | [forecast text]`
- `Friday: Wind | [forecast text]`
- `Tuesday: Fog, Patchy Fog | [forecast text]`

---

## 📄 FULL Format

**Purpose:** Complete detailed forecast information  
**Best for:** Users who want comprehensive weather details  
**Length:** 1100-2000+ characters  
**Parts:** 6+ emails (ZOLEO device)

### Example Output:
```
Tonight: Scattered showers.  Mostly cloudy, with a low around 40. Southwest wind around 5 mph becoming calm.  Chance of precipitation is 40%.
Tuesday: Scattered showers.  Partly sunny, with a high near 51. Calm wind becoming south around 5 mph.  Chance of precipitation is 40%.
Tuesday Night: Scattered showers.  Mostly cloudy, with a low around 42. South wind around 5 mph.  Chance of precipitation is 50%.
Wednesday: Scattered showers.  Cloudy, with a high near 52. South wind 5 to 10 mph.  Chance of precipitation is 50%.
Wednesday Night: A chance of rain.  Mostly cloudy, with a low around 41. Southeast wind around 10 mph.  Chance of precipitation is 40%.
Thursday: A chance of rain.  Cloudy, with a high near 52. Chance of precipitation is 50%.
Thursday Night: A chance of rain.  Cloudy, with a low around 42.
Friday: A chance of rain.  Cloudy, with a high near 54.
Friday Night: A chance of rain.  Cloudy, with a low around 42.
Saturday: A chance of rain.  Cloudy, with a high near 54.
Saturday Night: A chance of rain.  Cloudy, with a low around 43.
Sunday: Rain likely.  Cloudy, with a high near 52.
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
| **SUMMARY** | 80-150 chars | 1 | Time-Based Weather Events + Probabilities | Quick planning around significant weather |
| **COMPACT** | 400-1000 chars | 2-5 | Quick Overview + Event Indicators | General weather awareness with highlights |
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

### Choose COMPACT if:
- You want a quick weather overview
- You need temperature information
- You want a balance of detail and brevity
- You're checking general conditions
- You want weather event indicators
- You prefer pipe-separated format
- You want to see forecast descriptions

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
- **Extreme Event Detection**: Blizzard, ice storm, tornado, hurricane, severe thunderstorm, high wind warning, flood warning, dense fog
- **Smart Inference**: Provides meaningful percentages when NOAA doesn't specify them
- **Visual Highlighting**: Extreme events marked with 🚨

### Multi-Region Testing
The system has been tested across diverse weather conditions:

- **Alaska (Fairbanks)**: Summer conditions with rain, thunderstorms, fog, wildfire smoke
- **Alaska (Anchorage)**: Coastal conditions with rain, fog, moderate temperatures
- **Florida (Miami)**: Hurricane season with wind, rain, thunderstorms
- **Illinois (Chicago)**: Spring conditions with rain, thunderstorms
- **Massachusetts (Boston)**: Summer heat wave with rain, thunderstorms
- **California (Los Angeles)**: Spring conditions with fog, patchy fog

This provides much more actionable information for users planning outdoor activities across all seasons and weather conditions, with the Summary format now being the most efficient for single-message delivery. 