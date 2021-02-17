import os
from pathlib import Path, PosixPath


def init_logs(error_path: PosixPath, info_path: PosixPath) -> None:
    '''Creates log files inside log folder if it does not exist (unix only)'''
    if not error_path.exists():
        if not error_path.parent.is_dir():
            os.makedirs(error_path.parent)
        with open(error_path, 'w+'):
            pass

    if not info_path.exists():
        if not info_path.parent.is_dir():
            os.makedirs(info_path.parent)
        with open(info_path, 'w+'):
            pass


def parse_env_file(path_to_file: Path) -> dict:
    '''Parse .env file and construct dict with .env parameters'''
    args = {}
    with open(path_to_file, 'r') as file:
        for line in file.readlines():
            if not line.startswith((' ', '#', '\n')):
                if line.startswith('export '):
                    line = line.lstrip('export ')
                line = line.split('=')
                line[0] = line[0].rstrip()
                line[1] = line[1].lstrip(r' *"').rstrip('"\n')
                if line[1] == 'true' or line[1] == 'True':
                    line[1] = True
                if line[1] == 'false' or line[1] == 'False':
                    line[1] = False
                args[line[0]] = line[1]
    return args


def construct_db_url(env_values: dict, default_url: str) -> str:
    '''
    Reads all pg parameters from .env file and construct pg url
    if all of them are specified else returns default
    '''
    pg_keys = ['pg_name', 'pg_user', 'pg_password', 'pg_host', 'pg_port']
    if all([env_values.get(key) for key in pg_keys]):
        return 'postgresql://{user}:{password}@{host}:{port}/{database}'.format(
            user=env_values[pg_keys[1]],
            password=env_values[pg_keys[2]],
            host=env_values[pg_keys[3]],
            port=env_values[pg_keys[4]],
            database=env_values[pg_keys[0]]
        )
    return default_url


def merge_env_with_default(env: dict, default: dict) -> dict:
    '''Merge .env options with default'''
    result = {}
    env['db_url'] = construct_db_url(env, default['db_url'])
    for key, value in default.items():
        if env.get(key):
            result[key] = env[key]
        else:
            result[key] = value

    return result
