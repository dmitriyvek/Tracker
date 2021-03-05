import os
import uuid
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Optional

from asyncpgsa import pg, PG
from aiohttp.web_app import Application
from alembic.config import Config
from sqlalchemy_utils import create_database, drop_database
from yarl import URL

from tracker import __name__ as project_name
from tracker.utils.settings import BASE_DIR, DEFAULT_CONFIG, ENV_PATH
from tracker.utils.utils import parse_env_file


async def setup_db(app: Application) -> PG:
    config = app['config']
    log = app['logger']

    log_db_url = config['db_url'].with_password(config['censored_sign'])
    log.info(f'Connecting to database: {log_db_url}')

    app['db'] = pg
    await app['db'].init(
        str(config['db_url']),
        min_size=config['pg_pool_min_size'],
        max_size=config['pg_pool_max_size'],
    )
    await app['db'].fetchval('SELECT 1')
    log.info(f'Connected to database {log_db_url}')

    try:
        yield
    finally:
        log.info(f'Disconnecting from database {log_db_url}')
        await app['db'].pool.close()
        log.info(f'Disconnected from database {log_db_url}')


def construct_db_url(env_values: dict, default_url: str) -> str:
    '''
    Reads all pg parameters from .env file and construct pg url
    if all of them are specified else returns default
    '''
    pg_keys = ['pg_name', 'pg_user', 'pg_password', 'pg_host', 'pg_port']
    if all([env_values.get(key) for key in pg_keys]):
        return 'postgresql://{user}:{password}@{host}:{port}/{database}'.format(
            user=env_values[pg_keys[1]],
            password=env_values[pg_keys[2]],
            host=env_values[pg_keys[3]],
            port=env_values[pg_keys[4]],
            database=env_values[pg_keys[0]]
        )
    return default_url


def get_db_url() -> str:
    '''Helper for getting current db url'''
    env_options = parse_env_file(ENV_PATH)
    return construct_db_url(env_options, DEFAULT_CONFIG['db_url'])


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
    if cmd_opts.db_url:
        config.set_main_option('sqlalchemy.url', str(cmd_opts.db_url))

    return config


def get_alembic_config_from_url(db_url: Optional[str] = None) -> Config:
    '''Provides Python object, representing alembic.ini file.'''
    cmd_options = SimpleNamespace(
        config='alembic.ini', name='alembic', db_url=db_url,
        raiseerr=False, x=None,
    )

    return make_alembic_config(cmd_options)


@contextmanager
def tmp_database(db_url: str, suffix: str = '', **kwargs):
    tmp_db_name = '.'.join([uuid.uuid4().hex, project_name, suffix])
    tmp_db_url = str(URL(db_url).with_path(tmp_db_name))
    create_database(tmp_db_url, **kwargs)

    try:
        yield tmp_db_url
    finally:
        drop_database(tmp_db_url)
