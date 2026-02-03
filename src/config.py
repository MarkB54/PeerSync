"""
Configuration constants for PeerSync P2P system.
"""

# Network Configuration
SERVER_HOST = '127.0.0.1'
BUFFER_SIZE = 1024
CHUNK_SIZE = 1024
MAX_TCP_CONNECTIONS = 10

# Timing Configuration
HEARTBEAT_INTERVAL = 2  # seconds
HEARTBEAT_TIMEOUT = 3   # seconds
SOCKET_TIMEOUT = 5      # seconds

# File Configuration
CREDENTIALS_FILE = "credentials.txt"
MAX_FILENAME_LENGTH = 255

# Protocol Messages
MSG_AUTH = "auth"
MSG_HEARTBEAT = "HBT"
MSG_OK = "OK"
MSG_ERROR = "ERR"
MSG_TCP = "TCP"

# Commands
CMD_LIST_ACTIVE_PEERS = "lap"
CMD_LIST_PUBLISHED_FILES = "lpf"
CMD_PUBLISH = "pub"
CMD_UNPUBLISH = "unp"
CMD_SEARCH = "sch"
CMD_GET = "get"
CMD_EXIT = "xit"

# Response Messages
RESP_FILE_PUBLISHED = "File published successfully"
RESP_FILE_UNPUBLISHED = "File unpublished successfully"
RESP_FILE_UNPUB_FAILED = "File unpublication failed"
RESP_NO_ACTIVE_PEERS = "No active peers"
RESP_NO_PUBLISHED_FILES = "No published files"
RESP_NO_FILES_FOUND = "No files found"
RESP_FILE_NOT_FOUND = "File not found"
RESP_NO_ACTIVE_PEER_HAS_FILE = "No active peer has this file"
RESP_WELCOME = "Welcome to PeerSync!"
RESP_AVAILABLE_COMMANDS = "Available commands are: get, lap, lpf, pub, sch, unp, xit."
RESP_AUTH_FAILED = "Authentication failed. Please try again."
RESP_GOODBYE = "Goodbye."

# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
