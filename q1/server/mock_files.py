import os

def create_mock_files(user_dir):
    # create mock directories
    os.makedirs(f'{user_dir}/receitas', exist_ok=True)
    os.makedirs(f'{user_dir}/images', exist_ok=True)
    os.makedirs(f'{user_dir}/vazio', exist_ok=True)

    # mock recipes
    with open(f'{user_dir}/receitas/bolo.txt', 'w') as f:
        f.write('receita da silva')

    with open(f'{user_dir}/receitas/torta.txt', 'w') as f:
        f.write('torta de azeitona')

    # mock empty file
    with open(f'{user_dir}/vazio.txt', 'w') as f:
        f.write('...')

    # mock image
    with open(f'{user_dir}/images/img.png', 'wb') as f:
        f.write(b'\x89PNG\r\n')