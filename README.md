# 🗨️ Chatroom Server

A simple multi-user chat server using Python's `asyncio` standard library. Users connect by TCP, log in with a unique username, broadcast messages, and list active users in real time.


## Features

- Multiple concurrent connections (asyncio)
- Unique user login (`LOGIN <username>`)
- Message broadcasting (`MSG <text>`)
- Active user list (`WHO`)
- Client join/leave notifications


## Getting Started

### Prerequisites

- Python 3.7 or newer

### Running the Server
```
uv run server.py
```

### Connecting as a Client

Open another terminal and use `nc` (netcat):
```
nc localhost 4000
```
