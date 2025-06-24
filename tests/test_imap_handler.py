#!/usr/bin/env python3
"""
Test IMAP Handler
Tests the IMAP handler functionality and error handling.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from unittest.mock import Mock, patch, MagicMock

def test_imap_handler():
    """Test IMAP handler functionality."""
    print("🔐 IMAP Handler Test")
    print("=" * 60)
    print("Testing IMAP connection error handling and state management...")
    
    # Import here to avoid Home Assistant dependency issues in test environment
    try:
        from custom_components.satcom_forecast.imap_handler import check_imap_for_gps
    except ImportError:
        print("⚠️  Skipping IMAP handler test - Home Assistant not available in test environment")
        return True
    
    class TestIMAPHandler(unittest.TestCase):
        """Test IMAP handler functionality."""
        
        def test_imap_connection_error_handling(self):
            """Test that IMAP connection errors are handled gracefully."""
            with patch('custom_components.satcom_forecast.imap_handler.imaplib.IMAP4_SSL') as mock_imap:
                # Simulate connection failure
                mock_imap.side_effect = Exception("Connection failed")
                
                result = check_imap_for_gps("test.com", 993, "user", "pass")
                self.assertEqual(result, [])
        
        def test_imap_login_error_handling(self):
            """Test that IMAP login errors are handled gracefully."""
            with patch('custom_components.satcom_forecast.imap_handler.imaplib.IMAP4_SSL') as mock_imap:
                mock_connection = Mock()
                mock_connection.login.side_effect = Exception("Login failed")
                mock_imap.return_value = mock_connection
                
                result = check_imap_for_gps("test.com", 993, "user", "pass")
                self.assertEqual(result, [])
        
        def test_folder_selection_error_handling(self):
            """Test that folder selection errors are handled gracefully."""
            with patch('custom_components.satcom_forecast.imap_handler.imaplib.IMAP4_SSL') as mock_imap:
                mock_connection = Mock()
                mock_connection.login.return_value = None
                mock_connection.select.return_value = ("NO", ["Folder not found"])
                mock_imap.return_value = mock_connection
                
                result = check_imap_for_gps("test.com", 993, "user", "pass")
                self.assertEqual(result, [])
        
        def test_search_error_handling(self):
            """Test that search errors are handled gracefully."""
            with patch('custom_components.satcom_forecast.imap_handler.imaplib.IMAP4_SSL') as mock_imap:
                mock_connection = Mock()
                mock_connection.login.return_value = None
                mock_connection.select.return_value = ("OK", [b"1"])
                mock_connection.search.return_value = ("NO", ["Search failed"])
                mock_imap.return_value = mock_connection
                
                result = check_imap_for_gps("test.com", 993, "user", "pass")
                self.assertEqual(result, [])
        
        def test_successful_imap_operation(self):
            """Test successful IMAP operation with no messages."""
            with patch('custom_components.satcom_forecast.imap_handler.imaplib.IMAP4_SSL') as mock_imap:
                mock_connection = Mock()
                mock_connection.login.return_value = None
                mock_connection.select.return_value = ("OK", [b"1"])
                mock_connection.search.return_value = ("OK", [b""])  # No messages
                mock_connection.list.return_value = ("OK", [b'(\\HasNoChildren) "/" "INBOX"'])
                mock_imap.return_value = mock_connection
                
                result = check_imap_for_gps("test.com", 993, "user", "pass")
                self.assertEqual(result, [])
                
                # Verify proper cleanup
                mock_connection.logout.assert_called_once()
    
    # Run the tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestIMAPHandler)
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    print(f"\n📊 IMAP Handler Test Results: {len(result.failures)} failures, {len(result.errors)} errors")
    return result.wasSuccessful()

if __name__ == "__main__":
    print("🧪 Testing IMAP Handler...")
    success = test_imap_handler()
    sys.exit(0 if success else 1) 