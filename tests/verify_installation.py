#!/usr/bin/env python3
"""
Verification script for SatCom Forecast integration installation.
Run this script in your Home Assistant environment to verify the installation.
"""

import json
import os
import sys


def check_installation_path():
    """Check if the integration is installed in the correct location."""
    print("Checking installation path...")

    # Common Home Assistant config paths
    possible_paths = [
        "/config/custom_components/satcom_forecast",
        "/homeassistant/config/custom_components/satcom_forecast",
        "./custom_components/satcom_forecast",
    ]

    installed_path = None
    for path in possible_paths:
        if os.path.exists(path):
            installed_path = path
            print(f"✅ Found integration at: {path}")
            break

    if not installed_path:
        print("❌ Integration not found in common locations")
        print(
            "Please ensure you copied the entire 'custom_components/satcom_forecast' "
            "folder"
        )
        return False

    return installed_path


def check_required_files(integration_path):
    """Check if all required files are present."""
    print(f"\nChecking required files in {integration_path}...")

    required_files = [
        "__init__.py",
        "config_flow.py",
        "manifest.json",
        "const.py",
        "coordinator.py",
        "sensor.py",
        "translations/en.json",
    ]

    missing_files = []
    for file_name in required_files:
        file_path = os.path.join(integration_path, file_name)
        if os.path.exists(file_path):
            print(f"✅ {file_name}")
        else:
            print(f"❌ Missing: {file_name}")
            missing_files.append(file_name)

    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False

    print("✅ All required files present")
    return True


def check_manifest(integration_path):
    """Check if manifest.json is valid."""
    print("\nChecking manifest.json...")

    manifest_path = os.path.join(integration_path, "manifest.json")
    try:
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        print(f"✅ Domain: {manifest.get('domain', 'NOT FOUND')}")
        print(f"✅ Name: {manifest.get('name', 'NOT FOUND')}")
        print(f"✅ Version: {manifest.get('version', 'NOT FOUND')}")
        print(f"✅ Config Flow: {manifest.get('config_flow', False)}")

        return True

    except Exception as e:
        print(f"❌ Error reading manifest.json: {e}")
        return False


def check_file_permissions(integration_path):
    """Check file permissions."""
    print("\nChecking file permissions...")

    try:
        # Check if files are readable
        test_files = ["__init__.py", "config_flow.py", "manifest.json"]
        for file_name in test_files:
            file_path = os.path.join(integration_path, file_name)
            if os.access(file_path, os.R_OK):
                print(f"✅ {file_name} is readable")
            else:
                print(f"❌ {file_name} is not readable")
                return False

        return True

    except Exception as e:
        print(f"❌ Error checking permissions: {e}")
        return False


def check_home_assistant_environment():
    """Check if we're in a Home Assistant environment."""
    print("\nChecking Home Assistant environment...")

    try:
        import homeassistant

        print(f"✅ Home Assistant version: {homeassistant.__version__}")
        return True
    except ImportError:
        print("❌ Home Assistant not available in this environment")
        print("This script should be run inside Home Assistant")
        return False


def main():
    """Run all verification checks."""
    print("SatCom Forecast Integration Verification")
    print("=" * 50)

    # Check if we're in Home Assistant environment
    ha_available = check_home_assistant_environment()

    # Check installation
    integration_path = check_installation_path()
    if not integration_path:
        return False

    # Check files
    files_ok = check_required_files(integration_path)
    if not files_ok:
        return False

    # Check manifest
    manifest_ok = check_manifest(integration_path)
    if not manifest_ok:
        return False

    # Check permissions
    permissions_ok = check_file_permissions(integration_path)
    if not permissions_ok:
        return False

    print("\n" + "=" * 50)
    print("✅ All checks passed!")

    if ha_available:
        print("\nThe integration should be detected by Home Assistant.")
        print("If it's still not appearing:")
        print("1. Restart Home Assistant completely")
        print("2. Check Home Assistant logs for any error messages")
        print(
            "3. Try searching for 'SatCom Forecast' or 'satcom' in the integration "
            "search"
        )
    else:
        print("\nInstallation structure looks correct.")
        print("Restart Home Assistant and try adding the integration.")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
