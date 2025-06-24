#!/usr/bin/env python3
"""
Test script to verify the SatCom Forecast integration structure.
This helps identify issues that might prevent Home Assistant from detecting the integration.
"""

import json
import os
import sys
from pathlib import Path

# Get the project root directory (parent of tests directory)
PROJECT_ROOT = Path(__file__).parent.parent

def check_manifest():
    """Check if manifest.json is valid and complete."""
    print("Checking manifest.json...")
    
    try:
        manifest_path = PROJECT_ROOT / "custom_components/satcom_forecast/manifest.json"
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
        
        required_fields = [
            "domain", "name", "version", "config_flow", "dependencies", 
            "documentation", "issue_tracker", "requirements", "codeowners"
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in manifest:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        else:
            print("✅ Manifest.json is complete")
            return True
            
    except Exception as e:
        print(f"❌ Error reading manifest.json: {e}")
        return False

def check_required_files():
    """Check if all required files exist."""
    print("\nChecking required files...")
    
    required_files = [
        "custom_components/satcom_forecast/__init__.py",
        "custom_components/satcom_forecast/config_flow.py",
        "custom_components/satcom_forecast/manifest.json",
        "custom_components/satcom_forecast/const.py",
        "custom_components/satcom_forecast/coordinator.py",
        "custom_components/satcom_forecast/sensor.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files exist")
        return True

def check_python_syntax():
    """Check Python syntax of key files."""
    print("\nChecking Python syntax...")
    
    python_files = [
        "custom_components/satcom_forecast/__init__.py",
        "custom_components/satcom_forecast/config_flow.py",
        "custom_components/satcom_forecast/const.py"
    ]
    
    for file_path in python_files:
        full_path = PROJECT_ROOT / file_path
        try:
            with open(full_path, 'r') as f:
                compile(f.read(), str(full_path), 'exec')
            print(f"✅ {file_path} - syntax OK")
        except SyntaxError as e:
            print(f"❌ {file_path} - syntax error: {e}")
            return False
    
    return True

def check_directory_structure():
    """Check the overall directory structure."""
    print("\nChecking directory structure...")
    
    expected_structure = [
        "custom_components/",
        "custom_components/satcom_forecast/",
    ]
    
    for directory in expected_structure:
        full_path = PROJECT_ROOT / directory
        if full_path.exists():
            print(f"✅ {directory}")
        else:
            print(f"❌ Missing directory: {directory}")
            return False
    
    return True

def main():
    """Run all checks."""
    print("SatCom Forecast Integration Structure Check")
    print("=" * 50)
    
    checks = [
        check_directory_structure,
        check_required_files,
        check_manifest,
        check_python_syntax
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All checks passed! The integration structure looks correct.")
        print("\nIf Home Assistant still doesn't detect the integration:")
        print("1. Make sure you copied the entire 'custom_components/satcom_forecast' folder")
        print("2. Restart Home Assistant completely")
        print("3. Check Home Assistant logs for any error messages")
        print("4. Verify the integration folder is in the correct location")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
    
    return all_passed

if __name__ == "__main__":
    main() 