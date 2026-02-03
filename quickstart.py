#!/usr/bin/env python3
"""
Quick start script for PeerSync demo.

This script sets up a demo environment with sample credentials
and provides instructions for running the server and clients.
"""

import os
import sys
from pathlib import Path


def create_credentials():
    """Create sample credentials file if it doesn't exist."""
    credentials_file = Path("credentials.txt")
    
    if credentials_file.exists():
        print("✓ credentials.txt already exists")
        return
    
    credentials = """# Sample credentials for PeerSync demo
# Format: username password (space-separated)
alice password123
bob secretpass
charlie mypass456
"""
    
    credentials_file.write_text(credentials)
    print("✓ Created credentials.txt with sample users")


def create_sample_files():
    """Create sample files for testing."""
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    files = {
        "document.txt": "This is a sample document for testing file transfers.",
        "report.pdf": "Mock PDF content - imagine this is a real PDF file.",
        "data.csv": "name,value\nalice,100\nbob,200\ncharlie,300",
    }
    
    for filename, content in files.items():
        file_path = test_dir / filename
        if not file_path.exists():
            file_path.write_text(content)
    
    print(f"✓ Created sample files in {test_dir}/")


def print_instructions():
    """Print usage instructions."""
    print("\n" + "="*70)
    print("PeerSync Quick Start Guide")
    print("="*70)
    print("\n1. Start the server:")
    print("   python3 src/server.py 5000")
    print("\n2. In separate terminals, start clients:")
    print("   python3 src/client.py 5000")
    print("\n3. Login with sample credentials:")
    print("   Username: alice    Password: password123")
    print("   Username: bob      Password: secretpass")
    print("   Username: charlie  Password: mypass456")
    print("\n4. Try these commands:")
    print("   lap              - List active peers")
    print("   pub filename     - Publish a file")
    print("   lpf              - List all published files")
    print("   sch substring    - Search for files")
    print("   get filename     - Download a file")
    print("   xit              - Exit")
    print("\n5. Sample files available in test_files/:")
    print("   - document.txt")
    print("   - report.pdf")
    print("   - data.csv")
    print("\nFor more details, see examples/demo_usage.md")
    print("="*70 + "\n")


def check_python_version():
    """Check if Python version is sufficient."""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")


def main():
    """Main setup function."""
    print("\nPeerSync Demo Setup")
    print("-" * 40)
    
    check_python_version()
    create_credentials()
    create_sample_files()
    print_instructions()
    
    print("Setup complete! Ready to run PeerSync.\n")


if __name__ == "__main__":
    main()
