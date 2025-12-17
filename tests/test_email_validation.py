"""
Tests for email validation in IMAP handler.
"""

import asyncio
import email
import os
import sys
from email.message import Message
from unittest.mock import Mock, patch

import pytest

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "custom_components"))

# Import functions directly from module files
try:
    sys.path.insert(
        0,
        os.path.join(
            os.path.dirname(__file__), "..", "custom_components", "satcom_forecast"
        ),
    )
    from imap_handler import check_imap_for_gps
    HAS_HA = True
except ImportError:
    HAS_HA = False


class TestEmailValidation:
    """Test email validation logic."""

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_invalid_email_skipped(self):
        """Test that messages with invalid sender emails are skipped."""
        with patch("imap_handler.imaplib.IMAP4_SSL") as mock_imap:
            mock_connection = Mock()
            mock_connection.login.return_value = None
            mock_connection.select.return_value = ("OK", [b"1"])
            mock_connection.search.return_value = ("OK", [b"1"])

            # Create a mock message with invalid email
            msg = Message()
            msg["From"] = "invalid-email-address"
            msg.set_payload("61.11027, -149.79715")

            mock_connection.fetch.return_value = ("OK", [(b"1 (RFC822 {100}", msg.as_bytes())])
            mock_imap.return_value = mock_connection

            result = asyncio.run(check_imap_for_gps("test.com", 993, "user", "pass"))

            # Should be empty because email is invalid
            assert result == [], "Should skip invalid email address"

    @pytest.mark.skipif(not HAS_HA, reason="Home Assistant not available")
    def test_valid_email_processed(self):
        """Test that messages with valid sender emails are processed."""
        with patch("imap_handler.imaplib.IMAP4_SSL") as mock_imap:
            mock_connection = Mock()
            mock_connection.login.return_value = None
            mock_connection.select.return_value = ("OK", [b"1"])
            mock_connection.search.return_value = ("OK", [b"1"])

            # Create a mock message with valid email
            msg = Message()
            msg["From"] = "User <user@example.com>"
            msg.set_payload("61.11027, -149.79715")

            mock_connection.fetch.return_value = ("OK", [(b"1 (RFC822 {100}", msg.as_bytes())])
            mock_imap.return_value = mock_connection

            result = asyncio.run(check_imap_for_gps("test.com", 993, "user", "pass"))

            assert len(result) == 1
            assert result[0]["sender"] == "user@example.com"
