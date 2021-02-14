import os
from pathlib import Path

from dotenv import load_dotenv

from tracker.utils.argparse import get_arg_parser
from tracker.utils.utils import parse_env_file, merge_env_with_default


BASE_DIR = Path(__file__).parent.parent
ENV_PATH = Path(__file__).parent.parent.parent / '.env'

# All required params with default values
DEFAULT_CONFIG_PARAMS = {
    'debug': False,
    'db_url': 'sqlite:///tracker.db',
    'max_db_pool': 10,
    'min_db_pool': 10,
    'host': '0.0.0.0',
    'port': 8000,
}


def get_config(argv=None) -> dict:
    env_options = parse_env_file(ENV_PATH)
    params = merge_env_with_default(env_options, DEFAULT_CONFIG_PARAMS)

    parser = get_arg_parser(params)
    namespace = parser.parse_args(argv)
    return vars(namespace)
