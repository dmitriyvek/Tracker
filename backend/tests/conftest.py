from types import SimpleNamespace

import pytest
from pytest_aiohttp import aiohttp_unused_port, aiohttp_client
from alembic.command import upgrade
from sqlalchemy import create_engine
from yarl import URL

from tracker.api.app import create_app
from tracker.utils.db import get_db_url, make_alembic_config, tmp_database, get_alembic_config_from_url


@pytest.fixture(scope='session')
def db_url():
    return get_db_url()


@pytest.fixture
def db(db_url):
    '''Creates empty temporary database.'''
    with tmp_database(db_url, 'pytest') as tmp_url:
        yield tmp_url


@pytest.fixture()
def postgres_engine(db):
    '''SQLAlchemy engine, bound to temporary database.'''
    engine = create_engine(db, echo=True)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture()
def alembic_config(db):
    '''Alembic configuration object, bound to temporary database.'''
    return get_alembic_config_from_url(db)


@pytest.fixture(scope='session')
def migrated_db_template(db_url):
    '''
    Creates temporary database and applies migrations.
    Database can be used as template to fast creation databases for tests.
    Has "session" scope, so is called only once per tests run.
    '''
    with tmp_database(db_url, 'template') as tmp_url:
        alembic_config = get_alembic_config_from_url(tmp_url)
        upgrade(alembic_config, 'head')
        yield tmp_url


@pytest.fixture
def migrated_db(db_url, migrated_db_template):
    '''
    Quickly creates clean migrated database using temporary database as base.
    Use this fixture in tests that require migrated database.
    '''
    template_db = URL(migrated_db_template).name
    with tmp_database(db_url, 'pytest', template=template_db) as tmp_url:
        yield tmp_url


@pytest.fixture
def app_args(aiohttp_unused_port, migrated_db):
    return [
        '--api-port', str(aiohttp_unused_port()),
        '--log-level', 'debug',
        '--db-url', migrated_db,
        '--api-address', '127.0.0.1'
    ]


@pytest.fixture
async def client(aiohttp_client, app_args):
    app = create_app(app_args)
    client = await aiohttp_client(app, server_kwargs={
        'port': int(app_args[1])
    })

    try:
        yield client
    finally:
        await client.close()
