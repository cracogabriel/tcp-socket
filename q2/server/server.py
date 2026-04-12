import socket
import threading
import logging
import sys

sys.path.append('..')
from shared.protocol import CMD_ADDFILE, CMD_DELETE, CMD_GETFILE, CMD_GETFILESLIST, recv_request, send_response
from client_handler import handle_addfile, handle_delete, handle_getfile, handle_getfileslist

HOST = '0.0.0.0'
PORT = 6720

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)

def setup_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    logging.info(f'Server listening on {HOST}:{PORT}')
    return server

def handle_client(conn, addr):
    try:
        logging.info(f'{addr} connected')

        while True:
            try:
                command, filename = recv_request(conn)
            except:
                break 

            logging.info(f'{addr} > Command: {command}, Filename: "{filename}"')

            if command == CMD_ADDFILE:
                handle_addfile(conn, filename)
            elif command == CMD_DELETE:
                handle_delete(conn, filename)
            elif command == CMD_GETFILESLIST:
                handle_getfileslist(conn)
            elif command == CMD_GETFILE:
                handle_getfile(conn, filename)
            
    except Exception as e:
        logging.error(f'Error handling client {addr}: {e}')
    finally:
        logging.info(f'{addr} disconnected')
        conn.close()

def main():
    server = setup_server()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info('Server shutting down.')