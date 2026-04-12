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
│   └── files/              # User storage area (auto-created on first login)
│       └── <username>/     # Each user has their own isolated directory
├── client/
│   └── client.py           # Entry point: connects to server and sends commands
└── shared/
    └── protocol.py         # send_utf / recv_utf with length-prefix framing
```

---

## Requirements

- Python 3.8+
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

# Q2: TCP Binary File Server (binary-based)

A TCP client-server application built with Python's native `socket` library. The server manages a shared pool of remote files across multiple clients using a custom binary protocol over TCP.

## Problem Statement

Also proposed by Prof. Rodrigo Campiolo as part of the Distributed Systems course. The goal is to implement a multi-client TCP server that handles remote file management for upload, download, listing, and deletion, using a structured binary protocol with fixed headers. All server actions must be recorded using Python's native logging library.

---

## Project Structure

```
q2/
├── server/
│   ├── server.py           # Entry point: opens socket and accepts connections
│   ├── client_handler.py   # Command handlers for each connected client
│   └── storage/            # Files managed by the server (auto-created)
├─── client/
│   ├── client.py           # Entry point: connects to server and sends commands
│   └── downloads/          # Default download directory (auto-created)
└── shared/
    └── protocol.py         # send_request / send_response / constants with length-prefix framing
```

---

## Requirements

- Python 3.8+
- No external libraries required

---

## How to Run

Open **two terminals** at the project root.

**Terminal 1: Start the server:**

```bash
cd q2/server
python server.py
```

**Terminal 2: Start the client:**

```bash
cd q2/client
python client.py
```

> The server listens on `0.0.0.0:6720` (all interfaces).  
> The client connects to `127.0.0.1:6720` (localhost).  
> To connect from another machine, change `HOST` in `client.py` to the server's IP address.

---

## Supported Commands

| Command              | Description                                        |
| -------------------- | -------------------------------------------------- |
| `ADDFILE <filepath>` | Uploads a local file to the server                 |
| `DELETE <filename>`  | Removes a file from the server                     |
| `GETFILESLIST`       | Lists all files currently stored on the server     |
| `GETFILE <filename>` | Downloads a file from the server into `downloads/` |
| `HELP`               | Displays available commands (client-side only)     |
| `EXIT`               | Disconnects from the server                        |

---

## Binary Protocol

Unlike Q1 (text-based), all communication uses a **binary protocol** with fixed headers.

### Request header (client → server)

```
| 1 byte: Message Type (0x01) | 1 byte: Command | 1 byte: Filename Size | N bytes: Filename |
```

### Response header (server → client)

```
| 1 byte: Message Type (0x02) | 1 byte: Command | 1 byte: Status (0x01=SUCCESS, 0x02=ERROR) |
```

### ADDFILE: extra fields in request

```
| 4 bytes: file size (big endian) | N bytes: file content (byte by byte) |
```

### GETFILESLIST: extra fields in response

```
| 2 bytes: number of files (big endian) |
repeats per file:
| 1 byte: filename size | N bytes: filename |
```

### GETFILE: extra fields in response

```
| 4 bytes: file size (big endian) | N bytes: file content (byte by byte) |
```

### Command identifiers

| Command      | Code |
| ------------ | ---- |
| ADDFILE      | 0x01 |
| DELETE       | 0x02 |
| GETFILESLIST | 0x03 |
| GETFILE      | 0x04 |

---

## Logging

All server actions are recorded using Python's native `logging` library. Logs are written to both the terminal and `server.log`:

```
2024-01-01 12:00:00 [INFO] Server listening on 0.0.0.0:6720
2024-01-01 12:00:01 [INFO] ('127.0.0.1', 54321) connected
2024-01-01 12:00:02 [INFO] ADDFILE request: "foto.png" (204800 bytes)
2024-01-01 12:00:03 [INFO] ADDFILE success: "foto.png" saved to storage
2024-01-01 12:00:04 [WARNING] DELETE failed: "missing.txt" not found in storage
```

---

## Error Handling

- **Client:** `Ctrl+C` exits cleanly without a traceback.
- **Client:** Retries connection automatically if the server is unreachable.
- **Server:** `Ctrl+C` shuts down gracefully.
- **Server:** Exceptions per client are caught and logged without crashing other connections.
