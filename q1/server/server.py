import socket
import threading
import sys

sys.path.append('..')
from shared.protocol import send_utf, recv_utf

HOST = '0.0.0.0'
PORT = 6700

def setup_server():
  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server.bind((HOST, PORT))
  server.listen()
  print(f'Server listening on {HOST}:{PORT}')
  return server

def handle_client(conn, addr):
  print(f'{addr} connected')
  send_utf(conn, 'Welcome to the server!')
  msg = recv_utf(conn)
  print(f'{addr} > {msg}')
  conn.close()

def main():
  server = setup_server()
  while True:
    conn, addr = server.accept() # awaits connections from clients
    
    # when connection occurs, create a thread to not block the server from recieving new connections
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()

if __name__ == "__main__":
    main()