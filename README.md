# `send-recv-json`

Send and receive JSONs over byte streams - sockets, pipes, files, and more - using a universal, length-prefixed binary
framing scheme.

## Usage

- For `send_json`, provide a `send: Callable[[bytes], int]` function that accepts `bytes` and returns number of bytes sent.
  - If we cannot send anymore (i.e., byte stream is closed), throws `IOError`.
- For `recv_json`, provide a `recv: Callable[[int], bytes]` function that accepts a byte count and returns `bytes` with length `<=` that byte count.
  - If we cannot recv anymore (i.e., byte stream is closed), throws `EOFError`.

### Over TCP Sockets

```python
# coding=utf-8
from __future__ import print_function
import socket
from send_recv_json import send_json, recv_json

# Server
def server():
    sock = socket.socket()
    sock.bind(('localhost', 9999))
    sock.listen(1)
    conn, addr = sock.accept()
    # Receive a JSON object from the client
    obj = recv_json(conn.recv)
    print(obj)
    # Send a response
    send_json(conn.send, {"status": "ok"})
    conn.close()

# Client
def client():
    sock = socket.socket()
    sock.connect(('localhost', 9999))
    # Send a JSON object
    send_json(sock.send, {"msg": "hello"})
    # Receive a response
    resp = recv_json(sock.recv)
    print(resp)
    sock.close()

# Run server() in one process, client() in another.
```

### Between Processes (pipes, os.read/os.write)

```python
# coding=utf-8
from __future__ import print_function
import os
from send_recv_json import send_json, recv_json

read_file_descriptor, write_file_descriptor = os.pipe()

# In child process:
send_json(lambda b: os.write(write_file_descriptor, b), {"pid": 123})

# In parent process:
data = recv_json(lambda n: os.read(read_file_descriptor, n))
print(data)  # Output: {'pid': 123}
```

### Logging to and Reading from Files

```python
# coding=utf-8
from __future__ import print_function
from os import write
from os.path import getsize
from send_recv_json import send_json, recv_json

with open('events.log', 'wb') as f:
    # In Python 2, the built-in file object's `.write()` method returns `None` (both in text and binary mode).
    # In Python 3, it returns the number of chars/bytes written.
    # For compatibility, we use os.write instead
    send_json(lambda data: write(f.fileno(), data), {"event": "start", "user": "alice"})
    send_json(lambda data: write(f.fileno(), data), {"event": "stop", "user": "bob"})

with open('events.log', 'rb') as f:
    while True:
        try:
            print(recv_json(f.read))
        except EOFError:
            break
```

## Installation

```sh
pip install send-recv-json
```

## Use Case Examples

- Passing objects between local processes over pipes
- High-throughput network messaging (microservices, custom servers)
- Durable event logging in binary files
- Embedded systems communication
- Specialized "glue" between Python and other languages/tools
- Cross-language communication (cloud-native, rapid scripts, etc.)

## Philosophy

Unlike “kitchen sink” frameworks, `send-recv-json` does just one thing - robust, high-performance JSON
serialization/deserialization and framing over byte streams.

- No heavy abstractions, magic, or dependencies.
- Drop in as a primitive under your protocol, event system, or microservice stack.

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).