"""
PeerSync Server - Central coordinator for P2P file sharing.

This module implements the server component that manages:
- Client authentication
- Active peer tracking with heartbeat monitoring
- File publication registry
- Peer discovery and coordination
"""

import socket
import sys
import time
from typing import Dict, Tuple, Optional
from datetime import datetime

from config import (
    SERVER_HOST, BUFFER_SIZE, HEARTBEAT_TIMEOUT, CREDENTIALS_FILE,
    MSG_HEARTBEAT, MSG_OK, MSG_ERROR, MSG_TCP,
    CMD_LIST_ACTIVE_PEERS, CMD_LIST_PUBLISHED_FILES,
    CMD_PUBLISH, CMD_UNPUBLISH, CMD_SEARCH, CMD_GET,
    RESP_FILE_PUBLISHED, RESP_FILE_UNPUBLISHED, RESP_FILE_UNPUB_FAILED,
    RESP_NO_ACTIVE_PEERS, RESP_NO_PUBLISHED_FILES, RESP_NO_FILES_FOUND,
    RESP_FILE_NOT_FOUND, RESP_NO_ACTIVE_PEER_HAS_FILE
)
from utils import get_timestamp, load_credentials, parse_command


# Type aliases
ClientAddress = Tuple[str, int]
ClientData = Dict[str, any]


