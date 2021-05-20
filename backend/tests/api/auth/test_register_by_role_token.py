import json

import jwt

from tests.services import generate_user_data
from tracker.db.schema import projects_table, users_table, roles_table
from tracker.api.services.auth import (
    generate_password_hash
)
from tracker.api.services.roles.email_confirmation import (
    generate_role_confirmation_token
)


async def test_register_by_role_token(migrated_db_connection, client):
    USERNAME, PASSWORD = 'unique_username', 'password111'

    app = client.server.app
    email = 'test@mail.com'

    # create admin user
    admin = generate_user_data()
    admin['password'] = generate_password_hash(admin['password'])
    db_query = users_table.insert().values(admin).returning(users_table.c.id)
    admin_id = migrated_db_connection.execute(db_query).fetchone()[0]

    db_query = projects_table.insert().\
        values({'title': 'title1', 'created_by': admin_id}).\
        returning(projects_table.c.id)
    project_id = migrated_db_connection.execute(db_query).fetchone()[0]

    confirm_token = generate_role_confirmation_token(
        config=app['config'],
        email=email,
        project_id=project_id,
        role='team_member',
        assign_by=admin_id
    )

    query = '''
        mutation RegisterByRoleTokenMutation
            ($input: RegisterByRoleTokenInput!) {
            auth {
                registerByRoleToken(input: $input) {
                    registerByRoleTokenPayload {
                        status
                        authToken
                    }
                }
            }
        }
    '''
    variables = {
        'input': {
            'token': confirm_token,
            'username': USERNAME,
            'password': PASSWORD,
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
    data = data['data']['auth']['registerByRoleToken'][
        'registerByRoleTokenPayload']

    assert data['status'] == 'SUCCESS'
    assert data['authToken']
    assert jwt.decode(
        data['authToken'],
        app['config'].get('secret_key'),
        algorithms=['HS256'],
    )['sub']

    db_query = users_table.select().\
        with_only_columns([users_table.c.is_confirmed]).\
        where(users_table.c.username == USERNAME)
    is_confirmed = migrated_db_connection.execute(db_query).fetchone()[0]
    assert is_confirmed

    db_query = users_table.select().\
        with_only_columns([users_table.c.id]).\
        where(users_table.c.username == USERNAME)
    user_id = migrated_db_connection.execute(db_query).fetchone()[0]
    db_query = roles_table.select().\
        with_only_columns([roles_table.c.project_id]).\
        where(roles_table.c.user_id == user_id)
    project_id_2 = migrated_db_connection.execute(db_query).fetchone()[0]
    assert project_id == project_id_2

    # another time with the same token
    variables = {
        'input': {
            'token': confirm_token,
            'username': 'different_username',
            'password': 'password111'
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
    data = data['errors'][0]

    assert data['status'] == "BAD_REQUEST"

    # another time with invalid token
    variables = {
        'input': {
            'token': 'invalid_token',
            'username': 'different_username',
            'password': 'password111'
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
    data = data['errors'][0]

    assert data['status'] == "BAD_REQUEST"
