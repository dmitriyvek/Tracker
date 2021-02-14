import os
from pathlib import Path
from types import SimpleNamespace

from alembic.config import Config

from tracker.utils.settings import BASE_DIR, DEFAULT_CONFIG_PARAMS, ENV_PATH
from tracker.utils.utils import parse_env_file, construct_db_url


def get_default_db_url() -> str:
    '''Alembic helper for returning current db url'''
    env_options = parse_env_file(ENV_PATH)
    return construct_db_url(env_options, DEFAULT_CONFIG_PARAMS['db_url'])


def make_alembic_config(cmd_opts: SimpleNamespace,
                        base_path: str = BASE_DIR) -> Config:
    '''
    Creates alembic config object based on command line arguments,
    replaces relative paths with absolute ones 
    '''
    if not os.path.isabs(cmd_opts.config):
        cmd_opts.config = os.path.join(base_path, cmd_opts.config)

    config = Config(file_=cmd_opts.config, ini_section=cmd_opts.name,
                    cmd_opts=cmd_opts)

    alembic_location = config.get_main_option('script_location')
    if not os.path.isabs(alembic_location):
        config.set_main_option('script_location',
                               os.path.join(base_path, alembic_location))
    if cmd_opts.pg_url:
        config.set_main_option('sqlalchemy.url', cmd_opts.pg_url)

    return config
