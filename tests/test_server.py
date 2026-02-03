"""
Unit tests for PeerSync server components.
"""

import unittest
from unittest.mock import Mock, patch
import socket
import time

# Adjust import path as needed
import sys
sys.path.insert(0, '../src')
from server import PeerSyncServer
from config import MSG_OK, MSG_ERROR


class TestPeerSyncServer(unittest.TestCase):
    """Test cases for PeerSyncServer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.port = 5555
        # Mock socket to avoid actual network operations
        with patch('socket.socket'):
            self.server = PeerSyncServer(self.port)
    
    def test_server_initialization(self):
        """Test server initializes with correct parameters."""
        self.assertEqual(self.server.port, self.port)
        self.assertIsInstance(self.server.active_clients, dict)
        self.assertIsInstance(self.server.published_files, dict)
    
    def test_check_inactive_clients_removes_stale(self):
        """Test that inactive clients are removed after timeout."""
        # Add active client
        client_addr = ('127.0.0.1', 12345)
        self.server.active_clients[client_addr] = {
            'username': 'test_user',
            'last_heartbeat': time.time() - 10,  # 10 seconds ago
            'tcp_address': None
        }
        
        # Check for inactive clients
        self.server.check_for_inactive_clients()
        
        # Client should be removed
        self.assertNotIn(client_addr, self.server.active_clients)
    
    def test_check_inactive_clients_keeps_active(self):
        """Test that active clients are not removed."""
        # Add active client
        client_addr = ('127.0.0.1', 12345)
        self.server.active_clients[client_addr] = {
            'username': 'test_user',
            'last_heartbeat': time.time(),  # Just now
            'tcp_address': None
        }
        
        # Check for inactive clients
        self.server.check_for_inactive_clients()
        
        # Client should still be there
        self.assertIn(client_addr, self.server.active_clients)
    
    def test_process_heartbeat_updates_timestamp(self):
        """Test that heartbeat updates last_heartbeat time."""
        client_addr = ('127.0.0.1', 12345)
        old_time = time.time() - 5
        
        self.server.active_clients[client_addr] = {
            'username': 'test_user',
            'last_heartbeat': old_time,
            'tcp_address': None
        }
        
        # Process heartbeat
        self.server.process_heartbeat(client_addr)
        
        # Timestamp should be updated
        new_time = self.server.active_clients[client_addr]['last_heartbeat']
        self.assertGreater(new_time, old_time)
    
    def test_publish_file_adds_to_registry(self):
        """Test that publishing a file adds it to registry."""
        client_addr = ('127.0.0.1', 12345)
        self.server.active_clients[client_addr] = {
            'username': 'test_user',
            'last_heartbeat': time.time(),
            'tcp_address': None
        }
        
        # Mock socket sendto
        self.server.socket.sendto = Mock()
        
        # Publish file
        self.server.handle_publish_file(client_addr, "pub test.txt")
        
        # File should be in registry
        self.assertIn('test.txt', self.server.published_files)
        self.assertIn('test_user', self.server.published_files['test.txt'])
    
    def test_unpublish_file_removes_from_registry(self):
        """Test that unpublishing removes file from registry."""
        client_addr = ('127.0.0.1', 12345)
        self.server.active_clients[client_addr] = {
            'username': 'test_user',
            'last_heartbeat': time.time(),
            'tcp_address': None
        }
        
        # Add published file
        self.server.published_files['test.txt'] = ['test_user']
        
        # Mock socket sendto
        self.server.socket.sendto = Mock()
        
        # Unpublish file
        self.server.handle_unpublish_file(client_addr, "unp test.txt")
        
        # File should be removed from registry
        self.assertNotIn('test.txt', self.server.published_files)
    
    def test_search_files_finds_matches(self):
        """Test file search returns matching files."""
        client_addr = ('127.0.0.1', 12345)
        self.server.active_clients[client_addr] = {
            'username': 'searcher',
            'last_heartbeat': time.time(),
            'tcp_address': None
        }
        
        # Add some published files
        self.server.published_files = {
            'document.txt': ['other_user'],
            'report.pdf': ['other_user'],
            'image.png': ['other_user']
        }
        
        # Mock socket sendto to capture response
        sent_data = []
        self.server.socket.sendto = lambda data, addr: sent_data.append(data.decode())
        
        # Search for files
        self.server.handle_search_files(client_addr, "sch doc")
        
        # Should find document.txt
        self.assertIn('document.txt', sent_data[0])


class TestAuthenticationLogic(unittest.TestCase):
    """Test authentication logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        with patch('socket.socket'):
            self.server = PeerSyncServer(5555)
        
        # Mock credentials
        self.server.credentials = {
            'alice': 'password123',
            'bob': 'secret'
        }
    
    def test_valid_credentials_accepted(self):
        """Test that valid credentials are accepted."""
        client_addr = ('127.0.0.1', 12345)
        
        # Mock socket sendto to capture response
        sent_data = []
        self.server.socket.sendto = lambda data, addr: sent_data.append(data.decode())
        
        # Authenticate
        self.server.authenticate_client(client_addr, "auth alice password123")
        
        # Should send OK
        self.assertEqual(sent_data[-1], MSG_OK)
        self.assertIn(client_addr, self.server.active_clients)
    
    def test_invalid_credentials_rejected(self):
        """Test that invalid credentials are rejected."""
        client_addr = ('127.0.0.1', 12345)
        
        # Mock socket sendto to capture response
        sent_data = []
        self.server.socket.sendto = lambda data, addr: sent_data.append(data.decode())
        
        # Try to authenticate with wrong password
        self.server.authenticate_client(client_addr, "auth alice wrongpass")
        
        # Should send ERR
        self.assertEqual(sent_data[-1], MSG_ERROR)
        self.assertNotIn(client_addr, self.server.active_clients)
    
    def test_already_logged_in_rejected(self):
        """Test that already logged in user is rejected."""
        client_addr1 = ('127.0.0.1', 12345)
        client_addr2 = ('127.0.0.1', 54321)
        
        # First login
        self.server.active_clients[client_addr1] = {
            'username': 'alice',
            'last_heartbeat': time.time(),
            'tcp_address': None
        }
        
        # Mock socket sendto
        sent_data = []
        self.server.socket.sendto = lambda data, addr: sent_data.append(data.decode())
        
        # Try to login again from different address
        self.server.authenticate_client(client_addr2, "auth alice password123")
        
        # Should send ERR
        self.assertEqual(sent_data[-1], MSG_ERROR)
        self.assertNotIn(client_addr2, self.server.active_clients)


if __name__ == '__main__':
    unittest.main()
