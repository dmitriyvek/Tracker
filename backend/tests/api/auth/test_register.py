import json

import pytest
import jwt

from tests.utils import generate_user
from tracker.db.schema import users_table
from tracker.api.services.auth import check_password_hash


async def test_register_mutation(migrated_db_connection, client):
    user = generate_user()
    query = '''
        mutation register($input: RegisterInput!) {
            auth {
                register(input: $input) {
                    registerPayload {
                        status
                        authToken
                        recordId
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
            'email': user['email'],
            'password': user['password'],
        }
    }
    response = await client.post(
        '/graphql',
        data=json.dumps({
            'query': query,
            'variables': json.dumps(variables),
        }),
        headers={'content-type': 'application/json'},
    )

    # if something will go wrong there will be response body output
    print(await response.text())

    assert response.status == 200

    data = await response.json()
    data = data['data']['auth']['register']['registerPayload']
    app = client.server.app

    assert all([key in data for key in (
        'status', 'recordId', 'record', 'authToken')])
    assert data['status'] == 'SUCCESS'

    record = data['record']
    assert record['username'] == user['username']

    payload = jwt.decode(data['authToken'], app['config'].get(
        'secret_key'), algorithms=['HS256'])
    assert payload['sub'] == data['recordId']

    db_query = users_table.select().where(users_table.c.id == data['recordId'])
    db_record = migrated_db_connection.execute(db_query).fetchone()
    assert db_record['username'] == user['username']
    assert db_record['email'] == user['email']
    assert check_password_hash(db_record['password'], user['password'])
