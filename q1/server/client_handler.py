import sys
sys.path.append('..')

from users import USERS
from shared.protocol import send_utf
from mock_files import create_mock_files

import os

def handle_connect(conn, args) -> tuple[bool, str | None]:
    try:
        user, pwd = args.split(', ')
        if user in USERS and USERS[user] == pwd:
            print(f'{user} authenticated successfully')
            
            # create the user directory for personal use
            user_dir = f'files/{user}'
            os.makedirs(user_dir, exist_ok=True)
            create_mock_files(user_dir) # this creates a mock files to use the commands
            
            send_utf(conn, 'SUCCESS: Authenticated successfully - Type "HELP" for a list of commands')
            return True, user_dir
        else:
            print(f'{user} failed authentication')
            send_utf(conn, 'ERROR: Invalid username or password')
            return False, None
    except Exception as e:
        print(f'Error handling CONNECT: {e}')
        send_utf(conn, 'ERROR: Invalid CONNECT command format. Use: CONNECT <username>, <password>')
        return False, None

def handle_pwd(conn, args, user_dir, current_dir):
    send_utf(conn, current_dir)

def handle_chdir(conn, args, user_dir, current_dir):
    path = args
    full_path = os.path.normpath(os.path.join(user_dir, current_dir.lstrip('/'), path))

    if not os.path.isdir(full_path):
      send_utf(conn, 'ERROR: Directory does not exist')
      return
    
    if not full_path.startswith(user_dir):
        send_utf(conn, 'ERROR: Directory traversal not allowed')
        return current_dir

    new_dir = '/' + os.path.relpath(full_path, user_dir)
    send_utf(conn, 'SUCCESS')
    return new_dir

def handle_getfiles(conn, args, user_dir, current_dir):
    full_path = os.path.normpath(os.path.join(user_dir, current_dir.lstrip('/')))

    entries = os.listdir(full_path)
    files = [e for e in entries if os.path.isfile(os.path.join(full_path, e))]
    print(files)

    send_utf(conn, str(len(files)))
    
    for file in files:
        send_utf(conn, file)


def handle_getdirs(conn, args, user_dir, current_dir):
    full_path = os.path.normpath(os.path.join(user_dir, current_dir.lstrip('/')))

    entries = os.listdir(full_path)
    dirs = [e for e in entries if os.path.isdir(os.path.join(full_path, e))]
    print(dirs)

    send_utf(conn, str(len(dirs)))
    
    for dir in dirs:
        send_utf(conn, dir)