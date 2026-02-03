"""
Shared utility functions for PeerSync P2P system.
"""

import time
from datetime import datetime
from typing import Dict, Tuple


def get_timestamp() -> str:
    """
    Get current timestamp formatted to milliseconds.
    
    Returns:
        str: Timestamp in format 'YYYY-MM-DD HH:MM:SS.mmm'
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def format_client_address(client_address: Tuple[str, int]) -> str:
    """
    Format client address for logging.
    
    Args:
        client_address: Tuple of (IP address, port)
    
    Returns:
        str: Formatted address string
    """
    return f"{client_address[0]}:{client_address[1]}"


def parse_command(message: str) -> Tuple[str, str]:
    """
    Parse command message into command and argument.
    
    Args:
        message: Raw message string
    
    Returns:
        Tuple of (command, argument)
    """
    parts = message.split(' ', 1)
    command = parts[0]
    argument = parts[1] if len(parts) > 1 else ""
    return command, argument


def is_valid_filename(filename: str, max_length: int = 255) -> bool:
    """
    Validate filename.
    
    Args:
        filename: Filename to validate
        max_length: Maximum allowed length
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not filename or len(filename) > max_length:
        return False
    
    # Check for invalid characters
    invalid_chars = ['/', '\\', '\0', '\n', '\r']
    return not any(char in filename for char in invalid_chars)


def format_file_list(files: list, singular: str, plural: str) -> str:
    """
    Format list of files for display.
    
    Args:
        files: List of filenames
        singular: Singular form message
        plural: Plural form message
    
    Returns:
        str: Formatted string for display
    """
    if not files:
        return ""
    
    num_files = len(files)
    header = f"1 {singular}:" if num_files == 1 else f"{num_files} {plural}:"
    items = '\n'.join(files)
    return f"{header}\n{items}"


def calculate_elapsed_time(start_time: float) -> float:
    """
    Calculate elapsed time since start_time.
    
    Args:
        start_time: Starting timestamp from time.time()
    
    Returns:
        float: Elapsed time in seconds
    """
    return time.time() - start_time


def load_credentials(filepath: str) -> Dict[str, str]:
    """
    Load credentials from file.
    
    Args:
        filepath: Path to credentials file
    
    Returns:
        Dict mapping username to password
    
    Raises:
        FileNotFoundError: If credentials file doesn't exist
        ValueError: If file format is invalid
    """
    credentials = {}
    
    try:
        with open(filepath, 'r') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split(' ')
                if len(parts) != 2:
                    raise ValueError(
                        f"Invalid format at line {line_num}: expected 'username password'"
                    )
                
                username, password = parts
                credentials[username] = password
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Credentials file not found: {filepath}")
    
    return credentials
