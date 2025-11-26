import logging
import re
from typing import Any, Dict, List, Optional

_LOGGER = logging.getLogger(__name__)

# Define weather event types and their keywords at module level
event_types = {
    "rain": ["rain", "showers", "precipitation", "drizzle", "sprinkles"],
    "snow": ["snow", "blizzard", "flurries", "snowfall"],
    "sleet": ["sleet"],
    "freezing rain": ["freezing rain", "ice", "icy"],
    "wind": ["windy", "gusts", "high wind", "breezy"],
    "hail": ["hail"],
    "thunderstorm": ["thunderstorm", "thunderstorms", "t-storm", "tstorms"],
    "smoke": [
        "smoke",
        "smoky",
        "wildfire smoke",
        "fire smoke",
        "smoke from fires",
        "smoke conditions",
        "smoke warning",
        "areas of smoke",
        "widespread haze",
    ],
    "fog": ["fog", "foggy", "mist"],
    "dense fog": ["dense fog", "thick fog", "heavy fog"],
    "patchy fog": ["patchy fog"],
    "tornado": ["tornado"],
    "hurricane": ["hurricane", "tropical storm"],
    "blizzard": ["blizzard"],
    "ice storm": ["ice storm"],
    "severe thunderstorm": ["severe thunderstorm", "severe t-storm", "severe tstorm"],
    "high wind warning": ["high wind warning"],
    "flood warning": ["flood warning", "flash flood warning"],
}

# Define event name mapping at module level
event_name_map = {
    "rain": "Rn",
    "snow": "Snw",
    "sleet": "Slt",
    "freezing rain": "FzRn",
    "wind": "Wnd",
    "hail": "Hl",
    "thunderstorm": "ThSt",
    "smoke": "Smk",
    "fog": "Fg",
    "dense fog": "DFg",
    "patchy fog": "PFg",
    "tornado": "TOR",
    "hurricane": "HUR",
    "blizzard": "BLZ",
    "ice storm": "ISt",
    "severe thunderstorm": "SThSt",
    "high wind warning": "HiWW",
    "flood warning": "FldWng",
}


# Define valid period names including holidays
VALID_PERIOD_NAMES = [
    "This Afternoon",
    "Today",
    "Tonight",
    "Overnight",
    "Monday",
    "Monday Night",
    "Tuesday",
    "Tuesday Night",
    "Wednesday",
    "Wednesday Night",
    "Thursday",
    "Thursday Night",
    "Friday",
    "Friday Night",
    "Saturday",
    "Saturday Night",
    "Sunday",
    "Sunday Night",
    # Holidays
    "New Year's Day",
    "Martin Luther King Jr. Day",
    "M.L. King Day",
    "Washington's Birthday",
    "Presidents' Day",
    "Memorial Day",
    "Juneteenth",
    "Independence Day",
    "Labor Day",
    "Columbus Day",
    "Veterans Day",
    "Thanksgiving Day",
    "Christmas Day",
]


def format_forecast(
    forecast_text: str, mode: str = "summary", days: Optional[int] = None
) -> str:
    _LOGGER.debug(
        "Formatting forecast with mode: %s, days: %s, input length: %d characters",
        mode,
        days,
        len(forecast_text),
    )

    if mode == "full":
        result = format_full_forecast(forecast_text)
    elif mode == "compact":
        result = format_compact_forecast(forecast_text)
    elif mode == "summary":
        result = summarize_forecast(forecast_text, days)
    else:
        result = forecast_text[:1000]
        _LOGGER.debug("Unknown mode '%s', using truncated original", mode)

    _LOGGER.debug(
        "Forecast formatting completed, output length: %d characters", len(result)
    )
    return result


def clean_forecast_text(text: str) -> str:
    """Clean and format the raw forecast text."""
    _LOGGER.debug("Cleaning forecast text, input length: %d characters", len(text))

    # Ensure every period label starts on a new line (except at the start)
    period_labels = [label + ":" for label in VALID_PERIOD_NAMES]

    # Insert newline before each period label (except at the start of the text)
    for label in period_labels:
        # Replace any occurrence of the label (not at the start) with newline + label
        text = re.sub(r"(?<!^)(?<!\n)\s*" + re.escape(label), r"\n" + label, text)

    # Split by periods and clean up
    lines = text.strip().splitlines()
    _LOGGER.debug("Split into %d lines", len(lines))

    cleaned_lines = []

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # Handle the case where periods are concatenated
        if ":" in line:
            # Split by common period patterns
            # Create a regex pattern from VALID_PERIOD_NAMES
            period_pattern = "|".join(
                [re.escape(name + ":") for name in VALID_PERIOD_NAMES]
            )
            parts = re.split(f"({period_pattern})", line)

            current_period = ""
            for part in parts:
                part = part.strip()
                if part.endswith(":") and any(
                    day in part for day in VALID_PERIOD_NAMES
                ):
                    current_period = part
                elif part and current_period:
                    # Don't add extra space if the part already starts with a space
                    if part.startswith(" "):
                        cleaned_lines.append(f"{current_period}{part}")
                    else:
                        cleaned_lines.append(f"{current_period} {part}")
                    current_period = ""
        else:
            cleaned_lines.append(line)

    result = "\n".join(cleaned_lines)
    _LOGGER.debug("Cleaned forecast text, output length: %d characters", len(result))
    return result


