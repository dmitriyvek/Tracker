import os
from pathlib import Path

from dotenv import load_dotenv

from tracker.utils.utils import positive_int, get_arg_parser, get_config_trafaret, clear_environ


BASE_DIR = Path(__file__).parent.parent
DEFAULT_ENV_PATH = Path(__file__).parent.parent.parent / '.env'
DEFAULT_ENV_VAR_PREFIX = 'tracker_'

DEFAULT_CONFIG_PARAMS = {
    'debug': False,
    'db_url': 'sqlite:///tracker.db',
    'max_db_pool': 10,
    'min_db_pool': 10,
    'host': '0.0.0.0',
    'port': 8000,
}


def get_config(argv=None):
    parser = get_arg_parser()

    # ignore unknown options
    options, unknown = parser.parse_known_args(argv)
    options = {key: value for (key, value) in vars(
        options).items() if value is not None}

    load_dotenv(dotenv_path=options['env_file'], verbose=True)
    trafaret = get_config_trafaret(options['env_var_prefix'])
    config = trafaret.check(options)
    clear_environ(lambda i: i.startswith(options['env_var_prefix']))

    return config


# TODO: rewrite
def get_default_pg_url():
    pg_config = get_config()['postgres']
    pg_url = 'postgresql://{user}:{password}@{host}:{port}/{database}'.format(
        user=pg_config['user'],
        password=pg_config['password'],
        host=pg_config['host'],
        port=pg_config['port'],
        database=pg_config['database']
    )
    return pg_url
