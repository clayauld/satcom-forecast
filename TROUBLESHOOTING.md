# Troubleshooting: Integration Not Detected

If Home Assistant doesn't detect the SatCom Forecast integration after manual installation, follow these steps:

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
pytest tests/verify_installation.py -v
```

Or run the legacy verification script:
```bash
cd /path/to/satcom-forecast
python3 tests/verify_installation.py
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
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_forecast_parser.py -v
pytest tests/test_imap_handler.py -v
pytest tests/verify_installation.py -v
```

### Legacy Testing
```bash
# Run legacy test suite
cd tests
python3 run_tests.py
```

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
- Test results from pytest suite 