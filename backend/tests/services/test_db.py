import pytest

from sqlalchemy import create_engine


def test_db(db):
    engine = create_engine(db)
    assert engine.execute('SELECT 1').scalar() == 1
    engine.dispose()
