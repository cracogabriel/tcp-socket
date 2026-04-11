import hashlib
import struct

# hashes a password using SHA-512 and returns the hexadecimal digest.
def hash_pwd(pwd: str):
    return hashlib.sha512(pwd.encode()).hexdigest()

# wrapper functions to standardize message communication between client and server.
# ensures consistent UTF-8 encoding for all messages sent and received.
def send_utf(conn, message: str):
    data = message.encode('utf-8')
    length = struct.pack('>I', len(data))  # 4 bytes big endian
    conn.sendall(length + data)

def recv_utf(conn) -> str:
    # read the first 4 bytes of length
    raw_len = _recv_exact(conn, 4)
    if not raw_len:
        return ''
    length = struct.unpack('>I', raw_len)[0]
    # read the N bytes of the message
    data = _recv_exact(conn, length)
    return data.decode('utf-8')

def _recv_exact(conn, n: int) -> bytes:
    data = b''
    while len(data) < n:
        chunk = conn.recv(n - len(data))
        if not chunk:
            break
        data += chunk
    return data
    