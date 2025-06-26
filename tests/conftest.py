"""
Pytest configuration and fixtures for SatCom Forecast tests.
"""
import sys
import os
from pathlib import Path

# Add the custom_components directory to the Python path
project_root = Path(__file__).parent.parent
custom_components_path = project_root / "custom_components"
sys.path.insert(0, str(custom_components_path))

# Add the satcom_forecast directory to the Python path
satcom_forecast_path = custom_components_path / "satcom_forecast"
sys.path.insert(0, str(satcom_forecast_path)) 