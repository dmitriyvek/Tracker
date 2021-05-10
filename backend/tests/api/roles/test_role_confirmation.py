import json

import jwt

from tests.utils import generate_user_data
from tracker.db.schema import projects_table, users_table, roles_table
from tracker.api.services.auth import (
    generate_password_hash
)
from tracker.api.services.roles.email_confirmation import (
    generate_role_confirmation_token
)
from tracker.api.status_codes import StatusEnum


async def test_role_confirmation_mutation(migrated_db_connection, client):
    app = client.server.app
    email = 'test@mail.com'

    # create admin user
    admin = generate_user_data()
    admin['password'] = generate_password_hash(admin['password'])
    db_query = users_table.insert().values(admin).returning(users_table.c.id)
    admin_id = migrated_db_connection.execute(db_query).fetchone()[0]

    # create tested user
    user = generate_user_data(email=email)
    user['password'] = generate_password_hash(user['password'])
    db_query = users_table.insert().values(user).returning(users_table.c.id)
    user_id = migrated_db_connection.execute(db_query).fetchone()[0]

    db_query = users_table.select().\
        with_only_columns([users_table.c.is_confirmed]).\
        where(users_table.c.id == user_id)
    is_confirmed = migrated_db_connection.execute(db_query).fetchone()[0]
    assert not is_confirmed

    db_query = projects_table.insert().\
        values({'title': 'title1', 'created_by': admin_id}).\
        returning(projects_table.c.id)
    project_id = migrated_db_connection.execute(db_query).fetchone()[0]

    confirmation_token = generate_role_confirmation_token(
        config=app['config'],
        email=email,
        project_id=project_id,
        role='team_member',
        assign_by=admin_id
    )

    query = '''
        mutation RoleConfirmationMutation($input: RoleConfirmationInput!) {
            role {
                roleConfirmation(input: $input) {
                    roleConfirmationPayload {
                        status
                        authToken
                        nextUrl
                        record {
                            email
                        }
                        recordId
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
    data = data['data']['role']['roleConfirmation'][
        'roleConfirmationPayload']

    assert data['status'] == 'SUCCESS'
    assert data['recordId'] == user_id
    assert data['record']['email'] == email

    assert data['nextUrl'] is None

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

    db_query = roles_table.select().\
        with_only_columns([roles_table.c.project_id]).\
        where(roles_table.c.user_id == user_id)
    project_id_2 = migrated_db_connection.execute(db_query).fetchone()[0]
    assert project_id == project_id_2

    # user with new email
    confirmation_token = generate_role_confirmation_token(
        config=app['config'],
        email='unexistent@gmail.com',
        project_id=project_id,
        role='team_member',
        assign_by=admin_id
    )
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
    data = data['data']['role']['roleConfirmation'][
        'roleConfirmationPayload']

    assert data['status'] == 'MOVED_TEMPORARILY'
    assert data['recordId'] is None
    assert data['record'] is None
    assert data['authToken'] is None

    assert data['nextUrl'] == \
        f'http://localhost:3000/role/confirmation/register/{confirmation_token}'
