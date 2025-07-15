# Troubleshooting: Integration Not Detected

If Home Assistant doesn't detect the SatCom Forecast integration after manual installation, follow these steps:

## Recent Fixes and Improvements

### Formatting Fixes (Latest)
Several formatting issues have been resolved:

- **Summary Format**: Fixed missing space after colon in day names (e.g., "Tonight: Dense fog" instead of "Tonight:Dense fog")
- **Compact Format**: Fixed newline preservation between days for proper day separation
- **Split Utility**: Improved day separation logic to combine multiple days efficiently while preserving structure

### Test Suite Improvements
The test suite has been enhanced for better reliability:

- **Self-contained tests**: No Home Assistant dependencies required
- **55 tests with 0 skips**: Comprehensive coverage of all functionality
- **Fast execution**: Complete suite runs in ~0.12 seconds
- **Direct imports**: Faster execution by importing functions directly from module files

### Known Working Configurations
The integration has been tested and confirmed working with:
- Home Assistant 2023.1+
- Python 3.9+
- All major email providers (Gmail, Outlook, etc.)
- ZOLEO and InReach devices

## Quick Checklist

- [ ] Copied the **entire** `custom_components/satcom_forecast` folder (not just individual files)
- [ ] Placed it in `/config/custom_components/` (or your Home Assistant config directory)
- [ ] Restarted Home Assistant completely
- [ ] Checked file permissions (files should be readable)
- [ ] Verified no syntax errors in Python files

## Step-by-Step Troubleshooting

### 1. Verify Installation Location

**Correct structure:**
```
/config/
├── custom_components/
│   └── satcom_forecast/
│       ├── __init__.py
│       ├── config_flow.py
│       ├── manifest.json
│       ├── const.py
│       ├── coordinator.py
│       ├── sensor.py
│       ├── translations/
│       │   └── en.json
│       └── ... (other files)
```

**Common mistakes:**
- ❌ Copying individual files instead of the entire folder
- ❌ Placing files in wrong directory
- ❌ Missing the `translations` subfolder

### 2. Check File Permissions

Run this command in your Home Assistant environment:
```bash
ls -la /config/custom_components/satcom_forecast/
```

All files should be readable (have `r` in permissions).

### 3. Restart Home Assistant

**Important:** You must restart Home Assistant completely, not just reload.

- **Home Assistant OS:** Settings → System → Restart
- **Docker:** `docker restart homeassistant`
- **Manual:** Restart the service completely

### 4. Check Home Assistant Logs

Look for error messages related to the integration:

1. Go to **Settings** → **System** → **Logs**
2. Search for "satcom_forecast" or "satcom"
3. Look for any error messages

Common errors:
- `ModuleNotFoundError`: Missing dependencies
- `SyntaxError`: Python syntax issues
- `ImportError`: Import problems

### 5. Test Integration Structure

Run the modern pytest-based test suite:
```bash
cd /path/to/satcom-forecast
pytest tests/ -v  # Runs all 55 tests
```

Or run specific test categories:
```bash
pytest tests/test_forecast_parser.py -v
pytest tests/test_imap_handler_pytest.py -v
```

### 6. Verify in Home Assistant Environment

If you have SSH access to Home Assistant, run:
```bash
cd /config
python3 /path/to/satcom-forecast/tests/verify_installation.py
```

## Common Solutions

### Solution 1: Complete Reinstall
```bash
# Remove existing installation
rm -rf /config/custom_components/satcom_forecast

# Copy fresh installation
cp -r /path/to/satcom-forecast/custom_components/satcom_forecast /config/custom_components/

# Restart Home Assistant
```

### Solution 2: Fix Permissions
```bash
# Make files readable
chmod -R 644 /config/custom_components/satcom_forecast/*
chmod 755 /config/custom_components/satcom_forecast/
chmod 755 /config/custom_components/satcom_forecast/translations/
```

### Solution 3: Check for Conflicts
Make sure no other integration uses the domain `satcom_forecast`.

### Solution 4: Alternative Installation
If manual installation continues to fail:

1. **Use HACS (Recommended):**
   - Install HACS in Home Assistant
   - Add this repository as a custom repository
   - Install through HACS UI

2. **Use Git:**
   ```bash
   cd /config
   git clone https://github.com/clayauld/satcom-forecast.git
   ln -s satcom-forecast/custom_components/satcom_forecast custom_components/
   ```

## Testing Your Installation

### Modern Pytest Testing
```bash
# Run all tests (55 tests, ~0.12s)
pytest tests/ -v

# Run specific test categories
pytest tests/test_forecast_parser.py -v
pytest tests/test_compact_format.py -v
pytest tests/test_summary_format.py -v
pytest tests/test_full_format.py -v
pytest tests/test_split_utility.py -v
pytest tests/test_text_length.py -v
pytest tests/test_imap_handler_pytest.py -v
```

### Test Coverage
The comprehensive test suite covers:
- ✅ **Forecast Parsing**: All format types and edge cases
- ✅ **Weather Events**: Comprehensive event detection including smoke
- ✅ **Format Fixes**: Recent formatting improvements (spacing, newlines)
- ✅ **Split Utilities**: Message splitting and day separation
- ✅ **Character Limits**: Device-specific handling
- ✅ **IMAP Handling**: Email processing and error handling

## Search Terms

If the integration doesn't appear, try searching for:
- "SatCom Forecast"
- "Satellite Forecast"
- "satcom"
- "forecast"

## Still Not Working?

If none of the above solutions work:

1. **Check Home Assistant version compatibility**
2. **Verify all dependencies are installed**
3. **Try a different Home Assistant installation method**
4. **Check for any custom component conflicts**
5. **Review Home Assistant custom integration documentation**

## Getting Help

1. Check the [GitHub Issues](https://github.com/clayauld/satcom-forecast/issues)
2. Review the [Home Assistant Custom Integration Documentation](https://developers.home-assistant.io/docs/creating_integration_manifest)
3. Check the [Home Assistant Community Forum](https://community.home-assistant.io/)

## Debug Information

When reporting issues, include:
- Home Assistant version
- Installation method (Docker, OS, etc.)
- Complete error messages from logs
- Output from verification scripts
- Directory structure of your installation
- Test results from pytest suite (all 55 tests should pass)
