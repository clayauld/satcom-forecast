# SatCom Forecast

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.1+-blue.svg)](https://www.home-assistant.io/)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![GitHub Release](https://img.shields.io/github/v/release/clayauld/satcom-forecast)](https://github.com/clayauld/satcom-forecast/releases)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/clayauld/satcom-forecast/validation.yml?branch=main)](https://github.com/clayauld/satcom-forecast/actions)
[![Discussions](https://img.shields.io/badge/discussions-welcome-brightgreen.svg)](https://github.com/clayauld/satcom-forecast/discussions)
[![Support the project](https://img.shields.io/badge/support%20the%20project-☕%20Buy%20me%20a%20coffee-orange.svg)](https://www.buymeacoffee.com/clayauld)

A Home Assistant integration for fetching NOAA weather forecasts and sending them via email to satellite communicators.

<!-- [![My Home Assistant](https://my.home-assistant.io/badge.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=clayauld&repository=satcom-forecast&category=Integration) -->

## Features

- Fetches NOAA weather forecasts for GPS coordinates
- Supports multiple forecast formats (summary, compact, full)
- Email delivery to satellite communicators (ZOLEO, InReach)
- Automatic message splitting for device character limits
- Configurable scanning interval (1-1440 minutes)
- Two-step configuration process (email setup + forecast settings)
- Automatic folder detection and dropdown selection
- IMAP folder validation with helpful error messages
- Debug logging for troubleshooting
- Comprehensive test suite
- Enhanced weather event detection (rain, snow, sleet, wind, thunderstorms, fog, smoke)
- Extreme event highlighting with warning indicators (🚨)
- Temperature formatting with degree symbols (°)
- Wind speed detection with significant wind filtering (15+ mph)
- Probability inference for weather events when not explicitly stated
- Compact format with 1500 character limit for longer forecasts

## How to Use

To request a weather forecast, simply send an email to the address monitored by SatCom Forecast (the IMAP account you configured). The integration will extract the GPS coordinates from the email body and send a forecast reply to the sender.

**Basic Syntax:**

- The email body must contain latitude and longitude in decimal degrees (separated by a comma, space, or semicolon):

```
61.11027, -149.79715
```

- Optionally, you can specify a format keyword (`summary`, `compact`, or `full`) anywhere in the message to override the default format:

```
61.11027, -149.79715
format: summary
```

or simply:

```
61.11027, -149.79715 summary
```

**Example:**

Subject: `Forecast Request`

Body:
```
61.11027, -149.79715 compact
```

The integration will detect the coordinates and format, fetch the forecast, and reply to the sender with the requested weather information.

### Email Filtering Setup

To keep your inbox organized, consider setting up email filters or rules to automatically move forecast request emails to a dedicated folder. This helps separate forecast requests from regular emails and makes it easier to monitor the system.

**Gmail Example:**
1. Go to Gmail Settings → Filters and Blocked Addresses
2. Click "Create a new filter"
3. Set criteria (e.g., "Subject contains: forecast" or "From: your-satellite-device@domain.com")
4. Choose "Apply the label" and create a new label like "SatCom Forecasts"
5. Check "Skip the Inbox" to keep requests out of your main inbox

**Outlook Example:**
1. Go to Settings → View all Outlook settings → Mail → Rules
2. Click "Add new rule"
3. Set conditions (e.g., "Subject contains: forecast")
4. Choose "Move to" and select your forecast folder
5. Save the rule

**Other Email Providers:**
Most email providers support similar filtering options. Look for "Rules," "Filters," or "Actions" in your email settings to set up automatic organization.

**Benefits:**
- Keeps your main inbox clean
- Makes it easier to monitor forecast requests
- Allows you to set up different folders for different purposes
- Helps with troubleshooting if issues arise

## Quick Installation

### HACS Installation (Recommended)

#### Method 1: HACS UI (Default Store)
1. Open **HACS** in your Home Assistant sidebar
2. Go to **Integrations**
3. Click the **+** button in the bottom right
4. Search for "SatCom Forecast"
5. Click **Download**
6. Restart Home Assistant
7. Go to **Settings** > **Devices & Services** > **Add Integration**
8. Search for "SatCom Forecast" and configure

#### Method 2: HACS Custom Repository (Fallback)
If the integration is not yet in the default store:
1. Open **HACS** in your Home Assistant sidebar
2. Go to **Integrations**
3. Click the **+** button in the bottom right
4. Click **Custom repositories**
5. Add repository: `clayauld/satcom-forecast`
6. Category: **Integration**
7. Click **Add**
8. Find "SatCom Forecast" in the list and click **Download**
9. Restart Home Assistant
10. Go to **Settings** > **Devices & Services** > **Add Integration**
11. Search for "SatCom Forecast" and configure

### Manual Installation

1. Copy the `custom_components/satcom_forecast` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Add the integration via the UI

## Repository Structure

```
satcom-forecast/
├── custom_components/satcom_forecast/  # Main integration code
├── tests/                              # Test suite
├── docs/                               # Documentation
├── .github/                            # GitHub workflows
├── .translations/                      # Translation files
├── hacs.json                          # HACS configuration
└── README.md                          # This file
```

## Configuration

The integration uses a two-step configuration process similar to Mail and Packages:

### Step 1: Email Configuration
Enter your IMAP and SMTP server details to connect to your email account:
- **IMAP Host**: Your email provider's IMAP server (e.g., imap.gmail.com)
- **IMAP Port**: IMAP port (usually 993 for SSL, 143 for STARTTLS, 143 for None)
- **IMAP Security**: Choose SSL (recommended), STARTTLS, or None (unencrypted)
- **Username**: Your email address or username (depending on your provider)
- **Password**: Your email password or app password
- **SMTP Host**: Your email provider's SMTP server (e.g., smtp.gmail.com)
- **SMTP Port**: SMTP port (usually 587 for TLS)
- **SMTP Username**: Your email address
- **SMTP Password**: Your email password or app password

### Step 2: Forecast Configuration
After successfully connecting to your email account, configure the forecast settings:
- **Mail Folder**: Select from available folders in your email account
- **Forecast Format**: Choose summary, compact, or full format
- **Device Type**: Select ZOLEO or InReach
- **Character Limit**: Set message length limit (0 = no limit)
- **Debug Logging**: Enable detailed logging for troubleshooting
- **Scanning Interval**: How often to check for new emails (1-1440 minutes)

The integration will automatically detect and list all available folders in your email account, making it easy to select the correct folder to monitor.

## Reconfiguration

After the integration is installed, you can reconfigure all settings at any time:

1. Go to **Settings** > **Devices & Services**
2. Find "SatCom Forecast" in your integrations list
3. Click on the integration entry
4. Click **Configure** to open the reconfiguration options
5. Modify any settings as needed:
   - Email server settings (IMAP/SMTP)
   - Forecast format and device type
   - Character limits and debug settings
   - Polling interval (how often to check for new emails)
6. Click **Submit** to save changes

**Note**: Passwords are hidden by default in the configuration forms for security. You only need to enter passwords if you want to change them. The polling interval change takes effect immediately after saving.

## Forecast Formats

The integration supports three forecast formats:

- **Summary**: Concise time-based summaries with weather events and probabilities (1500 character limit)
- **Compact**: Detailed multi-line format with weather highlights and temperature/wind info (1500 character limit)
- **Full**: Complete NOAA forecast text (2000+ character limit)

See [docs/format_comparison.md](docs/format_comparison.md) for detailed format comparisons.

### Weather Event Detection

All formats support comprehensive weather event detection:

- **Precipitation**: Rain, showers, drizzle, sprinkles
- **Winter Weather**: Snow, blizzard, flurries, sleet, freezing rain
- **Wind**: Significant wind events (15+ mph) with direction and speed
- **Thunderstorms**: Thunderstorms, severe thunderstorms
- **Fog**: Fog, dense fog, patchy fog, haze, mist
- **Smoke**: Wildfire smoke, smoke conditions
- **Extreme Events**: Blizzard, ice storm, tornado, hurricane, severe thunderstorm, high wind warning, flood warning, dense fog, smoke

### Special Features

- **Warning Indicators**: Extreme events are marked with 🚨
- **Temperature Formatting**: High/low temperatures with degree symbols (°)
- **Wind Detection**: Only shows wind events for significant speeds (15+ mph)
- **Probability Inference**: Provides meaningful percentages when NOAA doesn't specify them
- **Smart Truncation**: Cuts at sentence boundaries to maintain readability

## Scanning Interval Configuration

The integration checks for new GPS coordinate emails at regular intervals. You can configure this scanning interval during setup or reconfiguration:

- **Range**: 1 to 1440 minutes (1 minute to 24 hours)
- **Default**: 5 minutes
- **Recommendation**: 5-15 minutes for most use cases

### Considerations

- **Faster scanning** (1-5 minutes): More responsive but higher email server load
- **Slower scanning** (15+ minutes): Lower server load but delayed responses
- **Email server limits**: Some providers have rate limits on IMAP connections
- **Battery usage**: For mobile devices, consider longer intervals to save battery

The scanning interval change takes effect immediately when you save the configuration.

## Testing

The integration includes a comprehensive test suite. To run tests:

```bash
cd tests
python3 run_tests.py
```

Or run individual tests:

```bash
cd tests
python3 test_multi_region.py
python3 test_weather_detection.py
```

See [tests/README.md](tests/README.md) for detailed testing information.

## Debug Logging

This integration includes comprehensive debug logging to help troubleshoot issues. You can enable debug logging in two ways:

### 1. During Configuration

When setting up the integration, you can enable debug logging by checking the "Debug" option in the configuration flow.

### 2. Using Home Assistant Services

You can enable or disable debug logging dynamically using the Home Assistant service:

**Enable debug logging:**
```yaml
service: satcom_forecast.set_debug_logging
data:
  enabled: true
```

**Disable debug logging:**
```yaml
service: satcom_forecast.set_debug_logging
data:
  enabled: false
```

### Debug Information

When debug logging is enabled, the integration will log detailed information about:

- IMAP connection and email processing
- GPS coordinate extraction from emails
- NOAA API requests and responses
- Forecast parsing and formatting
- Email sending operations
- Message splitting for device compatibility
- Coordinator update cycles

### Viewing Debug Logs

Debug logs can be viewed in the Home Assistant logs. To see debug logs for this integration specifically, you can filter the logs:

```bash
grep "custom_components.satcom_forecast" /config/home-assistant.log | grep DEBUG
```

Or in the Home Assistant UI, go to Developer Tools > Logs and filter for "satcom_forecast".

## Troubleshooting

### Common Issues

#### IMAP Connection Errors

**Error**: `command SEARCH illegal in state AUTH, only allowed in states SELECTED`

**Solution**: This error occurs when the IMAP connection is not properly selecting a mailbox before searching. The integration now includes improved error handling for this issue. If you encounter this error:

1. Check your IMAP folder name (default is "INBOX")
2. Verify your email server credentials
3. Enable debug logging to see detailed connection information
4. Restart the integration if the issue persists

#### Invalid IMAP Folder

**Error**: `Failed to select folder 'Forecasts': NO` or `[NONEXISTENT] Unknown Mailbox: Forecasts`

**Solution**: The integration now validates email connections and shows available folders during configuration. If you encounter this error:

1. **During initial setup**: The configuration will automatically detect and list available folders
2. **During reconfiguration**: The options form will display the error and prevent saving
3. **Common folder names**: Try "INBOX", "Sent", "Drafts", or check your email client for exact folder names
4. **Case sensitivity**: Some email providers are case-sensitive with folder names

The integration will now:
- ✅ **Automatically detect folders**: Lists all available folders in your email account
- ✅ **Dropdown selection**: Choose from available folders instead of typing
- ✅ **Show specific error messages**: Clear guidance when folder issues occur
- ✅ **Prevent configuration errors**: Validates folder selection before saving

#### Integration Not Detected

If Home Assistant doesn't detect the integration after installation:

1. Ensure the entire `custom_components/satcom_forecast` folder is copied
2. Restart Home Assistant completely
3. Check the Home Assistant logs for any error messages
4. Verify the integration folder is in the correct location: `config/custom_components/satcom_forecast/`

#### Email Delivery Issues

If forecasts are not being sent via email:

1. Verify SMTP server settings and credentials
2. Check if your email provider requires app-specific passwords
3. Enable debug logging to see detailed SMTP connection information
4. Test your SMTP settings with a simple email client first

#### Forecast Fetching Issues

If NOAA forecasts are not being fetched:

1. Verify the GPS coordinates are in the correct format (decimal degrees)
2. Check your internet connection
3. Enable debug logging to see NOAA API request details
4. Verify the coordinates are within the United States (NOAA coverage area)

### Getting Help

If you're still experiencing issues:

1. Enable debug logging and check the logs
2. Search existing [GitHub Issues](https://github.com/clayauld/satcom-forecast/issues)
3. Create a new issue with:
   - Home Assistant version
   - Integration version
   - Debug logs (with sensitive information removed)
   - Steps to reproduce the issue

## Documentation

- [Format Comparison](docs/format_comparison.md) - Detailed comparison of forecast formats
- [Test Suite](tests/README.md) - Testing information and examples

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.