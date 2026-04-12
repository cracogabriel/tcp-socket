import logging
import sys
import struct
import os

sys.path.append('..')
from shared.protocol import CMD_ADDFILE, CMD_DELETE, CMD_GETFILE, CMD_GETFILESLIST, STATUS_ERROR, STATUS_SUCCESS, recv_exact, send_response

def handle_addfile(conn, filename):
    try:
        logging.info(f'ADDFILE request: "{filename}" ({file_size} bytes)')
        size_bytes = recv_exact(conn, 4)
        file_size = struct.unpack('>I', size_bytes)[0]

        file_data = b''
        for _ in range(file_size):
            byte = conn.recv(1)
            if not byte:
                break
            file_data += byte

        os.makedirs('storage', exist_ok=True)
        with open(os.path.join('storage', filename), 'wb') as f:
            f.write(file_data)

        logging.info(f'ADDFILE success: "{filename}" saved to storage')
        send_response(conn, CMD_ADDFILE, STATUS_SUCCESS)
    except Exception as e:
        logging.error(f'Error handling ADDFILE for "{filename}": {e}')
        send_response(conn, CMD_ADDFILE, STATUS_ERROR)

def handle_delete(conn, filename):
    try: 
        logging.info(f'DELETE request: "{filename}"')
        file_path = os.path.join('storage', filename)

        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f'DELETE success: "{filename}" removed from storage')
            send_response(conn, CMD_DELETE, STATUS_SUCCESS)
        else:
            logging.warning(f'DELETE failed: "{filename}" not found in storage')
            send_response(conn, CMD_DELETE, STATUS_ERROR) 

    except Exception as e:
        logging.error(f'Error handling DELETE for "{filename}": {e}')
        send_response(conn, CMD_DELETE, STATUS_ERROR)

def handle_getfileslist(conn):
    try:
        logging.info('GETFILESLIST request received')
        files = os.listdir('storage')

        send_response(conn, CMD_GETFILESLIST, STATUS_SUCCESS)
        conn.sendall(struct.pack('>H', len(files)))

        for filename in files:
            filename_bytes = filename.encode('utf-8')
            conn.sendall(struct.pack('>B', len(filename_bytes)))  
            conn.sendall(filename_bytes)                           

        logging.info(f'GETFILESLIST success: {len(files)} files sent')
    except Exception as e:
        logging.error(f'Error handling GETFILESLIST: {e}')
        send_response(conn, CMD_GETFILESLIST, STATUS_ERROR)

def handle_getfile(conn, filename):
    try:
        logging.info('GETFILE request received')
        file_path = os.path.join('storage', filename)

        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                file_data = f.read()

            send_response(conn, CMD_GETFILE, STATUS_SUCCESS)
            conn.sendall(struct.pack('>I', len(file_data)))
            
            for byte in file_data:
                conn.send(bytes([byte]))

            logging.info(f'GETFILE success: "{filename}" fetched from storage')
        else:
            logging.warning(f'GETFILE failed: "{filename}" not found in storage')
            send_response(conn, CMD_DELETE, STATUS_ERROR) 
            
    except Exception as e:
        logging.error(f'Error handling GETFILE: {e}')
        send_response(conn, CMD_GETFILE, STATUS_ERROR)
