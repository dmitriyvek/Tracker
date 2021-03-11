import pytest
from sqlalchemy import create_engine

from tracker.utils.db import get_alembic_config_from_url


@pytest.fixture()
def db_engine(db):
    '''SQLAlchemy engine, bound to temporary database.'''
    engine = create_engine(db, echo=False)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture()
def alembic_config(db):
    '''Alembic configuration object, bound to temporary database.'''
    return get_alembic_config_from_url(db)
