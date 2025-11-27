"""Extended tests for IMAP handler functionality."""

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
    from imap_handler import (
        _check_imap_sync,
        _safe_decode_payload,
        extract_days_override,
    )
except ImportError:
    pytest.fail("Could not import imap_handler functions")


class TestIMAPHandlerExtended:
    """Extended tests for IMAP handler."""

    def test_extract_days_override(self):
        """Test extraction of days override from body."""
        assert extract_days_override("Forecast for 5 days") == 5
        assert extract_days_override("Forecast for 5days") == 5
        assert extract_days_override("3 day forecast") == 3
        assert extract_days_override("0days") == 0
        assert extract_days_override("today") == 0
        assert extract_days_override("current") == 0
        assert extract_days_override("tonight") == 0

        # Out of range
        assert extract_days_override("8 days") is None
        assert extract_days_override("-1 days") is None

        # No match
        assert extract_days_override("Hello world") is None

    def test_safe_decode_payload(self):
        """Test safe payload decoding."""
        assert _safe_decode_payload("string") == "string"
        assert _safe_decode_payload(b"bytes") == "bytes"
        assert _safe_decode_payload(None) == ""

        # Test with some non-ascii bytes
        assert _safe_decode_payload(b"caf\xc3\xa9") == "café"

    @patch("imap_handler.imaplib.IMAP4_SSL")
    def test_check_imap_sync_success_with_coords(self, mock_imap_cls):
        """Test successful message retrieval with coordinates."""
        mock_imap = Mock()
        mock_imap_cls.return_value = mock_imap

        # Setup successful connection and login
        mock_imap.login.return_value = "OK"
        mock_imap.select.return_value = ("OK", [b"1"])
        mock_imap.search.return_value = ("OK", [b"1"])

        # Setup fetch response
        # Message with coordinates and format
        email_body = "34.5, -118.2. Format: compact. 3 days."
        msg = Message()
        msg.set_payload(email_body)
        msg["From"] = "test@example.com"

        # Mock fetch return value
        # fetch returns (typ, data)
        # data is list of (response_part, payload)
        # payload for RFC822 is (header, body_bytes)
        mock_imap.fetch.return_value = ("OK", [(b"1 (RFC822 {100}", msg.as_bytes())])

        results = _check_imap_sync("host", 993, "user", "pass")

        assert len(results) == 1
        assert results[0]["lat"] == "34.5"
        assert results[0]["lon"] == "-118.2"
        assert results[0]["format"] == "compact"
        assert results[0]["days"] == 3
        assert results[0]["sender"] == "test@example.com"

    @patch("imap_handler.imaplib.IMAP4")
    def test_check_imap_sync_starttls(self, mock_imap_cls):
        """Test connection with STARTTLS."""
        mock_imap = Mock()
        mock_imap_cls.return_value = mock_imap

        _check_imap_sync("host", 143, "user", "pass", security="STARTTLS")

        mock_imap.starttls.assert_called_once()

    @patch("imap_handler.imaplib.IMAP4")
    def test_check_imap_sync_no_security(self, mock_imap_cls):
        """Test connection with no security."""
        mock_imap = Mock()
        mock_imap_cls.return_value = mock_imap

        _check_imap_sync("host", 143, "user", "pass", security="None")

        # Should not call starttls
        mock_imap.starttls.assert_not_called()

    @patch("imap_handler.imaplib.IMAP4_SSL")
    def test_check_imap_sync_multipart(self, mock_imap_cls):
        """Test multipart message handling."""
        mock_imap = Mock()
        mock_imap_cls.return_value = mock_imap

        mock_imap.login.return_value = "OK"
        mock_imap.select.return_value = ("OK", [b"1"])
        mock_imap.search.return_value = ("OK", [b"1"])

        # Create multipart message
        msg = email.message.EmailMessage()
        msg["From"] = "test@example.com"
        msg.set_content("This is text part. 34.5, -118.2")
        msg.add_alternative("<b>HTML part</b>", subtype="html")

        # Convert to bytes (need to use policy or generator for older python versions if needed,
        # but EmailMessage.as_bytes() should work)
        msg_bytes = msg.as_bytes()

        mock_imap.fetch.return_value = ("OK", [(b"1 (RFC822 {100}", msg_bytes)])

        results = _check_imap_sync("host", 993, "user", "pass")

        assert len(results) == 1
        assert results[0]["lat"] == "34.5"

    @patch("imap_handler.imaplib.IMAP4_SSL")
    def test_check_imap_sync_no_coords(self, mock_imap_cls):
        """Test message with no coordinates."""
        mock_imap = Mock()
        mock_imap_cls.return_value = mock_imap

        mock_imap.login.return_value = "OK"
        mock_imap.select.return_value = ("OK", [b"1"])
        mock_imap.search.return_value = ("OK", [b"1"])

        msg = Message()
        msg.set_payload("Just some text without coords")
        msg["From"] = "test@example.com"

        mock_imap.fetch.return_value = ("OK", [(b"1 (RFC822 {100}", msg.as_bytes())])

        results = _check_imap_sync("host", 993, "user", "pass")

        assert len(results) == 0

    @patch("imap_handler.imaplib.IMAP4_SSL")
    def test_check_imap_sync_fetch_error(self, mock_imap_cls):
        """Test fetch error."""
        mock_imap = Mock()
        mock_imap_cls.return_value = mock_imap

        mock_imap.login.return_value = "OK"
        mock_imap.select.return_value = ("OK", [b"1"])
        mock_imap.search.return_value = ("OK", [b"1"])

        mock_imap.fetch.return_value = ("NO", [])

        results = _check_imap_sync("host", 993, "user", "pass")

        assert len(results) == 0
