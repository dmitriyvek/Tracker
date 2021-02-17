import os
from pathlib import Path

from dotenv import load_dotenv

from tracker.utils.argparse import get_arg_parser
from tracker.utils.utils import parse_env_file, merge_env_with_default
from tracker.utils.loggers import LogLevelEnum


BASE_DIR = Path(__file__).parent.parent
ENV_PATH = Path(__file__).parent.parent.parent / '.env'

# All required params with default values
DEFAULT_CONFIG_PARAMS = {
    'debug': False,
    'db_url': 'sqlite:///tracker.db',
    'pg_pool_max_size': 10,
    'pg_pool_min_size': 10,
    'host': '0.0.0.0',
    'port': 8000,
    'log_level': LogLevelEnum.info.value.name.lower(),
}


def get_config(argv=None) -> dict:
    '''Gets config parameters from merging default params, params from .env file and params from argparser'''
    env_options = parse_env_file(ENV_PATH)
    params = merge_env_with_default(env_options, DEFAULT_CONFIG_PARAMS)

    parser = get_arg_parser(params)
    namespace = parser.parse_args(argv)
    return vars(namespace)
