import os
from pathlib import Path
from getpass import getuser

from tracker.utils.argparse import get_arg_parser
from tracker.utils.utils import parse_env_file, merge_env_with_default
from tracker.utils.loggers import LogLevelEnum


BASE_DIR = Path(__file__).parent.parent
ENV_PATH = Path(__file__).parent.parent.parent / '.env'

# All required params with default values
DEFAULT_CONFIG = {
    'debug': False,
    'db_url': 'postgres://{user}:{pswd}@{host}:{port}/{db}'.format(
        user=getuser(), pswd='tracker_pswd',
        host='localhost', port='5432',
        db='tracker_db'
    ),
    'pg_pool_max_size': 10,
    'pg_pool_min_size': 10,
    'host': '0.0.0.0',
    'port': 8000,
    'log_level': LogLevelEnum.debug.value.name.lower(),
    'error_log_file_path': BASE_DIR / Path('log/app/error.log'),
    'info_log_file_path': BASE_DIR / Path('log/app/info.log'),
    'censored_sign': '***',
}


def get_config(argv=None) -> dict:
    '''Gets config parameters from merging default params, params from .env file and params from argparser'''
    env_options = parse_env_file(ENV_PATH)
    params = merge_env_with_default(env_options, DEFAULT_CONFIG)

    parser = get_arg_parser(params)
    namespace = parser.parse_args(argv)

    config = DEFAULT_CONFIG.copy()
    config.update(vars(namespace))

    return config
