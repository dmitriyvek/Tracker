import os
from pathlib import Path, PosixPath

from yarl import URL


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


def merge_env_with_default(env: dict, default: dict) -> dict:
    '''Merge .env options with default'''
    from tracker.utils.db import construct_db_url

    result = {}
    env['db_url'] = URL(construct_db_url(env, default['db_url']))
    for key, value in default.items():
        if env.get(key):
            result[key] = env[key]
        else:
            result[key] = value

    return result
