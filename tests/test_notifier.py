"""Tests for notifier functionality."""

import pytest
import sys
import os
import asyncio
from unittest.mock import MagicMock, Mock, patch

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
    from notifier import send_forecast_email, _send_email_sync
except ImportError:
    pytest.fail("Could not import notifier")


class TestNotifier:
    """Tests for notifier."""

    @patch("notifier.smtplib.SMTP")
    def test_send_email_sync_success(self, mock_smtp_cls):
        """Test successful synchronous email send."""
        mock_smtp = Mock()
        mock_smtp_cls.return_value.__enter__.return_value = mock_smtp
        
        result = _send_email_sync(
            "smtp.test.com", 587, "user", "pass", "to@test.com", "Body", "Subject"
        )
        
        assert result is True
        mock_smtp_cls.assert_called_with("smtp.test.com", 587)
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_with("user", "pass")
        mock_smtp.send_message.assert_called_once()

    @patch("notifier.smtplib.SMTP")
    def test_send_email_sync_connection_error(self, mock_smtp_cls):
        """Test connection error."""
        mock_smtp_cls.side_effect = Exception("Connection failed")
        
        result = _send_email_sync(
            "smtp.test.com", 587, "user", "pass", "to@test.com", "Body", "Subject"
        )
        
        assert result is False

    @patch("notifier.smtplib.SMTP")
    def test_send_email_sync_login_error(self, mock_smtp_cls):
        """Test login error."""
        mock_smtp = Mock()
        mock_smtp_cls.return_value.__enter__.return_value = mock_smtp
        mock_smtp.login.side_effect = Exception("Login failed")
        
        result = _send_email_sync(
            "smtp.test.com", 587, "user", "pass", "to@test.com", "Body", "Subject"
        )
        
        assert result is False

    @patch("notifier._send_email_sync")
    async def test_send_forecast_email_success(self, mock_sync):
        """Test async wrapper success."""
        mock_sync.return_value = True
        
        result = await send_forecast_email(
            "host", 587, "user", "pass", "to", "text"
        )
        
        assert result is True
        mock_sync.assert_called_once()

    @patch("notifier._send_email_sync")
    async def test_send_forecast_email_failure(self, mock_sync):
        """Test async wrapper failure."""
        mock_sync.return_value = False
        
        result = await send_forecast_email(
            "host", 587, "user", "pass", "to", "text"
        )
        
        assert result is False

    @patch("notifier._send_email_sync")
    async def test_send_forecast_email_exception(self, mock_sync):
        """Test async wrapper exception."""
        mock_sync.side_effect = Exception("Async error")
        
        result = await send_forecast_email(
            "host", 587, "user", "pass", "to", "text"
        )
        
        assert result is False
