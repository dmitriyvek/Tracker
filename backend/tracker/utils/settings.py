import os
import sys
from datetime import timedelta
from pathlib import Path
from getpass import getuser

from dotenv import load_dotenv
from yarl import URL

from tracker.utils.argparse import get_arg_parser
from tracker.utils.utils import parse_env_file, merge_env_with_default
from tracker.utils.loggers import LogLevelEnum


BASE_DIR = Path(__file__).parent.parent
ENV_PATH = Path(__file__).parent.parent.parent / '.env'

load_dotenv(ENV_PATH)

# All required params with default values
MAIN_CONFIG = {
    'debug': True,
    'secret_key': os.getenv('secret_key') or 'SECRET_KEY',

    'db_url': URL('postgres://{user}:{pswd}@{host}:{port}/{db}'.format(
        user=os.getenv('pg_user') or getuser(),
        pswd=os.getenv('pg_password') or 'tracker_pswd',
        host=os.getenv('pg_host') or 'localhost',
        port=os.getenv('pg_port') or '5432',
        db=os.getenv('pg_name') or 'tracker_db'
    )),
    'pg_pool_max_size': 10,
    'pg_pool_min_size': 10,

    'api_host': os.getenv('api_host') or '0.0.0.0',
    'domain_name': os.getenv('domain_name') or 'localhost',
    'url_schema': os.getenv('url_schema') or 'http',
    'api_port': int(os.getenv('api_port')) or 8000,
    'max_fetch_number': 10,

    'log_level': LogLevelEnum.debug.value.name.lower(),
    'error_log_file_path': BASE_DIR.parent / Path('log/app/error.log'),
    'info_log_file_path': BASE_DIR.parent / Path('log/app/info.log'),
    'request_info_log_file_path':
        BASE_DIR.parent / Path('log/app/request.log'),
    'log_censored_sign': '***',

    'auth_token_expiration_time': timedelta(days=1),

    # must be in .env file
    'mail_server': os.getenv('mail_server'),
    'mail_port': os.getenv('mail_port'),
    'mail_username': os.getenv('mail_username'),
    'mail_password': os.getenv('mail_password'),
    'mail_use_ssl': os.getenv('mail_use_ssl'),
    'mail_timeout': 10,  # number of seconds
    # how many letters you can send in one api request
    # (hardcoded in EmailList scalar)
    'mail_max_letters_number': 5,
}


# deprecated
def get_config() -> dict:
    '''
    Gets config parameters from merging default params,
    params from .env file and params from argparser
    '''
    env_options = parse_env_file(ENV_PATH)
    params = merge_env_with_default(env_options, MAIN_CONFIG)
    config = MAIN_CONFIG.copy()

    if not all([
        params.get('mail_server'), params.get('mail_port'),
        params.get('mail_username'), params.get('mail_password'),
        params.get('mail_use_ssl')
    ]):
        raise KeyError(
            'There must be: "mail_server", '
            '"mail_port", "mail_username", "mail_password", "mail_use_ssl"'
            ' parameters in your .env file'
        )

    # if app started with gunicorn
    # then we does not need arg parser
    if os.getenv('gunicorn'):
        config.update(params)
    # if app started with aiohttp-devtools runserver
    # then we does not need arg parser
    elif 'runserver' in sys.argv:
        config.update(params)
    else:
        parser = get_arg_parser(params)
        namespace = parser.parse_args()
        config.update(vars(namespace))

    return config
