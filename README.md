# Q1: TCP Socket Server (text-based)

A TCP client-server application built with Python's native `socket` library. The server supports multiple simultaneous clients via threads and responds to a set of text-based (UTF-8) commands for remote directory navigation.

## Problem Statement

Proposed by Prof. Rodrigo Campiolo as part of the Distributed Systems course. The goal is to implement a multi-client TCP server that handles user authentication and remote directory navigation. Each user has an isolated area on the server and can list files, list directories, and navigate the directory tree, all through a custom text-based protocol over TCP.

---

## Project Structure

```
q1/
├── server/
│   ├── server.py           # Entry point: opens socket and accepts connections
│   ├── client_handler.py   # Command handlers for each connected client
│   ├── users.py            # Registered users and hashed passwords (SHA-512)
│   ├── protocol.py         # send_utf / recv_utf with length-prefix framing
│   └── files/              # User storage area (auto-created on first login)
│       └── <username>/     # Each user has their own isolated directory
└── client/
    ├── client.py           # Entry point: connects to server and sends commands
    └── protocol.py         # send_utf / recv_utf with length-prefix framing
```

---

## Requirements

- Python 3
- No external libraries required

---

## How to Run

Open **two terminals** at the project root.

**Terminal 1: Start the server:**

```bash
cd q1/server
python server.py
```

**Terminal 2: Start the client:**

```bash
cd q1/client
python client.py
```

> The server listens on `0.0.0.0:6711` (all interfaces).  
> The client connects to `127.0.0.1:6711` (localhost).  
> To connect from another machine, change `HOST` in `client.py` to the server's IP address.

---

## Supported Commands

All messages are exchanged as UTF-8 strings over TCP with a 4-byte length prefix to avoid message boundary issues.

| Command                  | Description                                                                                                   | Response                              |
| ------------------------ | ------------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| `CONNECT user, password` | Authenticates the user. Password must be typed in plain text: the client hashes it to SHA-512 before sending. | `SUCCESS` or `ERROR`                  |
| `PWD`                    | Returns the current working directory (relative to the user's root).                                          | path string (e.g. `/` or `/receitas`) |
| `CHDIR path`             | Changes the current directory. Directory traversal outside the user's area is blocked.                        | `SUCCESS` or `ERROR`                  |
| `GETFILES`               | Returns the number of files in the current directory, then each filename.                                     | count + filenames                     |
| `GETDIRS`                | Returns the number of directories in the current directory, then each name.                                   | count + dirnames                      |
| `HELP`                   | Displays available commands (client-side only, not sent to server).                                           | :                                     |
| `EXIT`                   | Closes the connection.                                                                                        | :                                     |

---

## Authentication

- Passwords are **never transmitted or stored in plain text**.
- The client hashes the password using **SHA-512** before sending.
- The server compares the received hash against the stored hash in `users.py`.
- All commands except `CONNECT` are blocked until the client is authenticated.

---

## Protocol

TCP is a stream protocol: messages have no natural boundaries. To avoid messages colliding (e.g. `"2bolo.txttorta.txt"`), every message is prefixed with its length:

```
| 4 bytes (big endian) | N bytes (UTF-8 string) |
```

This is handled transparently by `send_utf` and `recv_utf` in `protocol.py`.

---

## User Storage

Each user has an isolated directory under `server/files/<username>/`. On first login, the following mock structure is created automatically:

```
files/<username>/
├── vazio.txt
├── receitas/
│   ├── bolo.txt
│   └── torta.txt
└── images/
    └── img.png
```

Users can only navigate within their own area: attempts to escape via `../` are blocked server-side.

---

## Error Handling

- **Client:** `Ctrl+C` exits cleanly without a traceback.
- **Client:** Retries connection automatically if the server is unreachable.
- **Server:** `Ctrl+C` shuts down gracefully.
- **Server:** `BrokenPipeError` is caught per-thread when a client disconnects abruptly.