class PeerSyncServer:
    """Central server for PeerSync P2P system."""
    
    def __init__(self, port: int):
        """
        Initialise the PeerSync server.
        
        Args:
            port: UDP port number for server to bind to
        """
        self.port = port
        self.server_address = (SERVER_HOST, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(self.server_address)
        
        # Data structures
        self.active_clients: Dict[ClientAddress, ClientData] = {}
        self.published_files: Dict[str, list] = {}
        self.credentials = load_credentials(CREDENTIALS_FILE)
        
        print(f"Server started on {SERVER_HOST}:{port}")
    
    def log_action(self, client_address: ClientAddress, event: str) -> None:
        """
        Log server actions with timestamp.
        
        Args:
            client_address: Client's (IP, port) tuple
            event: Description of the event
        """
        timestamp = get_timestamp()
        print(f"{timestamp}: {client_address} {event}")
    
    def check_for_inactive_clients(self) -> None:
        """Remove clients that haven't sent heartbeat within timeout period."""
        current_time = time.time()
        inactive_clients = [
            client for client, data in self.active_clients.items()
            if current_time - data['last_heartbeat'] > HEARTBEAT_TIMEOUT
        ]
        
        for client in inactive_clients:
            username = self.active_clients[client]['username']
            del self.active_clients[client]
            # Optionally log inactive client removal
            # self.log_action(client, f"Removed inactive client {username}")
    
    def process_heartbeat(self, client_address: ClientAddress) -> None:
        """
        Update last heartbeat time for client.
        
        Args:
            client_address: Client's address tuple
        """
        if client_address in self.active_clients:
            self.active_clients[client_address]['last_heartbeat'] = time.time()
            username = self.active_clients[client_address]['username']
            self.log_action(client_address, f"Received HBT from {username}")
    
    def authenticate_client(self, client_address: ClientAddress, message: str) -> None:
        """
        Authenticate client credentials.
        
        Args:
            client_address: Client's address tuple
            message: Authentication message in format 'auth username password'
        """
        parts = message.split()
        
        if len(parts) != 3:
            self.log_action(client_address, "Received AUTH (invalid format)")
            self.socket.sendto(MSG_ERROR.encode(), client_address)
            self.log_action(client_address, "Sent ERR to unknown client")
            return
        
        _, username, password = parts
        self.log_action(client_address, f"Received AUTH from {username}")
        
        # Check if user already active
        if any(data['username'] == username for data in self.active_clients.values()):
            self.socket.sendto(MSG_ERROR.encode(), client_address)
            self.log_action(client_address, f"Sent ERR to {username}")
            return
        
        # Validate credentials
        if username in self.credentials and self.credentials[username] == password:
            self.socket.sendto(MSG_OK.encode(), client_address)
            self.active_clients[client_address] = {
                'username': username,
                'last_heartbeat': time.time(),
                'tcp_address': None
            }
            self.log_action(client_address, f"Sent OK to {username}")
        else:
            self.socket.sendto(MSG_ERROR.encode(), client_address)
            self.log_action(client_address, f"Sent ERR to {username}")
    
    def process_tcp_address(self, client_address: ClientAddress, message: str) -> None:
        """
        Store client's TCP address for file transfers.
        
        Args:
            client_address: Client's address tuple
            message: Message in format 'TCP <IP> <port>'
        """
        try:
            _, tcp_ip, tcp_port = message.split()
            if client_address in self.active_clients:
                self.active_clients[client_address]['tcp_address'] = (tcp_ip, tcp_port)
        except ValueError:
            self.log_action(client_address, "Received unreadable TCP address")
    
    def handle_publish_file(self, client_address: ClientAddress, message: str) -> None:
        """
        Handle file publication request.
        
        Args:
            client_address: Client's address tuple
            message: Message in format 'pub <filename>'
        """
        _, filename = parse_command(message)
        
        if client_address not in self.active_clients:
            self.log_action(client_address, "Received PUB from unknown client")
            return
        
        username = self.active_clients[client_address]['username']
        self.log_action(client_address, f"Received PUB from {username}")
        
        # Add file to published files registry
        if filename in self.published_files:
            if username not in self.published_files[filename]:
                self.published_files[filename].append(username)
        else:
            self.published_files[filename] = [username]
        
        self.socket.sendto(RESP_FILE_PUBLISHED.encode(), client_address)
        self.log_action(client_address, f"Sent OK to {username}")
    
    def handle_unpublish_file(self, client_address: ClientAddress, message: str) -> None:
        """
        Handle file unpublication request.
        
        Args:
            client_address: Client's address tuple
            message: Message in format 'unp <filename>'
        """
        _, filename = parse_command(message)
        
        if client_address not in self.active_clients:
            self.log_action(client_address, "Received UNP from unknown client")
            return
        
        username = self.active_clients[client_address]['username']
        self.log_action(client_address, f"Received UNP from {username}")
        
        # Remove file from published files registry
        if filename in self.published_files and username in self.published_files[filename]:
            self.published_files[filename].remove(username)
            if not self.published_files[filename]:
                del self.published_files[filename]
            
            self.socket.sendto(RESP_FILE_UNPUBLISHED.encode(), client_address)
            self.log_action(client_address, f"Sent OK to {username}")
        else:
            self.socket.sendto(RESP_FILE_UNPUB_FAILED.encode(), client_address)
            self.log_action(client_address, f"Sent ERR to {username}")
    
    def handle_list_active_peers(self, client_address: ClientAddress) -> None:
        """
        Send list of active peers to requesting client.
        
        Args:
            client_address: Client's address tuple
        """
        if client_address not in self.active_clients:
            return
        
        username = self.active_clients[client_address]['username']
        self.log_action(client_address, f"Received LAP from {username}")
        
        # Get active peers excluding requester
        active_peers = [
            data['username'] for addr, data in self.active_clients.items()
            if addr != client_address
        ]
        
        if active_peers:
            response = ", ".join(active_peers)
        else:
            response = RESP_NO_ACTIVE_PEERS
        
        self.socket.sendto(response.encode(), client_address)
        self.log_action(client_address, f"Sent OK to {username}")
    
    def handle_list_published_files(self, client_address: ClientAddress) -> None:
        """
        Send list of all published files to requesting client.
        
        Args:
            client_address: Client's address tuple
        """
        if client_address not in self.active_clients:
            return
        
        username = self.active_clients[client_address]['username']
        self.log_action(client_address, f"Received LPF from {username}")
        
        if self.published_files:
            response = ", ".join(self.published_files.keys())
        else:
            response = RESP_NO_PUBLISHED_FILES
        
        self.socket.sendto(response.encode(), client_address)
        self.log_action(client_address, f"Sent OK to {username}")
    
    def handle_search_files(self, client_address: ClientAddress, message: str) -> None:
        """
        Search for files containing substring (excluding requester's files).
        
        Args:
            client_address: Client's address tuple
            message: Message in format 'sch <substring>'
        """
        if client_address not in self.active_clients:
            self.log_action(client_address, "Received SCH from unknown client")
            return
        
        _, substring = parse_command(message)
        username = self.active_clients[client_address]['username']
        self.log_action(client_address, f"Received SCH from {username}")
        
        # Find matching files not published by requester
        matching_files = [
            filename for filename, publishers in self.published_files.items()
            if substring in filename and username not in publishers
        ]
        
        if matching_files:
            response = ", ".join(matching_files)
        else:
            response = RESP_NO_FILES_FOUND
        
        self.socket.sendto(response.encode(), client_address)
        self.log_action(client_address, f"Sent OK to {username}")
    
    def handle_get_request(self, client_address: ClientAddress, message: str) -> None:
        """
        Find active peer with requested file and provide TCP address.
        
        Args:
            client_address: Client's address tuple
            message: Message in format 'get <filename>'
        """
        _, filename = parse_command(message)
        
        requesting_username = self.active_clients[client_address]['username']
        self.log_action(client_address, f"Received GET from {requesting_username}")
        
        # Check if file is published
        if filename not in self.published_files:
            self.socket.sendto(RESP_FILE_NOT_FOUND.encode(), client_address)
            self.log_action(client_address, f"Sent ERR to {requesting_username}")
            return
        
        # Find active peer with the file
        for publisher_username in self.published_files[filename]:
            if publisher_username == requesting_username:
                continue
            
            # Find peer's address
            peer_address = None
            for addr, data in self.active_clients.items():
                if data['username'] == publisher_username:
                    peer_address = addr
                    break
            
            # If peer is active and has TCP address, return it
            if peer_address:
                tcp_address = self.active_clients[peer_address]['tcp_address']
                if tcp_address:
                    peer_ip, peer_port = tcp_address
                    response = f"{publisher_username} {peer_ip} {peer_port}"
                    self.socket.sendto(response.encode(), client_address)
                    self.log_action(client_address, f"Sent OK to {requesting_username}")
                    return
        
        # No active peer found with file
        self.socket.sendto(RESP_NO_ACTIVE_PEER_HAS_FILE.encode(), client_address)
        self.log_action(client_address, f"Sent ERR to {requesting_username}")
    
    def run(self) -> None:
        """Main server loop - process incoming messages."""
        while True:
            self.check_for_inactive_clients()
            
            try:
                message, client_address = self.socket.recvfrom(BUFFER_SIZE)
                message = message.decode().strip()
                
                # Route message to appropriate handler
                if message == MSG_HEARTBEAT:
                    self.process_heartbeat(client_address)
                
                elif message.startswith(CMD_PUBLISH):
                    self.handle_publish_file(client_address, message)
                
                elif message.startswith(CMD_UNPUBLISH):
                    self.handle_unpublish_file(client_address, message)
                
                elif message.startswith(MSG_TCP):
                    self.process_tcp_address(client_address, message)
                
                elif message == CMD_LIST_ACTIVE_PEERS:
                    self.handle_list_active_peers(client_address)
                
                elif message == CMD_LIST_PUBLISHED_FILES:
                    self.handle_list_published_files(client_address)
                
                elif message.startswith(CMD_SEARCH):
                    self.handle_search_files(client_address, message)
                
                elif message.startswith(CMD_GET):
                    self.handle_get_request(client_address, message)
                
                elif message.startswith("auth"):
                    self.authenticate_client(client_address, message)
                
                else:
                    self.socket.sendto(MSG_ERROR.encode(), client_address)
                    self.log_action(client_address, "Sent ERR (unknown command)")
            
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error processing message: {e}")
                continue


def main():
    """Entry point for server application."""
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        sys.exit(1)
    
    try:
        port = int(sys.argv[1])
        server = PeerSyncServer(port)
        server.run()
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
