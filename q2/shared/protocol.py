import struct

MSG_REQUEST  = 0x01 # 01 for request
MSG_RESPONSE = 0x02 # 02 for response

CMD_ADDFILE      = 0x01 # 01 for adding a file
CMD_DELETE       = 0x02 # 02 for deleting a file
CMD_GETFILESLIST = 0x03 # 03 for getting the list of files
CMD_GETFILE      = 0x04 # 04 for getting a specific file

STATUS_SUCCESS = 0x01 # 01 for success
STATUS_ERROR   = 0x02 # 02 for error

def send_request(conn, command, filename=b''):
    filename_size = len(filename)
    header = struct.pack('>BBB', MSG_REQUEST, command, filename_size)
    conn.sendall(header + filename)

def send_response(conn, command, status, data=b''):
    header = struct.pack('>BBB', MSG_RESPONSE, command, status)
    conn.sendall(header + data)

def recv_request(conn):
    header = recv_exact(conn, 3) # read the first 3 bytes of the header
    msg_type, command, filename_size = struct.unpack('>BBB', header)
    filename = recv_exact(conn, filename_size)  # read the filename
    return command, filename.decode('utf-8')

def recv_exact(conn, n):
    data = b''
    while len(data) < n:
        chunk = conn.recv(n - len(data))
        if not chunk:
            break
        data += chunk
    return data