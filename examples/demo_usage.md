# PeerSync Demo Usage Guide

This guide walks through a typical PeerSync session with multiple clients.

## Setup

### 1. Prepare Credentials

Create `credentials.txt` in the project root:
```
alice password123
bob secretpass
charlie mypass456
```

### 2. Start the Server

```bash
cd PeerSync
python src/server.py 5000
```

Expected output:
```
Server started on 127.0.0.1:5000
```

## Scenario: Three Users Sharing Files

### Client 1: Alice

**Terminal 1:**
```bash
python src/client.py 5000
```

**Interaction:**
```
Enter username: alice
Enter password: password123
Welcome to PeerSync!
Available commands are: get, lap, lpf, pub, sch, unp, xit.
> pub report.pdf
File published successfully
> pub presentation.pptx
File published successfully
> lap
2 active peers:
bob
charlie
```

### Client 2: Bob

**Terminal 2:**
```bash
python src/client.py 5000
```

**Interaction:**
```
Enter username: bob
Enter password: secretpass
Welcome to PeerSync!
Available commands are: get, lap, lpf, pub, sch, unp, xit.
> pub code.py
File published successfully
> lpf
3 files published:
report.pdf
presentation.pptx
code.py
> sch report
1 file found:
report.pdf
> get report.pdf
report.pdf downloaded successfully from alice
```

### Client 3: Charlie

**Terminal 3:**
```bash
python src/client.py 5000
```

**Interaction:**
```
Enter username: charlie
Enter password: mypass456
Welcome to PeerSync!
Available commands are: get, lap, lpf, pub, sch, unp, xit.
> lap
2 active peers:
alice
bob
> sch p
2 files found:
report.pdf
presentation.pptx
> get presentation.pptx
presentation.pptx downloaded successfully from alice
> get code.py
code.py downloaded successfully from bob
> xit
Goodbye.
```

## Server Log Output

While the demo is running, the server displays activity logs:

```
2025-01-30 10:15:23.456: ('127.0.0.1', 54321) Received AUTH from alice
2025-01-30 10:15:23.457: ('127.0.0.1', 54321) Sent OK to alice
2025-01-30 10:15:25.123: ('127.0.0.1', 54322) Received AUTH from bob
2025-01-30 10:15:25.124: ('127.0.0.1', 54322) Sent OK to bob
2025-01-30 10:15:27.789: ('127.0.0.1', 54323) Received AUTH from charlie
2025-01-30 10:15:27.790: ('127.0.0.1', 54323) Sent OK to charlie
2025-01-30 10:15:29.456: ('127.0.0.1', 54321) Received HBT from alice
2025-01-30 10:15:30.234: ('127.0.0.1', 54321) Received PUB from alice
2025-01-30 10:15:30.235: ('127.0.0.1', 54321) Sent OK to alice
2025-01-30 10:15:31.123: ('127.0.0.1', 54322) Received HBT from bob
2025-01-30 10:15:32.567: ('127.0.0.1', 54322) Received PUB from bob
2025-01-30 10:15:32.568: ('127.0.0.1', 54322) Sent OK to bob
2025-01-30 10:15:33.789: ('127.0.0.1', 54323) Received HBT from charlie
2025-01-30 10:15:35.234: ('127.0.0.1', 54323) Received LAP from charlie
2025-01-30 10:15:35.235: ('127.0.0.1', 54323) Sent OK to charlie
2025-01-30 10:15:40.123: ('127.0.0.1', 54322) Received GET from bob
2025-01-30 10:15:40.124: ('127.0.0.1', 54322) Sent OK to bob
```

## Common Commands Reference

| Command | Example | Description |
|---------|---------|-------------|
| `lap` | `lap` | List all active peers |
| `lpf` | `lpf` | List all published files |
| `pub` | `pub document.pdf` | Publish a file |
| `unp` | `unp document.pdf` | Unpublish a file |
| `sch` | `sch report` | Search for files containing "report" |
| `get` | `get report.pdf` | Download file from peer |
| `xit` | `xit` | Exit the application |

## Testing File Transfers

### Prepare Test Files

```bash
# Create some test files in your working directory
echo "This is a test document" > document.txt
echo "Sample data" > data.csv
dd if=/dev/urandom of=largefile.bin bs=1M count=10  # 10MB file
```

### Verify Transfer

```bash
# On publishing client
> pub document.txt
File published successfully

# On downloading client
> sch document
1 file found:
document.txt
> get document.txt
document.txt downloaded successfully from alice

# Verify file integrity
md5sum document.txt  # Compare checksums
```

## Troubleshooting

### Connection Issues

**Problem**: Client can't connect to server
```
Usage: python client.py <server_port>
```

**Solution**: Ensure server is running and port matches:
```bash
# Check server is running
ps aux | grep server.py

# Verify port number
netstat -an | grep 5000
```

### Authentication Failures

**Problem**: "Authentication failed. Please try again."

**Solutions**:
1. Check credentials.txt exists
2. Verify username/password format (space-separated)
3. Ensure user isn't already logged in

### File Transfer Failures

**Problem**: "Failed to download {filename} from {peer}"

**Possible causes**:
1. File doesn't exist on peer's system
2. Peer disconnected
3. Network timeout

**Solution**: Verify file exists and peer is active:
```
> lap          # Check peer is active
> lpf          # Verify file is published
> sch filename # Search for the file
```

### Heartbeat Timeout

**Problem**: Client disappears from active peers list

**Explanation**: Clients send heartbeats every 2 seconds. If server doesn't receive heartbeat for 3 seconds, client is removed.

**Solutions**:
1. Check network connectivity
2. Ensure client process is running
3. Restart client if crashed

## Advanced Scenarios

### Concurrent Downloads

Multiple clients can download from the same peer simultaneously:

```bash
# Client A publishes large file
> pub movie.mp4

# Clients B, C, D all download at once
> get movie.mp4  # From client B
> get movie.mp4  # From client C
> get movie.mp4  # From client D
```

The TCP welcoming socket accepts up to 10 concurrent connections.

### File Unpublishing During Transfer

If a peer unpublishes a file while another client is downloading:
- **Current transfer**: Continues to completion
- **New requests**: Fail with "File not found"

```bash
# Client A
> pub data.csv

# Client B starts download
> get data.csv   # Transfer begins

# Client A unpublishes
> unp data.csv
File unpublished successfully

# Client B's transfer completes successfully
data.csv downloaded successfully from alice
```

## Performance Tips

1. **Large Files**: Consider compression before publishing
2. **Network Load**: Limit concurrent transfers
3. **Cleanup**: Unpublish files no longer needed
4. **Monitoring**: Watch server logs for bottlenecks