def normalize_spaces(text: str) -> str:
    """Normalize spaces in text - replace multiple spaces with single spaces."""
    # Replace multiple spaces with single spaces
    text = re.sub(r" +", " ", text)
    # Ensure proper spacing after periods (single space)
    text = re.sub(r"\. +", ". ", text)
    return text


def format_full_forecast(text: str) -> str:
    """Format the full forecast with proper line breaks and better character utilization."""
    _LOGGER.debug("Formatting full forecast")
    cleaned_text = clean_forecast_text(text)
    lines = cleaned_text.strip().splitlines()
    formatted_lines = []

    for line in lines:
        line = line.strip()
        if ":" in line and any(day in line for day in VALID_PERIOD_NAMES):
            # Normalize spaces in the line
            line = normalize_spaces(line)
            formatted_lines.append(line)

    result = "\n".join(formatted_lines)

    # If result is longer than 2000 chars, truncate at a complete sentence
    if len(result) > 2000:
        # Try to find a good break point near 2000 characters
        truncated = result[:2000]
        # Look for the last complete sentence
        last_period = truncated.rfind(".")
        last_newline = truncated.rfind("\n")
        break_point = max(last_period, last_newline)

        if break_point > 1800:  # Only use if we have a reasonable break point
            result = result[: break_point + 1]
        else:
            result = result[:2000] + "..."

    _LOGGER.debug("Full forecast formatted, result length: %d characters", len(result))
    return result


def infer_chance(event: str, forecast_text: str) -> int:
    """Infer probability percentage for weather events, prioritizing explicit percentages when available."""
    forecast_lower = forecast_text.lower()

    # First check for explicit percentages in the entire forecast text
    # Look for "Chance of precipitation is X%" pattern first - ONLY for rain events
    precip_chance_match = re.search(
        r"chance of precipitation is (\d+)%", forecast_lower
    )
    if precip_chance_match and event == "rain":
        return int(precip_chance_match.group(1))

    # For non-rain events, look for percentages that are specifically associated with that event
    if event != "rain":
        # Look for event-specific percentage patterns
        event_keywords = event_types.get(event, [])
        for keyword in event_keywords:
            # Look for patterns like "chance of smoke", "smoke chance", etc.
            event_chance_patterns = [
                rf"chance of {keyword}[^.]*(\d+)%",
                rf"{keyword} chance[^.]*(\d+)%",
                rf"(\d+)% chance of {keyword}",
                rf"(\d+)% {keyword}",
            ]

            for pattern in event_chance_patterns:
                match = re.search(pattern, forecast_lower)
                if match:
                    return int(match.group(1))

    # Look for other explicit percentage patterns - but be more careful about context
    percent_patterns = [
        r"(\d+)\s*percent[^.]*",  # "20 percent" format
        r"(\d+)%[^.]*",  # "20%" format
    ]

    for pattern in percent_patterns:
        matches = re.findall(pattern, forecast_text, re.IGNORECASE)
        for match in matches:
            if not match:
                continue
            # Handle different match types from re.findall
            if isinstance(match, tuple):
                match_str = str(match[0])
            else:
                match_str = str(match)
            percent_val = int(match_str)
            # Check if this percentage is associated with the current event
            # Look for the percentage in context with weather keywords
            context_start = max(0, forecast_text.lower().find(match_str) - 100)
            context_end = min(
                len(forecast_text), forecast_text.lower().find(match_str) + 100
            )
            context = forecast_text[context_start:context_end].lower()

            # Check if the event keywords are in the same context as the percentage
            event_keywords = event_types.get(event, [])
            if any(kw in context for kw in event_keywords):
                # Additional check: make sure this percentage isn't from precipitation
                if "precipitation" not in context or event == "rain":
                    return percent_val

    # Then infer based on keywords
    if event == "rain":
        if "rain likely" in forecast_lower or "showers likely" in forecast_lower:
            return 70
        elif "scattered" in forecast_lower:
            return 40
        elif "isolated" in forecast_lower:
            return 20
        elif "chance" in forecast_lower:
            return 30
        elif "drizzle" in forecast_lower or "sprinkles" in forecast_lower:
            return 25
        else:
            return 50
    elif event == "snow":
        if "blizzard" in forecast_lower:
            return 90
        elif "snow likely" in forecast_lower or "heavy snow" in forecast_lower:
            return 70
        elif "flurries" in forecast_lower:
            return 30
        elif "chance" in forecast_lower:
            return 30
        else:
            return 50
    elif event == "sleet" or event == "freezing rain":
        if "likely" in forecast_lower:
            return 60
        elif "chance" in forecast_lower:
            return 30
        else:
            return 40
    elif event == "wind":
        if "high wind" in forecast_lower or "gusts" in forecast_lower:
            return 80
        elif "windy" in forecast_lower:
            return 60
        elif "breezy" in forecast_lower:
            return 40
        else:
            return 30
    elif event == "hail":
        if "likely" in forecast_lower:
            return 60
        elif "chance" in forecast_lower:
            return 30
        else:
            return 40
    elif event == "thunderstorm":
        if "severe" in forecast_lower:
            return 80
        elif "likely" in forecast_lower:
            return 60
        elif "chance" in forecast_lower:
            return 30
        else:
            return 50
    elif event == "fog":
        if (
            "dense fog" in forecast_lower
            or "thick fog" in forecast_lower
            or "heavy fog" in forecast_lower
        ):
            return 90
        elif "patchy fog" in forecast_lower:
            return 60
        elif "fog" in forecast_lower or "foggy" in forecast_lower:
            return 70
        elif "mist" in forecast_lower:
            return 30
        else:
            return 50
    elif event == "smoke":
        if (
            "heavy smoke" in forecast_lower
            or "thick smoke" in forecast_lower
            or "dense smoke" in forecast_lower
        ):
            return 90
        elif "wildfire smoke" in forecast_lower or "fire smoke" in forecast_lower:
            return 75
        elif "smoke" in forecast_lower or "smoky" in forecast_lower:
            return 65
        else:
            return 50
    elif event == "dense fog":
        return 90
    elif event == "patchy fog":
        return 60
    elif event in [
        "tornado",
        "hurricane",
        "blizzard",
        "ice storm",
        "severe thunderstorm",
        "high wind warning",
        "flood warning",
    ]:
        return 90
    return 0


