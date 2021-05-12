import sys

import pytest
from alembic.command import upgrade
from sqlalchemy import create_engine
from yarl import URL

from tracker.api.app import create_app
from tracker.utils.db import (
    get_alembic_config_from_url, get_db_url, tmp_database
)
from tracker.utils.loggers import setup_logger
from tracker.api.services.auth import (
    generate_auth_token, generate_password_hash
)
from tracker.db.schema import users_table
from tests.services import create_projects_in_db, generate_user_data


@pytest.fixture(scope='session')
def db_url():
    return get_db_url()


@pytest.fixture
def db(db_url):
    '''Creates empty temporary database.'''
    with tmp_database(db_url, 'pytest') as tmp_url:
        yield tmp_url


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
def migrated_db_connection(migrated_db):
    '''SQLAlchemy connection, bound to migrated temporary database.'''
    engine = create_engine(migrated_db, echo=False)
    conn = engine.connect()
    try:
        yield conn
    finally:
        conn.close()
        engine.dispose()


@pytest.fixture
def app_args(aiohttp_unused_port, migrated_db):
    port = aiohttp_unused_port()
    return [
        '--api-port', str(port),
        '--log-level', 'debug',
        '--db-url', migrated_db,
        '--api-host', '127.0.0.1',
    ]


@pytest.fixture()
async def client(aiohttp_client, app_args):
    # get rid of pytest params
    sys.argv = [sys.argv[0]]
    # set params needed for creating an app
    sys.argv.extend(app_args)
    app = create_app()

    # redirect log stream into tests root folder
    error_log_file_path = str(app['config']['error_log_file_path']).\
        replace('log', 'tests/log', 1)
    info_log_file_path = str(app['config']['info_log_file_path']).\
        replace('log', 'tests/log', 1)
    request_info_log_file_path = str(
        app['config']['request_info_log_file_path']
    ).replace('log', 'tests/log', 1)
    app['logger'] = setup_logger(
        app['config']['log_level'],
        error_log_file_path,
        info_log_file_path,
        request_info_log_file_path,
        app['config']['debug']
    )
    # app['logger'].remove()

    client = await aiohttp_client(app, server_kwargs={
        'port': app['config']['api_port']
    })

    try:
        yield client
    finally:
        await client.close()


# should be greater then 15 or max_fetch_number
NUMBER_OF_PROJECTS = 25
# should be greater then 10
NUMBER_OF_ROLES = 12


@pytest.fixture()
def setup_project_list_test_retrun_auth_token(client, migrated_db_connection):
    app = client.server.app

    user = generate_user_data()
    raw_password = user['password']
    user['password'] = generate_password_hash(raw_password)
    db_query = users_table.insert().values(user).returning(users_table.c.id)
    user_id = migrated_db_connection.execute(db_query).fetchone()[0]

    auth_token = generate_auth_token(app['config'], user_id=user_id)

    create_projects_in_db(
        migrated_db_connection,
        user_id,
        project_number=NUMBER_OF_PROJECTS,
        role_number=NUMBER_OF_ROLES
    )

    return auth_token
