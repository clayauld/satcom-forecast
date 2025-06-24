#!/usr/bin/env python3
"""
Test IMAP Folder Validation
Tests the folder validation functionality in the config flow.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from unittest.mock import Mock, patch, MagicMock

def test_folder_validation():
    """Test IMAP folder validation functionality."""
    print("📁 IMAP Folder Validation Test")
    print("=" * 60)
    print("Testing folder validation and error handling...")
    
    # Import here to avoid Home Assistant dependency issues in test environment
    try:
        from custom_components.satcom_forecast.config_flow import validate_imap_folder
    except ImportError:
        print("⚠️  Skipping folder validation test - Home Assistant not available in test environment")
        return True
    
    class TestFolderValidation(unittest.TestCase):
        """Test folder validation functionality."""
        
        @patch('custom_components.satcom_forecast.config_flow.imaplib.IMAP4_SSL')
        def test_valid_folder(self, mock_imap):
            """Test validation with a valid folder."""
            mock_connection = Mock()
            mock_connection.login.return_value = None
            mock_connection.list.return_value = ("OK", [b'(\\HasNoChildren) "/" "INBOX"', b'(\\HasNoChildren) "/" "Sent"'])
            mock_connection.select.return_value = ("OK", [b"1"])
            mock_connection.logout.return_value = None
            mock_imap.return_value = mock_connection
            
            is_valid, error = validate_imap_folder("test.com", 993, "user", "pass", "INBOX")
            self.assertTrue(is_valid)
            self.assertIsNone(error)
        
        @patch('custom_components.satcom_forecast.config_flow.imaplib.IMAP4_SSL')
        def test_invalid_folder(self, mock_imap):
            """Test validation with an invalid folder."""
            mock_connection = Mock()
            mock_connection.login.return_value = None
            mock_connection.list.return_value = ("OK", [b'(\\HasNoChildren) "/" "INBOX"', b'(\\HasNoChildren) "/" "Sent"'])
            mock_connection.logout.return_value = None
            mock_imap.return_value = mock_connection
            
            is_valid, error = validate_imap_folder("test.com", 993, "user", "pass", "Forecasts")
            self.assertFalse(is_valid)
            self.assertIn("Forecasts", error)
            self.assertIn("INBOX", error)
            self.assertIn("Sent", error)
        
        @patch('custom_components.satcom_forecast.config_flow.imaplib.IMAP4_SSL')
        def test_folder_access_error(self, mock_imap):
            """Test validation when folder exists but can't be accessed."""
            mock_connection = Mock()
            mock_connection.login.return_value = None
            mock_connection.list.return_value = ("OK", [b'(\\HasNoChildren) "/" "INBOX"'])
            mock_connection.select.return_value = ("NO", [b"Access denied"])
            mock_connection.logout.return_value = None
            mock_imap.return_value = mock_connection
            
            is_valid, error = validate_imap_folder("test.com", 993, "user", "pass", "INBOX")
            self.assertFalse(is_valid)
            self.assertIn("Could not access folder", error)
        
        @patch('custom_components.satcom_forecast.config_flow.imaplib.IMAP4_SSL')
        def test_list_folders_error(self, mock_imap):
            """Test validation when listing folders fails."""
            mock_connection = Mock()
            mock_connection.login.return_value = None
            mock_connection.list.return_value = ("NO", [b"Permission denied"])
            mock_connection.logout.return_value = None
            mock_imap.return_value = mock_connection
            
            is_valid, error = validate_imap_folder("test.com", 993, "user", "pass", "INBOX")
            self.assertFalse(is_valid)
            self.assertEqual(error, "Could not list folders")
        
        @patch('custom_components.satcom_forecast.config_flow.imaplib.IMAP4_SSL')
        def test_connection_error(self, mock_imap):
            """Test validation when connection fails."""
            mock_imap.side_effect = Exception("Connection failed")
            
            is_valid, error = validate_imap_folder("test.com", 993, "user", "pass", "INBOX")
            self.assertFalse(is_valid)
            self.assertIn("IMAP connection error", error)
        
        @patch('custom_components.satcom_forecast.config_flow.imaplib.IMAP4_SSL')
        def test_login_error(self, mock_imap):
            """Test validation when login fails."""
            mock_connection = Mock()
            mock_connection.login.side_effect = Exception("Invalid credentials")
            mock_imap.return_value = mock_connection
            
            is_valid, error = validate_imap_folder("test.com", 993, "user", "pass", "INBOX")
            self.assertFalse(is_valid)
            self.assertIn("IMAP connection error", error)
    
    # Run the tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFolderValidation)
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    print(f"\n📊 Folder Validation Test Results: {len(result.failures)} failures, {len(result.errors)} errors")
    return result.wasSuccessful()

if __name__ == "__main__":
    print("🧪 Testing IMAP Folder Validation...")
    success = test_folder_validation()
    sys.exit(0 if success else 1) 