import pytest

from tracker.api.services.auth import generate_password_hash, generate_auth_token
from tracker.db.schema import users_table
from tests.utils import generate_user_data, create_projects_in_db


# should be greater then 15 or max_fetch_number
NUMBER_OF_PROJECTS = 25


@pytest.fixture()
def setup_project_list_test_retrun_auth_token(client, migrated_db_connection):
    app = client.server.app

    user = generate_user_data()
    raw_password = user['password']
    user['password'] = generate_password_hash(raw_password)
    db_query = users_table.insert().values(user).returning(users_table.c.id)
    user_id = migrated_db_connection.execute(db_query).fetchone()[0]

    auth_token = generate_auth_token(app['config'], user_id)

    create_projects_in_db(
        migrated_db_connection,
        user_id,
        record_number=NUMBER_OF_PROJECTS
    )

    return auth_token
