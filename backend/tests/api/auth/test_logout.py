import json

from tracker.api.services.auth import (
    generate_auth_token, generate_password_hash
)
from tracker.db.schema import users_table, blacklist_tokens_table
from tests.utils import generate_user_data


async def test_logout_mutation(migrated_db_connection, client):
    app = client.server.app

    user = generate_user_data()
    raw_password = user['password']
    user['password'] = generate_password_hash(raw_password)
    db_query = users_table.insert().values(user).returning(users_table.c.id)
    user_id = migrated_db_connection.execute(db_query).fetchone()[0]

    auth_token = generate_auth_token(app['config'], user_id=user_id)

    query = '''
        mutation{
            auth {
                logout {
                    logoutPayload {
                        status
                    }
                }
            }
        }
    '''
    response = await client.post(
        '/graphql',
        data=json.dumps({
            'query': query,
        }),
        headers={
            'content-type': 'application/json',
            'Authorization': f'Bearer {auth_token}'
        },
    )

    # if something will go wrong there will be response body output
    print(await response.text())

    assert response.status == 200

    data = await response.json()
    data = data['data']['auth']['logout']['logoutPayload']
    assert data['status'] == 'SUCCESS'

    db_query = blacklist_tokens_table.select().where(
        blacklist_tokens_table.c.token == auth_token)
    result = migrated_db_connection.execute(db_query)
    assert result.rowcount == 1

    # check login with blacklisted token
    query = '''
        {
            users {
                detail {
                    record {
                        id
                    }
                }
            }
        }
    '''
    response = await client.post(
        '/graphql', data=json.dumps({
            'query': query,
        }),
        headers={
            'content-type': 'application/json',
            'Authorization': f'Bearer {auth_token}'
        },
    )
    assert response.status == 200

    # if something will go wrong there will be response body output
    print(await response.text())

    data = await response.json()
    assert 'errors' in data
    assert data['errors'][0]['status'] == 'UNAUTHORIZED'
