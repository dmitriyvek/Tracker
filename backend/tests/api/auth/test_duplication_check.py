import json

from tests.services import generate_user_data
from tracker.db.schema import users_table
from tracker.api.services.auth import (
    generate_password_hash
)


async def test_duplication_check_query(migrated_db_connection, client):
    app = client.server.app

    user = generate_user_data()
    raw_password = user['password']
    user['password'] = generate_password_hash(raw_password)
    db_query = users_table.insert().values(user).returning(users_table.c.id)
    migrated_db_connection.execute(db_query).fetchone()[0]


    query = '''
        query (
            $existent_username: Username!, 
            $nonexistent_username: Username!,
            $existent_email: Email!,
            $nonexistent_email: Email!
        ) 
        {
            auth {
                duplicationCheck {
                    existent_username: username(username: $existent_username)
                    nonexistent_username: username(username: $nonexistent_username)
                    existent_email: email(email: $existent_email)
                    nonexistent_email: email(email: $nonexistent_email)
                }
            }
        }
    '''
    variables = {
        'existent_username': user['username'],
        'nonexistent_username': 'test_username',
        'existent_email': user['email'],
        'nonexistent_email': 'test@mail.com',
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
    data = data['data']['auth']['duplicationCheck']

    assert data['existent_username'] is True
    assert data['nonexistent_username'] is False
    assert data['existent_email'] is True
    assert data['nonexistent_email'] is False
