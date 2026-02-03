# PeerSync - P2P File Sharing System

A peer-to-peer file-sharing application built with Python, featuring UDP/TCP communication, multithreaded architecture, and real-time heartbeat monitoring.

## 🚀 Features

- **Dual-Protocol Communication**: UDP for control messages, TCP for file transfers
- **Multithreaded Architecture**: Concurrent handling of heartbeats, file transfers, and user commands
- **Real-time Monitoring**: Heartbeat mechanism with automatic inactive client detection (3-second timeout)
- **File Management**: Publish, unpublish, search, and download files from active peers
- **Concurrent File Transfers**: Support for multiple simultaneous downloads/uploads
- **Error Handling**: Comprehensive exception handling and connection management

## 📋 Table of Contents

- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Commands](#commands)
- [Technical Details](#technical-details)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

## 🏗️ Architecture

```
┌─────────────┐                    ┌─────────────┐
│   Client    │    UDP (Control)   │   Server    │
│             │◄──────────────────►│             │
│  ┌───────┐  │                    │             │
│  │  UDP  │  │  Heartbeats (HBT)  │  ┌───────┐  │
│  │Socket │  │  Commands          │  │  UDP  │  │
│  └───────┘  │  Authentication    │  │Socket │  │
│             │                    │  └───────┘  │
│  ┌───────┐  │                    │             │
│  │  TCP  │  │    TCP (Data)      │             │
│  │Socket │  │◄──────────────────►│             │
│  └───────┘  │  File Transfers    │             │
│             │                    │             │
└─────────────┘                    └─────────────┘
        ▲                                   ▲
        │         TCP Connection            │
        │         (File Transfer)           │
        └───────────────────────────────────┘
             Peer-to-Peer Transfer
```

### Key Components

1. **Server (UDP)**: Central coordinator managing active peers, published files, and authentication
2. **Client (UDP)**: Communicates with server for control operations and peer discovery
3. **Client (TCP)**: Handles peer-to-peer file transfers with chunked streaming

## 💻 Installation

### Prerequisites

- Python 3.7+
- No external dependencies (uses only standard library)

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/PeerSync.git
cd PeerSync

# Install in development mode
pip install -e .
```

### Configuration

Create a `credentials.txt` file in the project root:

```
alice password123
bob secretpass
charlie mypass456
```

Format: `username password` (space-separated, one per line)

## 🎮 Usage

### Starting the Server

```bash
python src/server.py <port>

# Example
python src/server.py 5000
```

### Starting a Client

```bash
python src/client.py <server_port>

# Example
python src/client.py 5000
```

### Authentication Flow

1. Client connects to server via UDP
2. User enters username and password
3. Server validates credentials and adds client to active peers
4. Client sends TCP address for peer-to-peer transfers
5. Heartbeat thread begins (every 2 seconds)

## 📝 Commands

Once authenticated, clients can use the following commands:

| Command | Description | Example |
|---------|-------------|---------|
| `lap` | List all active peers | `lap` |
| `lpf` | List all published files | `lpf` |
| `pub <filename>` | Publish a file | `pub document.pdf` |
| `unp <filename>` | Unpublish a file | `unp document.pdf` |
| `sch <substring>` | Search for files containing substring | `sch report` |
| `get <filename>` | Download file from peer | `get report.txt` |
| `xit` | Exit the application | `xit` |

## 🔧 Technical Details

### Communication Protocols

- **UDP (Control Channel)**
  - Port: User-specified server port
  - Purpose: Authentication, heartbeats, file discovery, peer coordination
  - Buffer Size: 1024 bytes

- **TCP (Data Channel)**
  - Port: Dynamically assigned per client
  - Purpose: Peer-to-peer file transfers
  - Chunk Size: 1024 bytes
  - Max Connections: 10 concurrent

### Multithreading Architecture

```python
Main Thread          Thread 1              Thread 2
───────────          ────────              ────────
User Input    →      Heartbeat Timer  →   TCP Listener
Commands             (2s interval)        (Accept connections)
                                               │
                                               ├─► Transfer Thread 1
                                               ├─► Transfer Thread 2
                                               └─► Transfer Thread N
```

### Heartbeat Mechanism

- **Interval**: 2 seconds
- **Timeout**: 3 seconds
- **Detection**: Server checks for inactive clients on every message received
- **Cleanup**: Automatic removal of clients exceeding timeout threshold

### File Transfer Protocol

1. Requesting client sends `get <filename>` to server
2. Server finds active peer with the file
3. Server returns peer's TCP address to requesting client
4. Requesting client establishes TCP connection with peer
5. Peer streams file in 1024-byte chunks
6. Connection closes automatically upon completion


## 🎯 Performance Metrics

- **Concurrent Connections**: Supports 10+ simultaneous TCP connections
- **File Transfer**: Chunked streaming with 1024-byte blocks
- **Latency**: Sub-second peer discovery and connection establishment
- **Reliability**: Automatic reconnection handling with timeout detection

## 🔒 Security Considerations

- Credentials stored in plain text (suitable for testing purposes - but not production ready)
- No encryption on control or data channels
- Local network operation (127.0.0.1) by default
- **Production Recommendations**:
  - Implement password hashing (bcrypt/argon2)
  - Add TLS/SSL for TCP connections
  - Implement authentication tokens with expiry
  - Add rate limiting and DDoS protection

## 🐛 Known Limitations

- Single-server architecture (no load balancing)
- No file integrity verification (checksums/hashes)
- Limited to local network by default
- Fixed buffer sizes (1024 bytes)

## 🚦 Future Enhancements

- [ ] Add file integrity checking (MD5/SHA256 hashes)
- [ ] Implement progress bars for file transfers
- [ ] Add configuration file (YAML/JSON)
- [ ] Create GUI interface
- [ ] Add logging framework
- [ ] Implement NAT traversal for WAN operation
- [ ] Add file compression during transfer
- [ ] Create Docker container support

## 📊 Testing

```bash
# Run unit tests
python -m pytest tests/

# Run integration tests
python -m pytest tests/test_integration.py

# Run with coverage
python -m pytest --cov=src tests/
```
