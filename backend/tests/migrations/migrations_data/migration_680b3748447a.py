'''
Data migration test example.
MUST-have properties:
  - rev_base
    Previous migration identifier
  - rev_head
    Current (being tested) migration identifier
Optional properties:
  - on_init(engine)
    Is called before applying 'rev_head' migration. Can be used to add some
    data before migration is applied.
  - on_upgrade(engine)
    Is called after applying 'rev_head' migration. Can be used to check data
    was migrated successfully by upgrade() migration method.
  - on_downgrade(engine)
    Is called after migration is rolled back to 'rev_base'. Can be used to
    check data was rolled back to initial state.
'''

from sqlalchemy import Table, select
from sqlalchemy.engine import Engine

from tracker.utils.db import load_migration_as_module


# Load migration as module
migration = load_migration_as_module('680b3748447a_add_username.py')
rev_base: str = migration.down_revision
rev_head: str = migration.revision

# We can reuse objects from migration.
# users_table object with legacy & new columns would be very handy.
users_table: Table = migration.users_table

# Pytest call each test in separate process, so you could use global variables
# for this test to store state.
users = (
    {
        'id': 1,
        'email': 'john.smith@example.com',
        'username': 'john.smith',
        'password': 'zxcfghuio',
    },
    {
        'id': 2,
        'email': 'josephine.smith@example.com',
        'username': 'josephine.smith',
        'password': 'zxcfghuio',
    },
)


def on_init(engine: Engine):
    '''Create row in users table before migration is applied'''
    global users

    with engine.connect() as conn:
        query = users_table.insert().values([
            {
                'id': user['id'],
                'email': user['email'],
                'password': user['password'],
            }
            for user in users
        ])
        conn.execute(query)


def on_upgrade(engine: Engine):
    '''Ensure that data was successfully migrated'''
    global users

    with engine.connect() as conn:
        query = select([
            users_table.c.id,
            users_table.c.username,
        ])

        actual = {
            user['id']: user
            for user in conn.execute(query).fetchall()
        }

        for user in users:
            assert user['id'] in actual
            assert user['username'] == actual[user['id']]['username']


def on_downgrade(engine: Engine):
    '''Ensure that data changes were rolled back'''
    global users

    with engine.connect() as conn:
        query = select([
            users_table.c.id,
            users_table.c.email
        ])

        actual = {
            user['id']: user
            for user in conn.execute(query).fetchall()
        }

        for user in users:
            assert user['id'] in actual
            assert user['email'] == actual[user['id']]['email']
