import socket
import sys

sys.path.append('..')
from shared.protocol import send_utf, recv_utf

HOST = '127.0.0.1'
PORT = 6700

def setup_client():
  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client.connect((HOST, PORT))
  print(f'Connected to server at {HOST}:{PORT}')
  return client

def main():
  client = setup_client()
  msg = recv_utf(client)
  print(f'Server > {msg}')
  send_utf(client, 'client says hi')
  client.close()

if __name__ == "__main__":
  main()