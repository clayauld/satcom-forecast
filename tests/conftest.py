"""
Pytest configuration and fixtures for SatCom Forecast tests.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add the custom_components directory to the Python path
project_root = Path(__file__).parent.parent
custom_components_path = project_root / "custom_components"
sys.path.insert(0, str(custom_components_path))

# Add the satcom_forecast directory to the Python path
satcom_forecast_path = custom_components_path / "satcom_forecast"
sys.path.insert(0, str(satcom_forecast_path))

# Mock homeassistant modules
sys.modules["homeassistant"] = MagicMock()
sys.modules["homeassistant.config_entries"] = MagicMock()
sys.modules["homeassistant.core"] = MagicMock()
sys.modules["homeassistant.helpers"] = MagicMock()
sys.modules["homeassistant.helpers.typing"] = MagicMock()
sys.modules["homeassistant.const"] = MagicMock()
sys.modules["homeassistant.data_entry_flow"] = MagicMock()
sys.modules["aiofiles"] = MagicMock()
sys.modules["voluptuous"] = MagicMock()
