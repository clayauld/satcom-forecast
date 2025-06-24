#!/usr/bin/env python3
"""
Test IMAP Folder Detection
Tests the folder detection functionality in the config flow.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from unittest.mock import Mock, patch, MagicMock

def test_folder_detection():
    """Test IMAP folder detection functionality."""
    print("📁 IMAP Folder Detection Test")
    print("=" * 60)
    print("Testing folder detection and dropdown generation...")
    
    # Import here to avoid Home Assistant dependency issues in test environment
    try:
        from custom_components.satcom_forecast.config_flow import get_imap_folders
    except ImportError:
        print("⚠️  Skipping folder detection test - Home Assistant not available in test environment")
        return True
    
    class TestFolderDetection(unittest.TestCase):
        """Test folder detection functionality."""
        
        @patch('custom_components.satcom_forecast.config_flow.imaplib.IMAP4_SSL')
        def test_successful_folder_detection(self, mock_imap):
            """Test successful folder detection."""
            mock_connection = Mock()
            mock_connection.login.return_value = None
            mock_connection.list.return_value = ("OK", [
                b'(\\HasNoChildren) "/" "INBOX"',
                b'(\\HasNoChildren) "/" "Sent"',
                b'(\\HasNoChildren) "/" "Drafts"',
                b'(\\HasNoChildren) "/" "Trash"'
            ])
            mock_connection.logout.return_value = None
            mock_imap.return_value = mock_connection
            
            folders, error = get_imap_folders("test.com", 993, "user", "pass")
            self.assertIsNotNone(folders)
            self.assertIsNone(error)
            self.assertEqual(len(folders), 4)
            self.assertIn("INBOX", folders)
            self.assertIn("Sent", folders)
            self.assertIn("Drafts", folders)
            self.assertIn("Trash", folders)
        
        @patch('custom_components.satcom_forecast.config_flow.imaplib.IMAP4_SSL')
        def test_list_folders_error(self, mock_imap):
            """Test folder detection when listing fails."""
            mock_connection = Mock()
            mock_connection.login.return_value = None
            mock_connection.list.return_value = ("NO", [b"Permission denied"])
            mock_connection.logout.return_value = None
            mock_imap.return_value = mock_connection
            
            folders, error = get_imap_folders("test.com", 993, "user", "pass")
            self.assertIsNone(folders)
            self.assertEqual(error, "Could not list folders")
        
        @patch('custom_components.satcom_forecast.config_flow.imaplib.IMAP4_SSL')
        def test_connection_error(self, mock_imap):
            """Test folder detection when connection fails."""
            mock_imap.side_effect = Exception("Connection failed")
            
            folders, error = get_imap_folders("test.com", 993, "user", "pass")
            self.assertIsNone(folders)
            self.assertIn("IMAP connection error", error)
        
        @patch('custom_components.satcom_forecast.config_flow.imaplib.IMAP4_SSL')
        def test_login_error(self, mock_imap):
            """Test folder detection when login fails."""
            mock_connection = Mock()
            mock_connection.login.side_effect = Exception("Invalid credentials")
            mock_imap.return_value = mock_connection
            
            folders, error = get_imap_folders("test.com", 993, "user", "pass")
            self.assertIsNone(folders)
            self.assertIn("IMAP connection error", error)
        
        @patch('custom_components.satcom_forecast.config_flow.imaplib.IMAP4_SSL')
        def test_empty_folder_list(self, mock_imap):
            """Test folder detection with empty folder list."""
            mock_connection = Mock()
            mock_connection.login.return_value = None
            mock_connection.list.return_value = ("OK", [])
            mock_connection.logout.return_value = None
            mock_imap.return_value = mock_connection
            
            folders, error = get_imap_folders("test.com", 993, "user", "pass")
            self.assertIsNotNone(folders)
            self.assertIsNone(error)
            self.assertEqual(len(folders), 0)
        
        @patch('custom_components.satcom_forecast.config_flow.imaplib.IMAP4_SSL')
        def test_folder_name_parsing(self, mock_imap):
            """Test parsing of different folder name formats."""
            mock_connection = Mock()
            mock_connection.login.return_value = None
            mock_connection.list.return_value = ("OK", [
                b'(\\HasNoChildren) "/" "INBOX"',
                b'(\\HasNoChildren \\Drafts) "/" "Drafts"',
                b'(\\HasNoChildren \\Sent) "/" "Sent Mail"',
                b'(\\HasNoChildren \\Trash) "/" "Deleted Items"'
            ])
            mock_connection.logout.return_value = None
            mock_imap.return_value = mock_connection
            
            folders, error = get_imap_folders("test.com", 993, "user", "pass")
            self.assertIsNotNone(folders)
            self.assertIsNone(error)
            self.assertEqual(len(folders), 4)
            self.assertIn("INBOX", folders)
            self.assertIn("Drafts", folders)
            self.assertIn("Sent Mail", folders)
            self.assertIn("Deleted Items", folders)
    
    # Run the tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFolderDetection)
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    print(f"\n📊 Folder Detection Test Results: {len(result.failures)} failures, {len(result.errors)} errors")
    return result.wasSuccessful()

if __name__ == "__main__":
    print("🧪 Testing IMAP Folder Detection...")
    success = test_folder_detection()
    sys.exit(0 if success else 1) 