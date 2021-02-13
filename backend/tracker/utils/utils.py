import os
import argparse
from pathlib import Path
from typing import Callable, Dict, Union

import trafaret as T


def construct_db_url(env_prefix: str) -> Union[str, None]:
    '''
    Reads all pg parameters in .env file and construct pg url
    if all of them is specified else returns None
    '''
    pg_keys = [f'{env_prefix}pg_name', f'{env_prefix}pg_user',
               f'{env_prefix}pg_password', f'{env_prefix}pg_host', f'{env_prefix}pg_port']
    if all([os.getenv(key) for key in pg_keys]):
        return 'postgresql://{user}:{password}@{host}:{port}/{database}'.format(
            user=os.getenv(pg_keys[1]),
            password=os.getenv(pg_keys[2]),
            host=os.getenv(pg_keys[3]),
            port=os.getenv(pg_keys[4]),
            database=os.getenv(pg_keys[0])
        )
    return None


def get_config_trafaret(env_prefix: str) -> T.Dict:
    from tracker.utils.settings import DEFAULT_CONFIG_PARAMS as default
    db_url = construct_db_url(env_prefix)
    ENV_TRAFARET = T.Dict({
        T.Key(
            'debug',
            default=True if os.getenv(
                f'{env_prefix}debug') == 'true' else default['debug']
        ): T.Bool,
        T.Key(
            'db_url',
            default=db_url if db_url else default['db_url']
        ): T.String,
        T.Key(
            'api_address',
            default=os.getenv(f'{env_prefix}host') if os.getenv(
                f'{env_prefix}host') else default['host']
        ): T.IP,
        T.Key(
            'api_port',
            default=os.getenv(f'{env_prefix}port') if os.getenv(
                f'{env_prefix}port') else default['port']
        ): T.Int(),
        T.Key(
            'pg_pool_min_size',
            default=os.getenv(f'{env_prefix}minsize') if os.getenv(
                f'{env_prefix}minsize') else default['min_db_pool']
        ): T.Int,
        T.Key(
            'pg_pool_max_size',
            default=os.getenv(f'{env_prefix}maxsize') if os.getenv(
                f'{env_prefix}maxsize') else default['max_db_pool']
        ): T.Int,
        T.Key('env_var_prefix'): T.Any,
        T.Key('env_file'): T.Any
    })
    return ENV_TRAFARET


def validate(type: Callable, constrain: Callable):
    def wrapper(value):
        try:
            value = type(value)
        except ValueError:
            raise argparse.ArgumentTypeError(
                f'Given value: {value} must be a type of {type}')
        if not constrain(value):
            raise argparse.ArgumentTypeError
        return value

    return wrapper


positive_int = validate(int, constrain=lambda x: x > 0)


def clear_environ(rule: Callable):
    '''
    Clears environment variables, variables for clearing are determined by the passed
    rule function.
    '''
    # Keys from os.environ are copied to the new tuple so as not to change the object
    # os.environ during iteration.
    for name in filter(rule, tuple(os.environ)):
        os.environ.pop(name)


def get_arg_parser() -> argparse.ArgumentParser:
    '''Configure and return default parser for command line variables'''
    from tracker.utils.settings import DEFAULT_ENV_VAR_PREFIX, DEFAULT_ENV_PATH, DEFAULT_CONFIG_PARAMS as default

    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description='The default values specified here are overwritten with the values from the .env file ',
        # formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--debug', action='store_true', default=None,
                        help='Running application in debug mod if specified')

    group = parser.add_argument_group('.env file options')
    group.add_argument('--env-file', required=False, type=Path, default=DEFAULT_ENV_PATH,
                       help=f'Path to the .env file with config options (default: {DEFAULT_ENV_PATH})')
    group.add_argument('--env-var-prefix', required=False, type=str, default=DEFAULT_ENV_VAR_PREFIX,
                       help=f'Prefix for variables from the .env file (default: {DEFAULT_ENV_VAR_PREFIX})')

    group = parser.add_argument_group('API options')
    group.add_argument('--api-address', required=False,
                       help='IPv4/IPv6 address API server would listen on (default: {})'.format(default['host']))
    group.add_argument('--api-port', type=positive_int, required=False,
                       help='TCP port API server would listen on (default: {})'.format(default['port']))

    group = parser.add_argument_group('PostgreSQL options')
    group.add_argument('--db-url', type=str, required=False,
                       help='URL to use to connect to the database (default: {})'.format(default['db_url']))
    group.add_argument('--pg-pool-min-size', type=positive_int,
                       required=False, help='Minimum database connections (default: {})'.format(default['min_db_pool']))
    group.add_argument('--pg-pool-max-size', type=positive_int,
                       required=False, help='Maximum database connections (default: {})'.format(default['max_db_pool']))

    # group = parser.add_argument_group('Logging options')
    # group.add_argument('--log-level', default='info',
    #                    choices=('debug', 'info', 'warning', 'error', 'fatal'))
    # group.add_argument('--log-format', choices=LogFormat.choices(),
    #                    default='color')

    return parser
