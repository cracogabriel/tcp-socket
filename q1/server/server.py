import socket
import threading
import sys

sys.path.append('..')
from shared.protocol import send_utf, recv_utf
from client_handler import handle_connect, handle_pwd, handle_chdir, handle_getfiles, handle_getdirs

HOST = '0.0.0.0'
PORT = 6711

COMMANDS = {
  "PWD": handle_pwd,
  'CHDIR': handle_chdir,
  'GETFILES': handle_getfiles,
  'GETDIRS': handle_getdirs,
}

def setup_server():
  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server.bind((HOST, PORT))
  server.listen()
  print(f'Server listening on {HOST}:{PORT}')
  return server

def handle_client(conn, addr):
  try:
    print(f'{addr} connected')
    send_utf(conn, 'Welcome to the server! To startup, please authenticate using: CONNECT <username>, <password>')
    authenticated = False
    user_dir = None
    current_dir = '/'
    
    while True:
      msg = recv_utf(conn)
      print(f'{addr} > {msg}')

      command = msg.split(' ')[0]
      args = msg[len(command)+1:]

      if command == 'EXIT':
        break

      if command == 'CONNECT':
          authenticated, user_dir = handle_connect(conn, args)
          current_dir = '/'
      elif not authenticated:
          send_utf(conn, 'ERROR: Not authenticated')
      elif command in COMMANDS:
          new_dir = COMMANDS[command](conn, args, user_dir, current_dir)
          if new_dir is not None:
              current_dir = new_dir
      else:
          send_utf(conn, 'ERROR: Unknown command')

  except Exception as e:
    print(f'Error handling client {addr}: {e}')
  finally:    
    print(f'{addr} disconnected')
    conn.close()

def main():
  server = setup_server()
  while True:
    conn, addr = server.accept() # awaits connections from clients
    
    # when connection occurs, create a thread to not block the server from recieving new connections
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\nServer shutting down.')