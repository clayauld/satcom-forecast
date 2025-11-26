import os
import sys

import pytest

# Add custom_components/satcom_forecast to path
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__), "..", "custom_components", "satcom_forecast"
    ),
)

from imap_handler import extract_days_override


class TestDaysExtraction:
    """Test days extraction logic."""

    def test_no_override(self):
        """Test with no override."""
        assert extract_days_override("Subject: 61.4, -148.4") is None

    def test_numeric_days(self):
        """Test with numeric days."""
        assert extract_days_override("Subject: 61.4, -148.4 5days") == 5
        assert extract_days_override("Subject: 61.4, -148.4 5 days") == 5
        assert extract_days_override("Subject: 61.4, -148.4 0days") == 0
        assert extract_days_override("Subject: 61.4, -148.4 0 days") == 0

    def test_special_keywords(self):
        """Test with special keywords."""
        assert extract_days_override("Subject: 61.4, -148.4 today") == 0
        assert extract_days_override("Subject: 61.4, -148.4 current") == 0
        assert extract_days_override("Subject: 61.4, -148.4 tonight") == 0
        assert extract_days_override("Subject: 61.4, -148.4 Tonight") == 0

    def test_invalid_days(self):
        """Test with invalid days."""
        assert extract_days_override("Subject: 61.4, -148.4 8days") is None
        assert extract_days_override("Subject: 61.4, -148.4 -1days") is None
