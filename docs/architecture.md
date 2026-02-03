# PeerSync Architecture

## System Overview

PeerSync is a peer-to-peer file-sharing system that uses a hybrid architecture combining centralised coordination with distributed file transfer.

## Architecture Components

### 1. Central Server
**Purpose**: Coordinate peer discovery and maintain network state

**Responsibilities**:
- Client authentication
- Active peer tracking
- File publication registry
- Peer discovery for file requests
- Heartbeat monitoring

**Communication**: UDP only

### 2. Client Application
**Purpose**: User interface for file sharing

**Responsibilities**:
- User authentication
- Command processing
- Heartbeat transmission
- File publication/unpublication
- P2P file transfers

**Communication**: UDP (server) + TCP (peers)

## Communication Protocols

### UDP Protocol (Control Channel)

Used for all server-client communication:

| Message Type | Format | Direction | Description |
|-------------|---------|-----------|-------------|
| AUTH | `auth <username> <password>` | Client → Server | Authentication request |
| OK | `OK` | Server → Client | Success response |
| ERR | `ERR` | Server → Client | Error response |
| HBT | `HBT` | Client → Server | Heartbeat signal |
| TCP | `TCP <ip> <port>` | Client → Server | Client's TCP address |
| LAP | `lap` | Client → Server | List active peers |
| LPF | `lpf` | Client → Server | List published files |
| PUB | `pub <filename>` | Client → Server | Publish file |
| UNP | `unp <filename>` | Client → Server | Unpublish file |
| SCH | `sch <substring>` | Client → Server | Search files |
| GET | `get <filename>` | Client → Server | Request file |

### TCP Protocol (Data Channel)

Used for peer-to-peer file transfers:

1. **Connection Establishment**
   - Requesting peer connects to publishing peer's TCP socket
   
2. **File Request**
   - Requesting peer sends filename (text)
   
3. **File Transfer**
   - Publishing peer streams file in 1024-byte chunks
   - No explicit ACK - TCP handles reliability
   
4. **Connection Termination**
   - Publishing peer closes connection after transfer completes

## Data Structures

### Server State

```python
# Active clients tracking
active_clients = {
    (ip, port): {
        'username': str,
        'last_heartbeat': float,  # timestamp
        'tcp_address': (str, int) # (ip, port)
    }
}

# Published files registry
published_files = {
    'filename': ['username1', 'username2', ...]
}

# Credentials database
credentials = {
    'username': 'password'
}
```

### Client State

```python
# Server connection
server_address = (ip, port)
udp_socket = socket.socket(SOCK_DGRAM)

# P2P connection
tcp_socket = socket.socket(SOCK_STREAM)
tcp_port = int  # dynamically assigned
```

## Sequence Diagrams

### Authentication Flow

```
Client                Server
  |                     |
  |--auth user pass---->|
  |                     |(validate)
  |<------OK/ERR--------|
  |                     |
  |--TCP ip port------->|
  |                     |(store)
  |                     |
  |------HBT----------->| (every 2s)
  |------HBT----------->|
```

### File Download Flow

```
Client A        Server        Client B
  |               |              |
  |--get file---->|              |
  |               |(find peer)   |
  |<--peer info---|              |
  |               |              |
  |-------TCP connect---------->|
  |<-----file data stream--------|
  |               |              |
```

### Heartbeat & Timeout

```
Client          Server
  |               |
  |----HBT------->| (t=0s)
  |               | last_heartbeat = 0
  |               |
  |----HBT------->| (t=2s)
  |               | last_heartbeat = 2
  |               |
  | (crash)       |
  |               | (t=3s: check)
  |               | (5-2=3 > timeout)
  |               | remove client
```

## Threading Model

### Server
- **Single-threaded** event loop
- Processes messages sequentially
- Checks for inactive clients on every iteration

### Client
- **Main thread**: User input and command processing
- **Heartbeat thread**: Sends HBT every 2 seconds
- **TCP listener thread**: Accepts incoming connections
- **Transfer threads**: One per active file transfer (short-lived)

## Security Considerations

### Current Implementation
- Plain text credentials
- No encryption on any channel
- Local network only (127.0.0.1)
- No authentication tokens
- No rate limiting

### Production Recommendations
1. **Authentication**: Hash passwords with bcrypt/argon2
2. **Encryption**: TLS/SSL for TCP, DTLS for UDP
3. **Authorisation**: Token-based auth with expiry
4. **Integrity**: File checksums (SHA-256)
5. **Rate Limiting**: Per-client request throttling




