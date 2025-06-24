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

## Features

- Fetches NOAA weather forecasts for GPS coordinates
- Supports multiple forecast formats (summary, compact, full)
- Email delivery to satellite communicators (ZOLEO, InReach)
- Automatic message splitting for device character limits
- Configurable polling interval (1-1440 minutes)
- Debug logging for troubleshooting
- Comprehensive test suite
- Enhanced weather event detection (fog, extreme events)

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

1. Go to **Settings** > **Devices & Services**
2. Click **Add Integration**
3. Search for "SatCom Forecast"
4. Enter your email configuration and GPS coordinates
5. Choose your preferred forecast format

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

- **Summary**: Concise 200-character summaries with pipe separators
- **Compact**: Detailed multi-line format with weather highlights
- **Full**: Complete NOAA forecast text

See [docs/format_comparison.md](docs/format_comparison.md) for detailed format comparisons.

## Polling Interval Configuration

The integration checks for new GPS coordinate emails at regular intervals. You can configure this polling interval during setup or reconfiguration:

- **Range**: 1 to 1440 minutes (1 minute to 24 hours)
- **Default**: 5 minutes
- **Recommendation**: 5-15 minutes for most use cases

### Considerations

- **Faster polling** (1-5 minutes): More responsive but higher email server load
- **Slower polling** (15+ minutes): Lower server load but delayed responses
- **Email server limits**: Some providers have rate limits on IMAP connections
- **Battery usage**: For mobile devices, consider longer intervals to save battery

The polling interval change takes effect immediately when you save the configuration.

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
python3 test_fog_detection.py
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
