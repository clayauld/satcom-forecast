"""
Pytest-compatible IMAP Handler tests.
Tests the IMAP handler functionality and error handling.
"""

import asyncio
import os
import sys
from unittest.mock import Mock, patch

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

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_message_limit(self):
        """Test that only MAX_EMAIL_LIMIT messages are processed."""
        from imap_handler import MAX_EMAIL_LIMIT

        with patch("imap_handler.imaplib.IMAP4_SSL") as mock_imap:
            mock_connection = Mock()
            mock_connection.login.return_value = None
            mock_connection.select.return_value = ("OK", [b"1"])

            # Create a list of messages exceeding the limit
            messages_indices = [str(i).encode() for i in range(1, MAX_EMAIL_LIMIT + 5)]
            messages_response = b" ".join(messages_indices)
            mock_connection.search.return_value = ("OK", [messages_response])

            # Mock fetch to avoid errors when processing
            mock_connection.fetch.return_value = (
                "OK",
                [(b"1 (RFC822 {100}", b"From: sender@example.com\r\n\r\nBody text")],
            )

            mock_imap.return_value = mock_connection

            asyncio.run(check_imap_for_gps("test.com", 993, "user", "pass"))

            # Verify that fetch was called exactly MAX_EMAIL_LIMIT times
            assert mock_connection.fetch.call_count == MAX_EMAIL_LIMIT
