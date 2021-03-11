import json

import pytest
import jwt

from tests.utils import generate_user
from tracker.db.schema import users_table
from tracker.api.services import generate_password_hash, generate_auth_token


async def test_login_mutation(migrated_db_connection, client):
    app = client.server.app

    user = generate_user()
    raw_password = user['password']
    user['password'] = generate_password_hash(raw_password)
    db_query = users_table.insert().values(user).returning(users_table.c.id)
    db_record_id = migrated_db_connection.execute(db_query).fetchone()[0]

    auth_token = generate_auth_token(app['config'], db_record_id)

    query = '''
        mutation ($input: LoginInput!) {
            auth {
                login(input: $input) {
                    loginPayload {
                        status
                        recordId
                        authToken
                        record {
                            id
                            username
                        }
                    }
                }
            }
        }
    '''
    variables = {
        'input': {
            'username': user['username'],
            'password': raw_password,
        }
    }
    response = await client.post(
        '/graphql',
        data=json.dumps({
            'query': query,
            'variables': json.dumps(variables),
        }),
        headers={
            'content-type': 'application/json',
        },
    )

    # if something will go wrong there will be response body output
    print(await response.text())

    assert response.status == 200

    data = await response.json()
    data = data['data']['auth']['login']['loginPayload']

    assert all([key in data for key in (
        'status', 'recordId', 'record', 'authToken')])

    assert data['status'] == 'SUCCESS'
    assert data['recordId'] == db_record_id
    assert data['record']['username'] == user['username']

    payload = jwt.decode(data['authToken'], app['config'].get(
        'secret_key'), algorithms=['HS256'])
    assert payload['sub'] == db_record_id