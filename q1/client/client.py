import socket
import sys
import time

sys.path.append('..')
from shared.protocol import send_utf, recv_utf, hash_pwd

HOST = '127.0.0.1'
PORT = 6711

MAX_RETRIES = 5

def setup_client():
  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client.connect((HOST, PORT))
  print_startup()
  return client

def print_startup():
  print()
  print('-'* 30)
  print(f'Connected to server at {HOST}:{PORT}')
  print('Type "HELP" for a list of commands')
  print('-'* 30)
  print()

def print_help():
    print('')
    print('Available commands:')
    print('  CONNECT <username>, <password>  - Authenticate with the server')
    print('  PWD                             - Print the current directory')
    print('  CHDIR <path>                    - Change the current directory')
    print('  GETFILES                        - List files in the current directory')
    print('  GETDIRS                         - List directories in the current directory')
    print('  HELP                            - Show this help message')
    print('  EXIT                            - Disconnect from the server')
    print('')


def main():
  client = None
  for attempt in range(1, MAX_RETRIES + 1):
      try:
          client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          client.connect((HOST, PORT))
          print(f'Connected to server at {HOST}:{PORT}')
          break
      except Exception as e:
          print(f'[{attempt}/{MAX_RETRIES}] Error: {e}. Retrying in 3 seconds...')
          if attempt < MAX_RETRIES:
              time.sleep(3)

  if not client:
    print('Could not connect to server. Exiting.')
    sys.exit(1)

  parsed_command = ""
  msg = recv_utf(client)
  print(f'Server > {msg}')
  print('')
  
  while True:
      try:
          user_input = input("> ")
          if user_input.strip() == "":
              continue

          parsed_command = user_input.split(' ')[0].upper()

          if parsed_command == 'HELP':
              print_help()
              continue

          msg_to_send = user_input

          if parsed_command == 'CONNECT':
              try:
                  parsed_user_pwd = user_input[len(parsed_command)+1:]
                  user, pwd = parsed_user_pwd.split(', ')
                  pwd_hash = hash_pwd(pwd)
                  msg_to_send = f'{parsed_command} {user}, {pwd_hash}'
              except Exception as e:
                  print('Invalid CONNECT command format. Use: CONNECT <username>, <password>')
                  continue

          send_utf(client, msg_to_send)

          if parsed_command == 'EXIT':
              break

          # recebe resposta
          if parsed_command in ('GETFILES', 'GETDIRS'):
              count = int(recv_utf(client))
              for _ in range(count):
                  print(recv_utf(client))
          else:
              msg = recv_utf(client)
              print(f'Server > {msg}')

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