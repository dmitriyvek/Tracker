import argparse
from typing import Callable


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


def get_arg_parser(params: dict) -> argparse.ArgumentParser:
    '''Configure and return parser with given default params for command line variables'''
    from tracker.utils.settings import ENV_PATH

    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description=f'The default values specified here are taken from .env file located here: {ENV_PATH} (if you want to specify another location change ENV_PATH in tracker.utils.settings)',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--debug', action='store_true', default=params['debug'],
                        help='Running application in debug mod if specified')

    group = parser.add_argument_group('API options')
    group.add_argument('--api-address', required=False, default=params['host'],
                       help='IPv4/IPv6 address API server would listen on')
    group.add_argument('--api-port', type=positive_int, required=False, default=params['port'],
                       help='TCP port API server would listen on')

    group = parser.add_argument_group('PostgreSQL options')
    group.add_argument('--db-url', type=str, required=False, default=params['db_url'],
                       help='URL to use to connect to the database')
    group.add_argument('--pg-pool-min-size', type=positive_int, default=params['min_db_pool'],
                       required=False, help='Minimum database connections')
    group.add_argument('--pg-pool-max-size', type=positive_int, default=params['max_db_pool'],
                       required=False, help='Maximum database connections')

    # group = parser.add_argument_group('Logging options')
    # group.add_argument('--log-level', default='info',
    #                    choices=('debug', 'info', 'warning', 'error', 'fatal'))
    # group.add_argument('--log-format', choices=LogFormat.choices(),
    #                    default='color')

    return parser
