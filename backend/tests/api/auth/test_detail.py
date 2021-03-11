import base64

import pytest

from tests.utils import generate_user, make_request_coroutines
from tracker.db.schema import users_table
from tracker.api.services import generate_password_hash, generate_auth_token


async def test_detail_mutation(migrated_db_connection, client):
    app = client.server.app

    user = generate_user()
    raw_password = user['password']
    user['password'] = generate_password_hash(raw_password)
    db_query = users_table.insert().values(user).returning(users_table.c.id)
    db_record_id = migrated_db_connection.execute(db_query).fetchone()[0]

    auth_token = generate_auth_token(app['config'], db_record_id)

    query = '''
        {
            auth {
                detail {
                    record {
                        id
                        username
                        email
                    }
                }
            }
        }
    '''
    request_coroutine_list = make_request_coroutines(
        client=client, query=query, auth_token=auth_token)

    for request_coroutine in request_coroutine_list:
        response = await request_coroutine

        # if something will go wrong there will be response body output
        print(await response.text())

        assert response.status == 200

        data = await response.json()
        data = data['data']['auth']['detail']['record']

        id = base64.b64decode(data['id']).decode('utf-8').split(':')[1]
        assert int(id) == db_record_id
        assert data['username'] == user['username']
        assert data['email'] == user['email']