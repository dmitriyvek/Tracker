import json

import jwt

from tests.utils import generate_user_data
from tracker.db.schema import users_table
from tracker.api.services.auth import (
    generate_password_hash
)
from tracker.api.services.auth.email_confirmation import (
    generate_email_confirmation_token
)
from tracker.api.status_codes import StatusEnum


async def test_email_confirmation_mutation(migrated_db_connection, client):
    app = client.server.app
    email = 'test@mail.com'

    user = generate_user_data(email=email)
    user['password'] = generate_password_hash(user['password'])
    db_query = users_table.insert().values(user).returning(users_table.c.id)
    user_id = migrated_db_connection.execute(db_query).fetchone()[0]

    db_query = users_table.select().\
        with_only_columns([users_table.c.is_confirmed]).\
        where(users_table.c.id == user_id)
    is_confirmed = migrated_db_connection.execute(db_query).fetchone()[0]
    assert not is_confirmed

    confirmation_token = generate_email_confirmation_token(
        config=app['config'],
        email=email
    )

    query = '''
        mutation ($input: EmailConfirmationInput!) {
            auth {
                emailConfirmation(input: $input) {
                    emailConfirmationPayload {
                        recordId
                        authToken
                        record {
                            id
                            username
                            email
                        }
                        status
                    }
                }
            }
        }
    '''
    variables = {
        'input': {
            'token': confirmation_token,
        },
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
    data = data['data']['auth']['emailConfirmation'][
        'emailConfirmationPayload']

    assert data['status'] == 'SUCCESS'
    assert data['recordId'] == user_id
    assert data['record']['email'] == email

    payload = jwt.decode(
        data['authToken'],
        app['config'].get('secret_key'),
        algorithms=['HS256'],
        options={
            'require_exp': True,
            'require_iat': True,
            'verify_exp': True,
            'verify_iat': True,
            'verify_signature': True,
        }
    )
    assert payload['sub'] == user_id

    db_query = users_table.select().\
        with_only_columns([users_table.c.is_confirmed]).\
        where(users_table.c.id == user_id)
    is_confirmed = migrated_db_connection.execute(db_query).fetchone()[0]
    assert is_confirmed

    # againg with same token
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
    assert data['errors'][0]['status'] == StatusEnum.BAD_REQUEST._name_

    # with invalid token
    response = await client.post(
        '/graphql',
        data=json.dumps({
            'query': query,
            'variables': json.dumps({
                'input': {
                    'token': 'invalid_token'
                }
            }),
        }),
        headers={
            'content-type': 'application/json',
        },
    )

    # if something will go wrong there will be response body output
    print(await response.text())

    assert response.status == 200

    data = await response.json()
    assert data['errors'][0]['status'] == StatusEnum.BAD_REQUEST._name_
