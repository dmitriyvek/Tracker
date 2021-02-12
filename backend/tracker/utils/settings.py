import argparse
import pathlib

from trafaret_config import commandline

from tracker.utils.utils import ENV_TRAFARET


BASE_DIR = pathlib.Path(__file__).parent.parent
DEFAULT_CONFIG_PATH = BASE_DIR / 'config' / 'env.yaml'


def get_config(argv=None):
    ap = argparse.ArgumentParser()
    commandline.standard_argparse_options(
        ap,
        default_config=DEFAULT_CONFIG_PATH
    )

    # ignore unknown options
    options, unknown = ap.parse_known_args(argv)

    config = commandline.config_from_options(options, ENV_TRAFARET)
    return config


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