def check_significant_wind(forecast_text: str) -> bool:
    """Check if wind speeds are significant (15+ mph) to warrant a wind event."""
    forecast_lower = forecast_text.lower()

    # Look for wind speed patterns
    wind_patterns = [
        r"(\d+) to (\d+) mph",  # Range like "15 to 25 mph"
        r"(\d+) mph",  # Single speed like "20 mph"
        r"gusts (?:up to|as high as|to) (\d+) mph",  # Gusts
        r"wind (\d+) to (\d+) mph",
        r"wind (\d+) mph",
    ]

    for pattern in wind_patterns:
        matches = re.findall(pattern, forecast_lower)
        for match in matches:
            if len(match) == 2:  # Range
                try:
                    min_speed = int(match[0])
                    max_speed = int(match[1])
                    if min_speed >= 15 or max_speed >= 15:
                        return True
                except ValueError:
                    continue
            elif len(match) == 1:  # Single speed
                try:
                    speed = int(match[0])
                    if speed >= 15:
                        return True
                except ValueError:
                    continue

    return False


def extract_temperature_info(forecast_text: str) -> List[str]:
    """Extracts high and low temperature, returning a list."""
    temps = []
    high_match = re.search(r"high (?:near|around) (\d+)", forecast_text, re.IGNORECASE)
    if high_match:
        temps.append(f"H:{high_match.group(1)}°")

    low_match = re.search(r"low (?:around|near) (\d+)", forecast_text, re.IGNORECASE)
    if low_match:
        temps.append(f"L:{low_match.group(1)}°")

    return temps


def get_abbr(direction_word: str) -> str:
    # Expanded abbreviations
    mapping = {
        "north": "N",
        "east": "E",
        "south": "S",
        "west": "W",
        "northeast": "NE",
        "southeast": "SE",
        "southwest": "SW",
        "northwest": "NW",
        "north northeast": "NNE",
        "east northeast": "ENE",
        "east southeast": "ESE",
        "south southeast": "SSE",
        "south southwest": "SSW",
        "west southwest": "WSW",
        "west northwest": "WNW",
        "north northwest": "NNW",
    }
    return mapping.get(direction_word.lower(), direction_word)


