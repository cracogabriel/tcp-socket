# wrapper functions to standardize message communication between client and server.
# ensures consistent UTF-8 encoding for all messages sent and received.

def send_utf(conn, message: str):
    data = message.encode('utf-8')
    conn.sendall(data)

def recv_utf(conn, buffer=1024) -> str:
    data = conn.recv(buffer)
    return data.decode('utf-8')