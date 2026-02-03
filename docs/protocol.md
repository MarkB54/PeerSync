# PeerSync Protocol Specification v1.0

## Overview

PeerSync uses a hybrid protocol architecture combining UDP for control messages and TCP for data transfer.

## Protocol Stack

```
┌─────────────────────────────────┐
│     Application Layer           │
│  (PeerSync Protocol)          │
├─────────────────────────────────┤
│  Transport Layer                │
│  UDP (Control) | TCP (Data)     │
├─────────────────────────────────┤
│     Network Layer (IP)          │
├─────────────────────────────────┤
│   Data Link & Physical Layers   │
└─────────────────────────────────┘
```

## Message Format

### UDP Messages (Control Channel)

All UDP messages are plaintext, UTF-8 encoded.

#### Message Types

| Type | Format | Direction | Description |
|------|--------|-----------|-------------|
| AUTH | `auth <username> <password>` | C→S | Authentication request |
| OK | `OK` | S→C | Success response |
| ERR | `ERR` | S→C | Error response |
| HBT | `HBT` | C→S | Heartbeat signal |
| TCP | `TCP <ip> <port>` | C→S | Client TCP address |
| LAP | `lap` | C→S | List active peers request |
| LPF | `lpf` | C→S | List published files request |
| PUB | `pub <filename>` | C→S | Publish file |
| UNP | `unp <filename>` | C→S | Unpublish file |
| SCH | `sch <substring>` | C→S | Search files |
| GET | `get <filename>` | C→S | Request file download |

**Legend**: C = Client, S = Server

#### Authentication Messages

**Request**:
```
auth alice password123
```
- Command: `auth`
- Username: `alice`
- Password: `password123`
- Separator: Single space

**Response - Success**:
```
OK
```

**Response - Failure**:
```
ERR
```

#### Heartbeat Messages

**Request**:
```
HBT
```
- No parameters
- Sent every 2 seconds
- No response expected

#### TCP Address Registration

**Message**:
```
TCP 127.0.0.1 54321
```
- Command: `TCP`
- IP Address: `127.0.0.1`
- Port: `54321`
- Separator: Single space

#### List Active Peers

**Request**:
```
lap
```

**Response - With Peers**:
```
alice, bob, charlie
```
- Comma-separated list
- Excludes requesting client

**Response - No Peers**:
```
No active peers
```

#### List Published Files

**Request**:
```
lpf
```

**Response - With Files**:
```
document.txt, report.pdf, data.csv
```
- Comma-separated list

**Response - No Files**:
```
No published files
```

#### Publish File

**Request**:
```
pub document.txt
```

**Response - Success**:
```
File published successfully
```

**Response - Failure**:
```
ERR
```

#### Unpublish File

**Request**:
```
unp document.txt
```

**Response - Success**:
```
File unpublished successfully
```

**Response - Failure**:
```
File unpublication failed
```

#### Search Files

**Request**:
```
sch report
```
- Substring to search: `report`

**Response - Found**:
```
report.pdf, monthly_report.doc
```
- Comma-separated matches
- Excludes files published by requester

**Response - Not Found**:
```
No files found
```

#### Get File

**Request**:
```
get document.txt
```

**Response - Success**:
```
alice 127.0.0.1 54321
```
- Publisher username: `alice`
- TCP IP address: `127.0.0.1`
- TCP port: `54321`

**Response - File Not Found**:
```
File not found
```

**Response - No Active Peer**:
```
No active peer has this file
```

### TCP Messages (Data Channel)

TCP is used exclusively for peer-to-peer file transfers.

#### Connection Establishment

1. Requesting peer connects to publishing peer's TCP socket
2. Three-way handshake (handled by TCP)

#### File Request

**Message**:
```
filename.txt
```
- Plaintext filename
- UTF-8 encoded
- Terminated by send completion

#### File Transfer

**Format**: Binary stream
- Chunk size: 1024 bytes
- No message framing
- Transfer continues until file complete
- Connection closed by sender

**Pseudocode**:
```
while not end_of_file:
    chunk = read(1024 bytes)
    send(chunk)
close_connection()
```

#### Connection Termination

- Publishing peer closes connection after transfer completes
- Four-way handshake (handled by TCP)
- No explicit ACK required from application layer

## State Machines

### Client State Machine

```
┌─────────────┐
│ Disconnected│
└──────┬──────┘
       │ connect()
       ▼
┌─────────────┐
│Authenticating│
└──────┬──────┘
       │ auth OK
       ▼
┌─────────────┐     heartbeat
│   Active    │◄───────────────┐
│             │                │
│             ├────────────────┘
└──────┬──────┘     every 2s
       │ xit
       ▼
┌─────────────┐
│ Disconnected│
└─────────────┘
```

### Server Client Tracking

```
┌─────────────┐
│   Unknown   │
└──────┬──────┘
       │ AUTH OK
       ▼
┌─────────────┐    HBT received
│   Active    │◄───────────────┐
│ (heartbeat) │                │
│             ├────────────────┘
└──────┬──────┘     < 3s
       │ timeout (> 3s)
       ▼
┌─────────────┐
│   Removed   │
└─────────────┘
```

## Error Handling

### Client Errors

| Error | Handling |
|-------|----------|
| Authentication failure | Retry with new credentials |
| Connection refused | Check server is running |
| Timeout | Retry with exponential backoff |
| File not found | Inform user |
| Transfer failure | Close connection, inform user |

### Server Errors

| Error | Handling |
|-------|----------|
| Invalid message format | Send ERR response |
| Unknown client | Ignore or send ERR |
| Duplicate username | Send ERR |
| File already published | Silently succeed |
| File not published | Send failure response |