def extract_wind_info(forecast_text: str) -> List[str]:
    """Extracts wind direction and speed, supporting various formats including gusts."""
    # Pattern for direction and speed, with optional gusts
    patterns = [
        r"(\b(?:north|south|east|west|northeast|southeast|southwest|northwest|north northeast|east northeast|east southeast|south southeast|south southwest|west southwest|west northwest|north northwest)\b) wind (\d+ to \d+|\d+) mph(?:, with gusts as high as (\d+) mph)?",
        r"wind (\d+ to \d+|\d+) mph from the (\b(?:north|south|east|west|northeast|southeast|southwest|northwest|north northeast|east northeast|east southeast|south southeast|south southwest|west southwest|west northwest|north northwest)\b)",
        r"(\b(?:north|south|east|west|northeast|southeast|southwest|northwest|north northeast|east northeast|east southeast|south southeast|south southwest|west southwest|west northwest|north northwest)\b) wind around (\d+) mph",
        r"becoming (\b(?:north|south|east|west|northeast|southeast|southwest|northwest)\b) (\d+ to \d+|\d+) mph",
    ]

    for pattern in patterns:
        match = re.search(pattern, forecast_text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if "from the" in pattern:
                direction, speed = get_abbr(groups[1]), groups[0].replace(" to ", "-")
                return [f"{direction}{speed}mph"]
            if "becoming" in pattern:
                direction, speed = get_abbr(groups[0]), groups[1].replace(" to ", "-")
                return [f"{direction}{speed}mph"]

            direction, speed = get_abbr(groups[0]), groups[1].replace(" to ", "-")
            gusts = groups[2] if len(groups) > 2 and groups[2] else None

            wind_str = f"{direction}{speed}mph"
            if gusts:
                wind_str += f" (G:{gusts}mph)"
            return [wind_str]
    return []


def format_compact_forecast(text: str) -> str:
    """Format a compact version of the forecast with enhanced weather detection."""
    _LOGGER.debug("Formatting compact forecast")
    cleaned_text = clean_forecast_text(text)
    lines = cleaned_text.strip().splitlines()
    result = []

    # List of extreme event keys
    extreme_events = [
        "blizzard",
        "ice storm",
        "tornado",
        "hurricane",
        "severe thunderstorm",
        "high wind warning",
        "flood warning",
        "dense fog",
        "smoke",
    ]

    for line in lines:
        if ":" in line and any(day in line for day in VALID_PERIOD_NAMES):
            try:
                day, forecast = line.split(":", 1)
                day = day.strip()
                if day == "This Afternoon":
                    day = "Afternoon"
                forecast = forecast.strip()

                # Detect significant weather events
                forecast_lower = forecast.lower()
                detected_events = []

                for event, keywords in event_types.items():
                    if any(kw in forecast_lower for kw in keywords):
                        # For wind events, only add if speeds are significant
                        if event == "wind" and not check_significant_wind(forecast):
                            continue
                        chance = infer_chance(event, forecast)
                        if chance > 0:
                            if event in extreme_events:
                                detected_events.append(f"🚨{event.title()}({chance}%)")
                            else:
                                detected_events.append(f"{event.title()}({chance}%)")

                # Extract temperature and wind info
                temp_info = extract_temperature_info(forecast)
                wind_info = extract_wind_info(forecast)

                # Make a clean version of the forecast for display
                display_forecast = forecast

                # Remove verbose weather details from the display version
                temp_patterns = [
                    r"with a high (?:near|around) \d+",
                    r"with a low (?:around|near) \d+",
                    r"a high (?:near|around) \d+",
                    r"a low (?:around|near) \d+",
                    r"high (?:near|around) \d+",
                    r"low (?:around|near) \d+",
                ]
                for pattern in temp_patterns:
                    display_forecast = re.sub(
                        pattern, "", display_forecast, flags=re.IGNORECASE
                    )

                wind_patterns = [
                    r"(\b(?:north|south|east|west|northeast|southeast|southwest|northwest|north northeast|east northeast|east southeast|south southeast|south southwest|west southwest|west northwest|north northwest)\b) wind (\d+ to \d+|\d+) mph(?:, with gusts as high as (\d+) mph)?",
                    r"wind (\d+ to \d+|\d+) mph from the (\b(?:north|south|east|west|northeast|southeast|southwest|northwest|north northeast|east northeast|east southeast|south southeast|south southwest|west southwest|west northwest|north northwest)\b)",
                    r"(\b(?:north|south|east|west|northeast|southeast|southwest|northwest|north northeast|east northeast|east southeast|south southeast|south southwest|west southwest|west northwest|north northwest)\b) wind around (\d+) mph",
                ]
                for pattern in wind_patterns:
                    display_forecast = re.sub(
                        pattern, "", display_forecast, flags=re.IGNORECASE
                    )

                # General cleanup
                display_forecast = re.sub(
                    r"Chance of precipitation is \d+%",
                    "",
                    display_forecast,
                    flags=re.IGNORECASE,
                )
                display_forecast = re.sub(r"\s+", " ", display_forecast).strip()
                display_forecast = (
                    display_forecast.replace(" ,", ",").replace(" .", ".").strip(" ,.")
                )
                if display_forecast.endswith(","):
                    display_forecast = display_forecast[:-1]

                # Take just the first sentence of the cleaned forecast
                first_sentence = (
                    display_forecast.split(".")[0]
                    if "." in display_forecast
                    else display_forecast
                )

                # Build details string
                details = []
                if temp_info:
                    for item in temp_info:
                        # Remove degree symbol for compact display
                        details.append(item.replace("°", ""))
                if wind_info:
                    details.extend(wind_info)

                details_str = f" ({', '.join(details)})" if details else ""

                # Add weather event indicators if detected
                if detected_events:
                    smoke_events = [
                        ev for ev in detected_events if ev.startswith("🚨Smoke(")
                    ]
                    if smoke_events:
                        events_str = ", ".join(smoke_events)
                        result.append(
                            f"{day.strip()}: {events_str}{details_str} - Smoke"
                        )
                    else:
                        events_str = ", ".join(detected_events)
                        result.append(
                            f"{day.strip()}: {events_str}{details_str} - {first_sentence}"
                        )
                else:
                    result.append(f"{day.strip()}: {first_sentence}{details_str}")

                _LOGGER.debug(
                    "Added compact forecast for %s: %s",
                    day.strip(),
                    (
                        first_sentence[:50] + "..."
                        if len(first_sentence) > 50
                        else first_sentence
                    ),
                )
            except ValueError:
                _LOGGER.debug("Failed to parse line for compact format: %s", line)
                continue

    # Use newlines between days for better readability instead of pipe separators
    final_result = "\n".join(result)[:1500]
    _LOGGER.debug(
        "Compact forecast formatted, result length: %d characters", len(final_result)
    )
    _LOGGER.debug("Compact forecast final result: %r", final_result)
    return final_result


def summarize_forecast(text: str, days: Optional[int] = None) -> str:
    """Summarize forecast text with weather events, temperatures, and wind info.

    Args:
        text: Raw forecast text
        days: Number of days to include (None for all available)
    """
    _LOGGER.debug("Creating forecast summary")
    cleaned_text = clean_forecast_text(text)
    lines = cleaned_text.strip().splitlines()

    # Define event types and their keywords
    event_types = {
        "rain": ["rain", "showers", "precipitation", "drizzle", "sprinkles"],
        "snow": ["snow", "blizzard", "flurries", "snowfall"],
        "sleet": ["sleet"],
        "freezing rain": ["freezing rain", "ice", "icy"],
        "wind": ["windy", "gusts", "high wind", "breezy"],
        "hail": ["hail"],
        "thunderstorm": ["thunderstorm", "thunderstorms", "t-storm", "tstorms"],
        "smoke": [
            "smoke",
            "smoky",
            "wildfire smoke",
            "fire smoke",
            "smoke from fires",
            "smoke conditions",
            "smoke warning",
            "areas of smoke",
            "widespread haze",
        ],
        "fog": ["fog", "foggy", "mist"],
        "dense fog": ["dense fog", "thick fog", "heavy fog"],
        "patchy fog": ["patchy fog"],
        "tornado": ["tornado"],
        "hurricane": ["hurricane", "tropical storm"],
        "blizzard": ["blizzard"],
        "ice storm": ["ice storm"],
        "severe thunderstorm": [
            "severe thunderstorm",
            "severe t-storm",
            "severe tstorm",
        ],
        "high wind warning": ["high wind warning"],
        "flood warning": ["flood warning", "flash flood warning"],
    }
    # List of extreme event keys
    extreme_events = [
        "blizzard",
        "ice storm",
        "tornado",
        "hurricane",
        "severe thunderstorm",
        "high wind warning",
        "flood warning",
        "dense fog",
        "smoke",
    ]

    def short_period(period: str) -> str:
        """Shorten period names for brevity"""
        period = period.strip()
        if period == "This Afternoon":
            return "Aft"
        elif period == "Today":
            return "Tdy"
        elif period == "Tonight":
            return "Tngt"
        elif period == "Overnight":
            return "ON"  # Overnight abbreviation, standard for forecasts
        elif period == "Monday":
            return "Mon"
        elif period == "Tuesday":
            return "Tue"
        elif period == "Wednesday":
            return "Wed"
        elif period == "Thursday":
            return "Thu"
        elif period == "Friday":
            return "Fri"
        elif period == "Saturday":
            return "Sat"
        elif period == "Sunday":
            return "Sun"
        else:
            return period[:3]

    def extract_temperature_info(forecast_text: str) -> List[str]:
        """Extract high and low temperature information from forecast text."""
        temp_info = []

        # Look for high temperature patterns
        high_patterns = [
            r"with a high near (\d+)",
            r"high near (\d+)",
            r"high of (\d+)",
            r"high (\d+)",
            r"temperature near (\d+)",
        ]

        # Look for low temperature patterns
        low_patterns = [
            r"with a low around (\d+)",
            r"low around (\d+)",
            r"low of (\d+)",
            r"low (\d+)",
            r"temperature around (\d+)",
        ]

        for pattern in high_patterns:
            match = re.search(pattern, forecast_text.lower())
            if match:
                temp_info.append(f"H:{match.group(1)}°")
                break

        for pattern in low_patterns:
            match = re.search(pattern, forecast_text.lower())
            if match:
                temp_info.append(f"L:{match.group(1)}°")
                break

        return temp_info

    def extract_wind_info(forecast_text: str) -> List[str]:
        """Extract wind direction and speed information from forecast text."""

        direction_map = {
            "north": "N",
            "northeast": "NE",
            "east": "E",
            "southeast": "SE",
            "south": "S",
            "southwest": "SW",
            "west": "W",
            "northwest": "NW",
            "variable": "VAR",
        }

        def get_abbr(direction_word: str) -> str:
            return direction_map.get(direction_word.lower(), direction_word.title()[:1])

        forecast_lower = forecast_text.lower()

        # Special handling for 'becoming' phrases
        if "becoming" in forecast_lower:
            after_becoming = forecast_lower.split("becoming", 1)[1].strip()
            wind_patterns = [
                r"(\w+)\s+(\d+) to (\d+) mph",  # direction followed by range
                r"(\w+) wind (\d+) to (\d+) mph",
                r"wind (\w+) (\d+) to (\d+) mph",
                r"(\w+) wind (?:around|near|up to|to) (\d+) mph",
                r"wind (?:from the )?(\w+) (?:around|near|up to|to) (\d+) mph",
                r"(\w+) wind (\d+) mph",
                r"wind (\w+) (\d+) mph",
                r"(\w+) (?:around|near|up to|to) (\d+) mph",  # direction around speed mph
                r"(\d+) to (\d+) mph(?:\W|$)",  # just a range with no direction, allow trailing words
                r"(\w+)",  # just direction
            ]
            for pattern in wind_patterns:
                match = re.search(pattern, after_becoming)
                if match:
                    if len(match.groups()) == 3:
                        direction = get_abbr(match.group(1))
                        speed_min = match.group(2)
                        speed_max = match.group(3)
                        return [f"{direction}{speed_min}-{speed_max}mph"]
                    elif len(match.groups()) == 2:
                        # If it's just a range with no direction
                        if pattern == r"(\d+) to (\d+) mph":
                            speed_min = match.group(1)
                            speed_max = match.group(2)
                            return [f"{speed_min}-{speed_max}mph"]
                        direction = get_abbr(match.group(1))
                        speed = match.group(2)
                        return [f"{direction}{speed}mph"]
                    elif len(match.groups()) == 1:
                        direction_word = match.group(1).lower()
                        if direction_word == "calm":
                            return ["Calm"]
                        if direction_word == "light":
                            return ["Light"]
                        direction = get_abbr(direction_word)
                        return [f"{direction}wind"]
            if "calm" in after_becoming:
                return ["Calm"]
            if "light" in after_becoming:
                return ["Light"]
            return []

        # Otherwise, extract the first matching wind pattern
        wind_patterns = [
            r"(\w+) wind (\d+) to (\d+) mph",
            r"wind (\w+) (\d+) to (\d+) mph",
            r"(\w+) wind (?:around|near|up to|to) (\d+) mph",
            r"wind (?:from the )?(\w+) (?:around|near|up to|to) (\d+) mph",
            r"(\w+) wind (\d+) mph",
            r"wind (\w+) (\d+) mph",
            r"(\w+) (?:around|near|up to|to) (\d+) mph",  # direction around speed mph
            r"(\w+)wind",
            r"(\w+) wind",
        ]
        for pattern in wind_patterns:
            match = re.search(pattern, forecast_lower)
            if match:
                if len(match.groups()) == 3:
                    direction = get_abbr(match.group(1))
                    speed_min = match.group(2)
                    speed_max = match.group(3)
                    return [f"{direction}{speed_min}-{speed_max}mph"]
                elif len(match.groups()) == 2:
                    direction = get_abbr(match.group(1))
                    speed = match.group(2)
                    return [f"{direction}{speed}mph"]
                elif len(match.groups()) == 1:
                    direction_word = match.group(1).lower()
                    if direction_word == "calm":
                        return ["Calm"]
                    if direction_word == "light":
                        return ["Light"]
                    direction = get_abbr(direction_word)
                    return [f"{direction}wind"]

        if "calm wind" in forecast_lower or "calm" in forecast_lower:
            return ["Calm"]
        elif "light wind" in forecast_lower:
            return ["Light"]

        return []

    def infer_chance(event: str, forecast_text: str) -> int:
        """Infer probability percentage for weather events, prioritizing explicit percentages when available."""
        forecast_lower = forecast_text.lower()

        # First check for explicit percentages in the entire forecast text
        # Look for "Chance of precipitation is X%" pattern first - ONLY for rain events
        precip_chance_match = re.search(
            r"chance of precipitation is (\d+)%", forecast_lower
        )
        if precip_chance_match and event == "rain":
            return int(precip_chance_match.group(1))

        # For non-rain events, look for percentages that are specifically associated with that event
        if event != "rain":
            # Look for event-specific percentage patterns
            event_keywords = event_types.get(event, [])
            for keyword in event_keywords:
                # Look for patterns like "chance of smoke", "smoke chance", etc.
                event_chance_patterns = [
                    rf"chance of {keyword}[^.]*(\d+)%",
                    rf"{keyword} chance[^.]*(\d+)%",
                    rf"(\d+)% chance of {keyword}",
                    rf"(\d+)% {keyword}",
                ]

                for pattern in event_chance_patterns:
                    match = re.search(pattern, forecast_lower)
                    if match:
                        return int(match.group(1))

        # Look for other explicit percentage patterns - but be more careful about context
        percent_patterns = [
            r"(\d+)\s*percent[^.]*",  # "20 percent" format
            r"(\d+)%[^.]*",  # "20%" format
        ]

        for pattern in percent_patterns:
            matches = re.findall(pattern, forecast_text, re.IGNORECASE)
            for match in matches:
                if not match:
                    continue
                # Handle different match types from re.findall
                # re.findall returns strings when pattern has one group
                match_str = (
                    str(match) if not isinstance(match, tuple) else str(match[0])
                )
                percent_val = int(match_str)
                # Check if this percentage is associated with the current event
                # Look for the percentage in context with weather keywords
                context_start = max(0, forecast_text.lower().find(match_str) - 100)
                context_end = min(
                    len(forecast_text), forecast_text.lower().find(match_str) + 100
                )
                context = forecast_text[context_start:context_end].lower()

                # Check if the event keywords are in the same context as the percentage
                event_keywords = event_types.get(event, [])
                if any(kw in context for kw in event_keywords):
                    # Additional check: make sure this percentage isn't from precipitation
                    if "precipitation" not in context or event == "rain":
                        return percent_val

        # Then infer based on keywords
        if event == "rain":
            if "rain likely" in forecast_lower or "showers likely" in forecast_lower:
                return 70
            elif "scattered" in forecast_lower:
                return 40
            elif "isolated" in forecast_lower:
                return 20
            elif "chance" in forecast_lower:
                return 30
            elif "drizzle" in forecast_lower or "sprinkles" in forecast_lower:
                return 25
            else:
                return 50
        elif event == "snow":
            if "blizzard" in forecast_lower:
                return 90
            elif "snow likely" in forecast_lower or "heavy snow" in forecast_lower:
                return 70
            elif "flurries" in forecast_lower:
                return 30
            elif "chance" in forecast_lower:
                return 30
            else:
                return 50
        elif event == "sleet" or event == "freezing rain":
            if "likely" in forecast_lower:
                return 60
            elif "chance" in forecast_lower:
                return 30
            else:
                return 40
        elif event == "wind":
            if "high wind" in forecast_lower or "gusts" in forecast_lower:
                return 80
            elif "windy" in forecast_lower:
                return 60
            elif "breezy" in forecast_lower:
                return 40
            else:
                return 30
        elif event == "hail":
            if "likely" in forecast_lower:
                return 60
            elif "chance" in forecast_lower:
                return 30
            else:
                return 40
        elif event == "thunderstorm":
            if "severe" in forecast_lower:
                return 80
            elif "likely" in forecast_lower:
                return 60
            elif "chance" in forecast_lower:
                return 30
            else:
                return 50
        elif event == "fog":
            if (
                "dense fog" in forecast_lower
                or "thick fog" in forecast_lower
                or "heavy fog" in forecast_lower
            ):
                return 90
            elif "patchy fog" in forecast_lower:
                return 60
            elif "fog" in forecast_lower or "foggy" in forecast_lower:
                return 70
            elif "mist" in forecast_lower:
                return 30
            else:
                return 50
        elif event == "smoke":
            if (
                "heavy smoke" in forecast_lower
                or "thick smoke" in forecast_lower
                or "dense smoke" in forecast_lower
            ):
                return 90
            elif "wildfire smoke" in forecast_lower or "fire smoke" in forecast_lower:
                return 75
            elif "smoke" in forecast_lower or "smoky" in forecast_lower:
                return 65
            else:
                return 50
        elif event == "dense fog":
            return 90
        elif event == "patchy fog":
            return 60
        elif event in [
            "tornado",
            "hurricane",
            "blizzard",
            "ice storm",
            "severe thunderstorm",
            "high wind warning",
            "flood warning",
        ]:
            return 90
        return 0

    # Dictionary to store events by period (consolidating day/night)
    period_events_dict: Dict[str, List[str]] = {}

    event_name_map = {
        "rain": "Rn",
        "snow": "Snw",
        "sleet": "Slt",
        "freezing rain": "FzRn",
        "wind": "Wnd",
        "hail": "Hl",
        "thunderstorm": "ThSt",
        "smoke": "Smk",
        "fog": "Fg",
        "dense fog": "DFg",
        "patchy fog": "PFg",
        "tornado": "TOR",
        "hurricane": "HUR",
        "blizzard": "BLZ",
        "ice storm": "ISt",
        "severe thunderstorm": "SThSt",
        "high wind warning": "HiWW",
        "flood warning": "FldWng",
    }

    # Track day grouping
    current_day_index = 0
    is_previous_night = False
    day_display_names = {}  # Map index to display name

    # Filter and parse lines first to handle indexing correctly
    parsed_periods = []
    for line in lines:
        if ":" in line and any(day in line for day in VALID_PERIOD_NAMES):
            try:
                period, forecast = line.split(":", 1)
                parsed_periods.append((period.strip(), forecast.strip()))
            except ValueError:
                continue

    for i, (period, forecast) in enumerate(parsed_periods):
        forecast = forecast.lower()
        detected = []

        # Determine is_daytime
        is_daytime = True
        if "Night" in period or period in ["Tonight", "Overnight"]:
            is_daytime = False

        # Check for Day/Night transition
        if i > 0 and is_daytime and is_previous_night:
            current_day_index += 1

        is_previous_night = not is_daytime

        # Determine display name for this day index
        if current_day_index not in day_display_names:
            # Use the current period name to generate the short name
            # If it's a night period (e.g. Tonight), it will be the name
            # If it's a day period (e.g. Thanksgiving Day), it will be the name
            base_name = period

            # Special handling: "This Afternoon" on day 0 should be "Today"
            if current_day_index == 0 and base_name == "This Afternoon":
                base_name = "Today"

            if "Night" in base_name and base_name not in ["Tonight", "Overnight"]:
                base_name = base_name.replace(" Night", "")
            day_display_names[current_day_index] = short_period(base_name)

        short_period_name = day_display_names[current_day_index]

        # Extract weather events
        for event, keywords in event_types.items():
            if any(kw in forecast for kw in keywords):
                # For wind events, only add if speeds are significant
                if event == "wind" and not check_significant_wind(forecast):
                    continue

                chance = infer_chance(event, forecast)
                if chance > 0:
                    # Format event with proper capitalization and probability
                    event_name = event_name_map.get(
                        event, event.replace(" ", "").title()[:2]
                    )
                    if event in extreme_events:
                        detected.append(f"🚨{event_name}({chance}%)")
                    else:
                        detected.append(f"{event_name}({chance}%)")

        # Extract temperature and wind information
        temp_info = extract_temperature_info(forecast)
        wind_info = extract_wind_info(forecast)

        # Combine all information
        all_info = detected + temp_info + wind_info

        if all_info:
            # If we already have events for this period, merge them
            if short_period_name in period_events_dict:
                existing_events = period_events_dict[short_period_name]
                # Merge events, keeping the highest probability for duplicates
                for new_event in all_info:
                    if "(" in new_event and ")" in new_event:
                        # Event with probability
                        event_name = new_event.split("(")[0]
                        new_prob = int(new_event.split("(")[1].split("%")[0])

                        # Check if we already have this event
                        found = False
                        for i, existing_event in enumerate(existing_events):
                            if existing_event.split("(")[0] == event_name:
                                existing_prob = int(
                                    existing_event.split("(")[1].split("%")[0]
                                )
                                # Keep the higher probability
                                if new_prob > existing_prob:
                                    existing_events[i] = new_event
                                found = True
                                break

                        if not found:
                            existing_events.append(new_event)
                    else:
                        # For events without probabilities, just add if not already present
                        if new_event not in existing_events:
                            existing_events.append(new_event)
            else:
                period_events_dict[short_period_name] = all_info

    # Convert dictionary to list format with pipe separators for better character utilization
    period_events = []
    for period, events in period_events_dict.items():
        if events:
            period_events.append(f"{period}: {','.join(events)}")

    # Join period events with newlines for better readability
    summary = "\n".join(period_events)

    if not summary:
        summary = "No significant weather expected."

    _LOGGER.debug(
        f"Summary created with {len(period_events)} periods, days limit was {days}"
    )
    return summary


def get_email_body_from_subject(subject: str) -> str:
    """
    Parses an email subject to extract the email body (coordinates and format).
    Example subjects:
    - "61.408,-148.444"
    - "61.408, -148.444"
    - "61.408, -148.444 summary"
    - "61.408, -148.444 compact"
    - "61.408, -148.444 full"
    """
    _LOGGER.debug("Parsing email subject: %s", subject)
    # Regex to find coordinates and an optional format keyword
    # It looks for two numbers (latitude and longitude) separated by a comma,
    # and an optional word (summary, compact, full) at the end.
    match = re.search(r"(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*(\w+)?", subject)

    if match:
        lat, lon, fmt = match.groups()
        if fmt:
            result = f"{lat},{lon} {fmt}"
        else:
            result = f"{lat},{lon}"
        _LOGGER.debug("Parsed subject to: %s", result)
        return result

    # Return empty string if no match found
    _LOGGER.debug("No coordinates found in subject")
    return ""


def parse_forecast_periods(
    html_content: str, days_limit: int = 7
) -> List[Dict[str, Any]]:
    """Parse forecast periods from HTML content with days limit.

    Args:
        html_content: HTML content from NWS forecast page
        days_limit: Number of days to include:
            - 0: Only current day (day 0)
            - 1: Current day + next full day (day 0 + day 1)
            - 2: Current day + next 2 full days (day 0 + day 1 + day 2)
            - etc.
    """
    _LOGGER.debug(f"Parsing forecast periods with days_limit={days_limit}")

    # Find all <table> tags
    tables = re.findall(
        r"<table[\s\S]*?>[\s\S]*?<\/table>", html_content, re.IGNORECASE
    )
    if len(tables) < 2:
        _LOGGER.error("Could not find second forecast table")
        print("\n--- DEBUG: Forecast div HTML (first 2000 chars) ---")
        print(html_content[:2000])
        print("--- END DEBUG ---\n")
        return []

    table_content = tables[1]
    _LOGGER.debug(f"Found second forecast table, content length: {len(table_content)}")

    # Find the cell containing the forecast periods
    cell_match = re.search(r"<td[^>]*>(.*?)</td>", table_content, re.DOTALL)
    if not cell_match:
        _LOGGER.error("Could not find forecast cell")
        print("\n--- DEBUG: Forecast table HTML (first 2000 chars) ---")
        print(table_content[:2000])
        print("--- END DEBUG ---\n")
        return []

    cell_content = cell_match.group(1)
    _LOGGER.debug(f"Found forecast cell, content length: {len(cell_content)}")

    # Use regex to extract forecast periods directly
    # Pattern: <b>DayName: </b> followed by content until next <b>DayName: </b> or end
    # Updated to include "Overnight" as a valid period
    period_pattern = r"<b>([^:]+):\s*</b>(.*?)(?=<b>[^:]+:\s*</b>|$)"
    period_matches = re.findall(period_pattern, cell_content, re.DOTALL)

    _LOGGER.debug(f"Found {len(period_matches)} period matches")

    # Calculate target days (N+1 logic)
    # If days_limit is None, we want all available days (set to a high number)
    target_days = 100
    if days_limit is not None:
        target_days = max(0, days_limit) + 1

    periods = []
    current_day_index = 0
    is_previous_night = False

    for i, (day_name, forecast_text) in enumerate(period_matches):
        day_name = day_name.strip()

        # Clean up the period content
        forecast_text = re.sub(r"<br\s*/?>", "\n", forecast_text).strip()
        forecast_text = re.sub(r"\n+", "\n", forecast_text)  # Normalize line breaks

        # Determine is_daytime from period name
        is_daytime = True
        if "Night" in day_name or day_name in ["Tonight", "Overnight"]:
            is_daytime = False

        # Check for Day/Night transition to increment day count
        # A new day starts when we transition from Night to Day (except for the first period)
        if i > 0 and is_daytime and is_previous_night:
            current_day_index += 1

        # If we've reached the target number of days, stop
        if current_day_index >= target_days:
            break

        # Update previous night status for next iteration
        is_previous_night = not is_daytime

        # Create period object (dictionary for compatibility)
        period = {
            "day": day_name,
            "content": forecast_text,
            # Add other fields as needed by the consumer
        }
        periods.append(period)
        _LOGGER.debug(f"Parsed period: {day_name} (Day {current_day_index})")

    _LOGGER.info(
        f"Successfully parsed {len(periods)} forecast periods (covered {current_day_index + (1 if periods else 0)} days)"
    )
    return periods
