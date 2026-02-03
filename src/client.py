"""
PeerSync Client - P2P file sharing client implementation.

This module implements the client component that:
- Authenticates with the server
- Sends periodic heartbeats
- Publishes and searches for files
- Downloads files from peers via TCP
- Uploads files to peers via TCP
"""

import socket
import sys
import time
import threading
from typing import Optional, Tuple

from config import (
    SERVER_HOST, BUFFER_SIZE, CHUNK_SIZE, MAX_TCP_CONNECTIONS,
    HEARTBEAT_INTERVAL,
    MSG_HEARTBEAT, MSG_OK,
    CMD_LIST_ACTIVE_PEERS, CMD_LIST_PUBLISHED_FILES,
    CMD_PUBLISH, CMD_UNPUBLISH, CMD_SEARCH, CMD_GET, CMD_EXIT,
    RESP_NO_ACTIVE_PEERS, RESP_NO_PUBLISHED_FILES, RESP_NO_FILES_FOUND,
    RESP_FILE_NOT_FOUND, RESP_NO_ACTIVE_PEER_HAS_FILE,
    RESP_WELCOME, RESP_AVAILABLE_COMMANDS, RESP_AUTH_FAILED, RESP_GOODBYE
)


class PeerSyncClient:
    """Client for PeerSync P2P system."""
    
    def __init__(self, server_port: int):
        """
        Initialise the PeerSync client.
        
        Args:
            server_port: Server's UDP port number
        """
        self.server_port = server_port
        self.server_address = (SERVER_HOST, server_port)
        
        # Create UDP socket for server communication
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Create TCP welcoming socket for file transfers
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind((SERVER_HOST, 0))  # Bind to random available port
        self.tcp_socket.listen(MAX_TCP_CONNECTIONS)
        
        self.tcp_port = self.tcp_socket.getsockname()[1]
        self.authenticated = False
    
    def authenticate(self) -> bool:
        """
        Authenticate with the server.
        
        Returns:
            bool: True if authentication successful
        """
        while True:
            username = input("Enter username: ")
            password = input("Enter password: ")
            
            # Send authentication request
            auth_message = f"auth {username} {password}"
            self.udp_socket.sendto(auth_message.encode(), self.server_address)
            
            # Get response
            response, _ = self.udp_socket.recvfrom(BUFFER_SIZE)
            
            if response.decode() == MSG_OK:
                print(RESP_WELCOME)
                print(RESP_AVAILABLE_COMMANDS)
                
                # Send TCP address to server
                tcp_message = f"TCP {SERVER_HOST} {self.tcp_port}"
                self.udp_socket.sendto(tcp_message.encode(), self.server_address)
                
                self.authenticated = True
                return True
            else:
                print(RESP_AUTH_FAILED)
    
    def send_heartbeat(self) -> None:
        """Send heartbeat messages to server every HEARTBEAT_INTERVAL seconds."""
        while True:
            time.sleep(HEARTBEAT_INTERVAL)
            self.udp_socket.sendto(MSG_HEARTBEAT.encode(), self.server_address)
    
    def list_active_peers(self) -> None:
        """Request and display list of active peers."""
        self.udp_socket.sendto(CMD_LIST_ACTIVE_PEERS.encode(), self.server_address)
        
        response, _ = self.udp_socket.recvfrom(BUFFER_SIZE)
        message = response.decode()
        
        if message == RESP_NO_ACTIVE_PEERS:
            print(RESP_NO_ACTIVE_PEERS)
        else:
            peers = message.split(", ")
            count = len(peers)
            print(f"{count} active peer{'s' if count != 1 else ''}:")
            for peer in peers:
                print(peer)
    
    def list_published_files(self) -> None:
        """Request and display list of all published files."""
        self.udp_socket.sendto(CMD_LIST_PUBLISHED_FILES.encode(), self.server_address)
        
        response, _ = self.udp_socket.recvfrom(BUFFER_SIZE)
        message = response.decode()
        
        if message == RESP_NO_PUBLISHED_FILES:
            print(message)
        else:
            files = message.split(", ")
            count = len(files)
            print(f"{count} file{'s' if count != 1 else ''} published:")
            for file in files:
                print(file)
    
    def publish_file(self, filename: str) -> None:
        """
        Publish a file to the network.
        
        Args:
            filename: Name of file to publish
        """
        command = f"{CMD_PUBLISH} {filename}"
        self.udp_socket.sendto(command.encode(), self.server_address)
        
        response, _ = self.udp_socket.recvfrom(BUFFER_SIZE)
        print(response.decode())
    
    def unpublish_file(self, filename: str) -> None:
        """
        Unpublish a file from the network.
        
        Args:
            filename: Name of file to unpublish
        """
        command = f"{CMD_UNPUBLISH} {filename}"
        self.udp_socket.sendto(command.encode(), self.server_address)
        
        response, _ = self.udp_socket.recvfrom(BUFFER_SIZE)
        print(response.decode())
    
    def search_files(self, substring: str) -> None:
        """
        Search for files containing substring.
        
        Args:
            substring: Search substring
        """
        command = f"{CMD_SEARCH} {substring}"
        self.udp_socket.sendto(command.encode(), self.server_address)
        
        response, _ = self.udp_socket.recvfrom(BUFFER_SIZE)
        message = response.decode()
        
        if message == RESP_NO_FILES_FOUND:
            print(message)
        else:
            files = message.split(", ")
            count = len(files)
            print(f"{count} file{'s' if count != 1 else ''} found:")
            for file in files:
                print(file)
    
    def download_file(self, peer_ip: str, peer_port: int, filename: str) -> bool:
        """
        Download file from peer via TCP.
        
        Args:
            peer_ip: Peer's IP address
            peer_port: Peer's TCP port
            filename: Name of file to download
        
        Returns:
            bool: True if download successful
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
                tcp_socket.connect((peer_ip, peer_port))
                tcp_socket.sendall(filename.encode())
                
                with open(filename, "wb") as file:
                    while True:
                        chunk = tcp_socket.recv(CHUNK_SIZE)
                        if not chunk:
                            break
                        file.write(chunk)
                
                return True
        
        except Exception as e:
            return False
    
    def get_file(self, filename: str) -> None:
        """
        Request file download from network.
        
        Args:
            filename: Name of file to download
        """
        command = f"{CMD_GET} {filename}"
        self.udp_socket.sendto(command.encode(), self.server_address)
        
        response, _ = self.udp_socket.recvfrom(BUFFER_SIZE)
        message = response.decode()
        
        if message == RESP_NO_ACTIVE_PEER_HAS_FILE:
            print(RESP_NO_ACTIVE_PEER_HAS_FILE)
        elif message == RESP_FILE_NOT_FOUND:
            print(RESP_FILE_NOT_FOUND)
        else:
            # Parse peer information
            peer_username, peer_ip, peer_port = message.split()
            
            # Download file
            if self.download_file(peer_ip, int(peer_port), filename):
                print(f"{filename} downloaded successfully from {peer_username}")
            else:
                print(f"Failed to download {filename} from {peer_username}")
    
    def upload_file(self, peer_socket: socket.socket, 
                   peer_address: Tuple[str, int], filename: str) -> None:
        """
        Upload file to peer via TCP.
        
        Args:
            peer_socket: Connected socket to peer
            peer_address: Peer's address tuple
            filename: Name of file to upload
        """
        try:
            with open(filename, "rb") as file:
                while True:
                    chunk = file.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    peer_socket.sendall(chunk)
        
        except FileNotFoundError:
            print(f"File {filename} not found.")
        except Exception as e:
            print(f"Error during upload to {peer_address}: {e}")
        finally:
            peer_socket.close()
    
    def listen_for_downloads(self) -> None:
        """Listen for incoming download requests on TCP socket."""
        while True:
            peer_socket, peer_address = self.tcp_socket.accept()
            
            # Receive filename request
            filename = peer_socket.recv(BUFFER_SIZE).decode().strip()
            
            # Handle upload in separate thread
            upload_thread = threading.Thread(
                target=self.upload_file,
                args=(peer_socket, peer_address, filename)
            )
            upload_thread.start()
    
    def handle_commands(self) -> None:
        """Main command loop for user input."""
        while True:
            command = input("> ").strip()
            
            if command == CMD_EXIT:
                print(RESP_GOODBYE)
                break
            
            elif command == CMD_LIST_ACTIVE_PEERS:
                self.list_active_peers()
            
            elif command == CMD_LIST_PUBLISHED_FILES:
                self.list_published_files()
            
            elif command.startswith(f"{CMD_PUBLISH} "):
                filename = command.split(" ", 1)[1]
                self.publish_file(filename)
            
            elif command.startswith(f"{CMD_UNPUBLISH} "):
                filename = command.split(" ", 1)[1]
                self.unpublish_file(filename)
            
            elif command.startswith(f"{CMD_SEARCH} "):
                substring = command.split(" ", 1)[1]
                self.search_files(substring)
            
            elif command.startswith(f"{CMD_GET} "):
                filename = command.split(" ", 1)[1]
                self.get_file(filename)
            
            # Ignore invalid commands
    
    def run(self) -> None:
        """Start the client application."""
        # Authenticate with server
        if not self.authenticate():
            return
        
        # Start heartbeat thread
        heartbeat_thread = threading.Thread(target=self.send_heartbeat)
        heartbeat_thread.daemon = True #automatically finishes when the main thread finishes
        heartbeat_thread.start()
        
        # Start download listener thread
        download_thread = threading.Thread(target=self.listen_for_downloads)
        download_thread.daemon = True
        download_thread.start()
        
        # Handle user commands in main thread
        self.handle_commands()
        
        # Cleanup
        self.udp_socket.close()
        self.tcp_socket.close()


def main():
    """Entry point for client application."""
    if len(sys.argv) != 2:
        print("Usage: python client.py <server_port>")
        sys.exit(1)
    
    try:
        server_port = int(sys.argv[1])
        client = PeerSyncClient(server_port)
        client.run()
    except KeyboardInterrupt:
        print("\nClient shutting down...")
    except Exception as e:
        print(f"Client error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
