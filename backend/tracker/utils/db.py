import importlib
import os
import uuid
from contextlib import contextmanager
from collections import defaultdict, namedtuple
from pathlib import Path
from types import SimpleNamespace
from typing import Optional, List

from asyncpgsa import pg, PG
from aiohttp.web_app import Application
from alembic.config import Config
from sqlalchemy_utils import create_database, drop_database
from yarl import URL

from tracker import __name__ as project_name
from tracker.utils.settings import BASE_DIR, MAIN_CONFIG, ENV_PATH
from tracker.utils.utils import parse_env_file


MIGRATIONS_PATH = BASE_DIR / Path('db/alembic/versions/')


async def setup_db(app: Application) -> PG:
    config = app['config']
    log = app['logger']

    log_db_url = URL(config['db_url']).with_password(
        config['log_censored_sign'])
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


def construct_db_url(env_values: dict, default_url: str) -> URL:
    '''
    Reads all pg parameters from .env file and construct pg url
    if all of them are specified else returns default
    '''
    pg_keys = ['pg_name', 'pg_user', 'pg_password', 'pg_host', 'pg_port']
    if all([env_values.get(key) for key in pg_keys]):
        return URL('postgresql://{user}:{password}@{host}:{port}/{database}'.
                   format(
                       user=env_values[pg_keys[1]],
                       password=env_values[pg_keys[2]],
                       host=env_values[pg_keys[3]],
                       port=env_values[pg_keys[4]],
                       database=env_values[pg_keys[0]]
                   ))
    return default_url


def get_db_url() -> str:
    '''Helper for getting current db url'''
    env_options = parse_env_file(ENV_PATH)
    return construct_db_url(env_options, MAIN_CONFIG['db_url'])


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
    '''Creates tmp database with random name in given db url'''
    tmp_db_name = '.'.join([uuid.uuid4().hex, project_name, suffix])
    tmp_db_url = str(URL(db_url).with_path(tmp_db_name))
    create_database(tmp_db_url, **kwargs)

    try:
        yield tmp_db_url
    finally:
        drop_database(tmp_db_url)


# Represents test for 'data' migration.
# Contains revision to be tested, it's previous revision, and callbacks that
# could be used to perform validation.
MigrationValidationParamsGroup = namedtuple('MigrationData', [
    'rev_base', 'rev_head', 'on_init', 'on_upgrade', 'on_downgrade'
])


def load_migration_as_module(file: str):
    '''
    Allows to import alembic migration as a module.
    '''
    return importlib.machinery.SourceFileLoader(
        file,
        os.path.join(MIGRATIONS_PATH, file)
    ).load_module()


def make_validation_params_groups(
        *migrations
) -> List[MigrationValidationParamsGroup]:
    '''
    Creates objects that describe test for data migrations.
    See examples in tests/data_migrations/migration_*.py.
    '''
    data = []
    for migration in migrations:

        # Ensure migration has all required params
        for required_param in ['rev_base', 'rev_head']:
            if not hasattr(migration, required_param):
                raise RuntimeError(
                    '{param} not specified for {migration}'.format(
                        param=required_param,
                        migration=migration.__name__
                    )
                )

        # Set up callbacks
        callbacks = defaultdict(lambda: lambda *args, **kwargs: None)
        for callback in ['on_init', 'on_upgrade', 'on_downgrade']:
            if hasattr(migration, callback):
                callbacks[callback] = getattr(migration, callback)

        data.append(
            MigrationValidationParamsGroup(
                rev_base=migration.rev_base,
                rev_head=migration.rev_head,
                on_init=callbacks['on_init'],
                on_upgrade=callbacks['on_upgrade'],
                on_downgrade=callbacks['on_downgrade']
            )
        )

    return data
