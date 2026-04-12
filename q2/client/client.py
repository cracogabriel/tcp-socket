import os
import socket
import sys
import time
import struct

sys.path.append('..')
from shared.protocol import CMD_ADDFILE, CMD_DELETE, CMD_GETFILE, CMD_GETFILESLIST, STATUS_SUCCESS, send_request, recv_exact

HOST = '127.0.0.1'
PORT = 6720

MAX_RETRIES = 5

def setup_client():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST, PORT))
            print_startup()
            return client
        except Exception as e:
            print(f'[{attempt}/{MAX_RETRIES}] Error: {e}. Retrying in 3 seconds...')
            if attempt < MAX_RETRIES:
                time.sleep(3)
    print('Could not connect to server. Exiting.')
    sys.exit(1)

def print_startup():
    print()
    print('-' * 30)
    print(f'Connected to server at {HOST}:{PORT}')
    print('Type "HELP" for a list of commands')
    print('-' * 30)
    print()

def print_help():
    print()
    print('Available commands:')
    print('  ADDFILE <filepath>  - Upload a file to the server')
    print('  DELETE <filename>   - Remove a file from the server')
    print('  GETFILESLIST        - List all files on the server')
    print('  GETFILE <filename>  - Download a file from the server')
    print('  HELP                - Show this help message')
    print('  EXIT                - Disconnect from the server')
    print()

def main():
    client = setup_client()

    while True:
        try:
            user_input = input('> ')
            if user_input.strip() == '':
                continue

            parsed_command = user_input.split(' ')[0].upper()

            if parsed_command == 'HELP':
                print_help()
                continue

            if parsed_command == 'EXIT':
                break

            if parsed_command not in ('GETFILESLIST', 'ADDFILE', 'DELETE', 'GETFILE' ):
                 print(f'Command "{parsed_command}" does not exists.')
                 
                 print_help()
                 continue
            
            if parsed_command == 'ADDFILE':
                filepath = user_input[len(parsed_command)+1:]
                filename = filepath.split('/')[-1] 

                with open(filepath, 'rb') as f:
                    file_data = f.read()

                send_request(client, CMD_ADDFILE, filename.encode('utf-8'))

                file_size = len(file_data)
                client.sendall(struct.pack('>I', file_size))

                for byte in file_data:
                    client.send(bytes([byte]))

                response = recv_exact(client, 3)
                msg_type, command, status = struct.unpack('>BBB', response)

                if status == STATUS_SUCCESS:
                    print(f'File "{filename}" uploaded successfully')
                else:
                    print(f'Error uploading file "{filename}"')

            if parsed_command == 'DELETE':
                filename = user_input[len(parsed_command)+1:]
                send_request(client, CMD_DELETE, filename.encode('utf-8'))

                response = recv_exact(client, 3)
                msg_type, command, status = struct.unpack('>BBB', response)

                if status == STATUS_SUCCESS:
                    print(f'File "{filename}" deleted successfully')
                else:
                    print(f'Error deleting file "{filename}"')

            if parsed_command == 'GETFILESLIST':
                send_request(client, CMD_GETFILESLIST)
                response = recv_exact(client, 3)
                msg_type, command, status = struct.unpack('>BBB', response)
                if status == STATUS_SUCCESS:
                    num_files_bytes = recv_exact(client, 2)
                    num_files = struct.unpack('>H', num_files_bytes)[0]
                    print(f'\n{num_files} file(s) on server:')

                    for _ in range(num_files):
                        filename_size = struct.unpack('>B', recv_exact(client, 1))[0]
                        filename = recv_exact(client, filename_size).decode('utf-8')
                        print(f'{filename}')

                    print()
                else:
                    print('Error listing files on server')

            if parsed_command == 'GETFILE':
                filename = user_input[len(parsed_command)+1:]
                send_request(client, CMD_GETFILE, filename.encode('utf-8'))
                response = recv_exact(client, 3)
                msg_type, command, status = struct.unpack('>BBB', response)
                if status == STATUS_SUCCESS:
                    file_data_len_bytes = recv_exact(client, 4)
                    file_data_len = struct.unpack('>I', file_data_len_bytes)[0]

                    file_data = b''
                    for _ in range(file_data_len):
                        byte = recv_exact(client, 1)
                        if not byte:
                            break
                        file_data += byte

                    os.makedirs('downloads', exist_ok=True)
                    with open(os.path.join('downloads', filename), 'wb') as f:
                        f.write(file_data)
                    
                    print(f'Successfully downloaded file {filename}, saved at downloads folder')
                else:
                    print(f'Error fetching file "{filename}"')
        except Exception as e:
            print(f'Error: {e}')
            break

    print('Closing connection')
    client.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\nKeyboard interrupt received. Exiting.')