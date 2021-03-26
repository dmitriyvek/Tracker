from typing import Callable

import pytest
from alembic.command import downgrade, upgrade
from alembic.config import Config
from alembic.script import Script, ScriptDirectory

from .migrations_data import migration_680b3748447a
from tracker.utils.db import (
    get_alembic_config_from_url, make_validation_params_groups
)


def get_revisions():
    # Create Alembic configuration object
    # (we don't need database for getting revisions list)
    config = get_alembic_config_from_url()

    # Get directory object with Alembic migrations
    revisions_dir = ScriptDirectory.from_config(config)

    # Get & sort migrations, from first to last
    revisions = list(revisions_dir.walk_revisions('base', 'heads'))
    revisions.reverse()
    return revisions


@pytest.mark.parametrize('revision', get_revisions())
def test_migrations_stairway(alembic_config: Config, revision: Script):
    upgrade(alembic_config, revision.revision)

    # We need -1 for downgrading first migration (its down_revision is None)
    downgrade(alembic_config, revision.down_revision or '-1')
    upgrade(alembic_config, revision.revision)


def get_data_migrations():
    '''
    Returns tests for data migrations, from tests/migration_data folder.
    '''
    return make_validation_params_groups(
        migration_680b3748447a,
    )


@pytest.mark.parametrize(
    ('rev_base', 'rev_head', 'on_init', 'on_upgrade', 'on_downgrade'),
    get_data_migrations()
)
def test_data_migrations(
    alembic_config, db_engine, rev_base: str, rev_head: str,
    on_init: Callable, on_upgrade: Callable, on_downgrade: Callable
):
    # Upgrade to previous migration before target and add some data,
    # that would be changed by tested migration.
    upgrade(alembic_config, rev_base)
    on_init(engine=db_engine)

    # Perform upgrade in tested migration.
    # Check that data is migrated correctly in on_upgrade callback
    upgrade(alembic_config, rev_head)
    on_upgrade(engine=db_engine)

    # Perform downgrade in tested migration.
    # Check that changes are reverted back using on_downgrade callback
    downgrade(alembic_config, rev_base)
    on_downgrade(engine=db_engine)
