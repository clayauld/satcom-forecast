# Manual Installation Guide for SatCom Forecast

This guide helps you install the SatCom Forecast integration manually when it's not detected by Home Assistant.

## Prerequisites

- Home Assistant running (any installation method: Docker, Home Assistant OS, etc.)
- Access to your Home Assistant configuration directory
- Basic knowledge of file operations

## Installation Steps

### 1. Download the Integration

**Option A: Download from GitHub**
1. Go to [https://github.com/clayauld/satcom-forecast](https://github.com/clayauld/satcom-forecast)
2. Click the green "Code" button
3. Select "Download ZIP"
4. Extract the ZIP file to your computer

**Option B: Clone the Repository**
```bash
git clone https://github.com/clayauld/satcom-forecast.git
```

### 2. Copy the Integration Files

**Important**: You need to copy the **entire** `custom_components/satcom_forecast` folder to your Home Assistant configuration directory.

#### For Home Assistant OS / Supervised:
```bash
# Copy the integration folder
cp -r custom_components/satcom_forecast /config/custom_components/
```

#### For Docker:
```bash
# Copy the integration folder to your mounted config directory
cp -r custom_components/satcom_forecast /path/to/your/config/custom_components/
```

#### For Manual Installation:
Copy the `custom_components/satcom_forecast` folder to your Home Assistant configuration directory's `custom_components` folder.

### 3. Verify the Installation

After copying, your directory structure should look like this:
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
├── configuration.yaml
└── ... (other config files)
```

### 4. Restart Home Assistant

**Important**: You must restart Home Assistant completely for it to detect new custom integrations.

#### For Home Assistant OS:
- Go to **Settings** > **System** > **Restart**

#### For Docker:
```bash
docker restart homeassistant
```

#### For Manual Installation:
Restart the Home Assistant service according to your installation method.

### 5. Add the Integration

1. Go to **Settings** > **Devices & Services**
2. Click **Add Integration**
3. Search for "SatCom Forecast" or "Satellite Forecast"
4. If it doesn't appear, try searching for "satcom" or "forecast"

## Testing Your Installation

### Modern Pytest Testing (Recommended)
```bash
# Install pytest if not already installed
pip install pytest

# Run the installation verification tests
cd /path/to/satcom-forecast
pytest tests/verify_installation.py -v

# Run all tests to verify functionality
pytest tests/ -v
```

### Legacy Testing
```bash
# Run the legacy verification script
cd /path/to/satcom-forecast
python3 tests/verify_installation.py

# Run the legacy test suite
cd tests
python3 run_tests.py
```

## Troubleshooting

### Integration Not Found

If the integration doesn't appear in the search:

1. **Check File Permissions**
   ```bash
   ls -la /config/custom_components/satcom_forecast/
   ```
   Make sure all files are readable.

2. **Verify Directory Structure**
   ```bash
   tree /config/custom_components/satcom_forecast/
   ```
   You should see all the required files.

3. **Check Home Assistant Logs**
   - Go to **Settings** > **System** > **Logs**
   - Look for any error messages related to "satcom_forecast"
   - Common errors include syntax errors or missing dependencies

4. **Test Integration Structure**
   Run the modern pytest-based verification:
   ```bash
   cd /path/to/satcom-forecast
   pytest tests/verify_installation.py -v
   ```

   Or run the legacy verification script:
   ```bash
   cd /path/to/satcom-forecast
   python3 tests/verify_installation.py
   ```

### Common Issues

#### Issue: "No module named 'homeassistant'"
- This is normal when testing outside of Home Assistant
- The integration will work fine inside Home Assistant

#### Issue: Integration appears but fails to configure
- Check that all required dependencies are installed
- Verify your email server settings
- Check Home Assistant logs for specific error messages

#### Issue: Integration disappears after restart
- Make sure you copied the entire folder, not just individual files
- Verify the folder is in the correct location
- Check file permissions

#### Issue: Pytest not found
```bash
# Install pytest
pip install pytest

# Or use python -m pytest
python -m pytest tests/verify_installation.py -v
```

### Alternative Installation Methods

#### Using HACS (Recommended)
If manual installation continues to fail, consider using HACS:

1. Install HACS in Home Assistant
2. Add this repository as a custom repository in HACS
3. Install through HACS UI

#### Using Git Submodule
```bash
cd /config
git submodule add https://github.com/clayauld/satcom-forecast.git
ln -s satcom-forecast/custom_components/satcom_forecast custom_components/
```

## Verification

After successful installation, you should be able to:

1. Find "SatCom Forecast" in the integration search
2. Configure the integration with your email settings
3. See the integration listed in **Settings** > **Devices & Services**
4. Access reconfiguration options by clicking on the integration
5. Run tests successfully with pytest

## Support

If you continue to have issues:

1. Check the [GitHub Issues](https://github.com/clayauld/satcom-forecast/issues)
2. Review the [Home Assistant Custom Integration Documentation](https://developers.home-assistant.io/docs/creating_integration_manifest)
3. Check your Home Assistant version compatibility
4. Run the test suite and include results in your issue report

## File Checklist

Before restarting Home Assistant, verify these files exist:

- [ ] `/config/custom_components/satcom_forecast/__init__.py`
- [ ] `/config/custom_components/satcom_forecast/config_flow.py`
- [ ] `/config/custom_components/satcom_forecast/manifest.json`
- [ ] `/config/custom_components/satcom_forecast/const.py`
- [ ] `/config/custom_components/satcom_forecast/translations/en.json`
- [ ] `/config/custom_components/satcom_forecast/coordinator.py`
- [ ] `/config/custom_components/satcom_forecast/sensor.py`
