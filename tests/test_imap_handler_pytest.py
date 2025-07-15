"""
Pytest-compatible IMAP Handler tests.
Tests the IMAP handler functionality and error handling.
"""

import asyncio
import sys
import os
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "custom_components"))

# Import functions directly from module files to avoid Home Assistant dependencies
try:
    # Import directly from the module files
    sys.path.insert(
        0,
        os.path.join(
            os.path.dirname(__file__), "..", "custom_components", "satcom_forecast"
        ),
    )
    from imap_handler import check_imap_for_gps

    HAS_HA = True
except ImportError:
    # If modules are not available, skip these tests
    HAS_HA = False
    pytest.skip(
        "Home Assistant not available in test environment", allow_module_level=True
    )


class TestIMAPHandler:
    """Test IMAP handler functionality using pytest."""

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_imap_connection_error_handling(self):
        """Test that IMAP connection errors are handled gracefully."""
        with patch("imap_handler.imaplib.IMAP4_SSL") as mock_imap:
            # Simulate connection failure
            mock_imap.side_effect = Exception("Connection failed")

            result = asyncio.run(check_imap_for_gps("test.com", 993, "user", "pass"))
            assert result == []

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_imap_login_error_handling(self):
        """Test that IMAP login errors are handled gracefully."""
        with patch("imap_handler.imaplib.IMAP4_SSL") as mock_imap:
            mock_connection = Mock()
            mock_connection.login.side_effect = Exception("Login failed")
            mock_imap.return_value = mock_connection

            result = asyncio.run(check_imap_for_gps("test.com", 993, "user", "pass"))
            assert result == []

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_folder_selection_error_handling(self):
        """Test that folder selection errors are handled gracefully."""
        with patch("imap_handler.imaplib.IMAP4_SSL") as mock_imap:
            mock_connection = Mock()
            mock_connection.login.return_value = None
            mock_connection.select.return_value = ("NO", ["Folder not found"])
            mock_imap.return_value = mock_connection

            result = asyncio.run(check_imap_for_gps("test.com", 993, "user", "pass"))
            assert result == []

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_search_error_handling(self):
        """Test that search errors are handled gracefully."""
        with patch("imap_handler.imaplib.IMAP4_SSL") as mock_imap:
            mock_connection = Mock()
            mock_connection.login.return_value = None
            mock_connection.select.return_value = ("OK", [b"1"])
            mock_connection.search.return_value = ("NO", ["Search failed"])
            mock_imap.return_value = mock_connection

            result = asyncio.run(check_imap_for_gps("test.com", 993, "user", "pass"))
            assert result == []

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_successful_imap_operation(self):
        """Test successful IMAP operation with no messages."""
        with patch("imap_handler.imaplib.IMAP4_SSL") as mock_imap:
            mock_connection = Mock()
            mock_connection.login.return_value = None
            mock_connection.select.return_value = ("OK", [b"1"])
            mock_connection.search.return_value = ("OK", [b""])  # No messages
            mock_connection.list.return_value = (
                "OK",
                [b'(\\HasNoChildren) "/" "INBOX"'],
            )
            mock_imap.return_value = mock_connection

            result = asyncio.run(check_imap_for_gps("test.com", 993, "user", "pass"))
            assert result == []

            # Verify proper cleanup
            mock_connection.logout.assert_called_once()
