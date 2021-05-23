import json

from graphql_relay import to_global_id

from tests.services import generate_user_data
from tracker.api.services.auth import (
    generate_auth_token,
    generate_password_hash,
)
from tracker.db.schema import (
    UserRoleEnum, projects_table, users_table, roles_table
)


query = '''
    mutation RoleDeletionMutation ($input: RoleDeletionInput!) {
        role {
            roleDeletion(input: $input) {
                roleDeletionPayload {
                    status
                }
            }
        }
    }
'''


async def test_role_deletion_mutation(migrated_db_connection, client):
    app = client.server.app

    # create admin user
    admin = generate_user_data()
    admin['password'] = generate_password_hash(admin['password'])
    db_query = users_table.insert().values(admin).returning(users_table.c.id)
    admin_id = migrated_db_connection.execute(db_query).fetchone()[0]

    # create tested users
    user1 = generate_user_data()
    user2 = generate_user_data()
    user1['password'] = generate_password_hash(user1['password'])
    user1['is_confirmed'], user2['is_confirmed'] = True, True
    user2['password'] = generate_password_hash(user2['password'])
    db_query = users_table.insert().values([user1, user2])
    migrated_db_connection.execute(db_query)

    db_query = projects_table.insert().\
        values({'title': 'title1', 'created_by': admin_id}).\
        returning(projects_table.c.id)
    project_id = migrated_db_connection.execute(db_query).fetchone()[0]

    # create tested users roles
    admin_role = {}
    admin_role['user_id'] = 1
    admin_role['role'] = UserRoleEnum.project_manager.value
    admin_role['project_id'] = project_id
    admin_role['assign_by'] = admin_id
    role1 = admin_role.copy()
    role1['user_id'] = 2
    role2 = role1.copy()
    role2['user_id'] = 3
    role2['role'] = UserRoleEnum.team_member.value
    db_query = roles_table.insert().values([admin_role, role1, role2])
    migrated_db_connection.execute(db_query)

    admin_role_id = to_global_id('RoleType', 1)
    role1_id = to_global_id('RoleType', 2)
    role2_id = to_global_id('RoleType', 3)

    admin_auth_token = generate_auth_token(app['config'], user_id=1)
    user1_auth_token = generate_auth_token(app['config'], user_id=2)
    user2_auth_token = generate_auth_token(app['config'], user_id=3)

    # try to delete pm role by team member
    variables = {
        'input': {
            'roleId': role1_id,
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
            'Authorization': f'Bearer {user2_auth_token}',
        },
    )

    # if something will go wrong there will be response body output
    print(await response.text())

    assert response.status == 200

    data = await response.json()
    error = data['errors'][0]['status']
    data = data['data']['role']['roleDeletion']

    assert not data
    assert error == 'FORBIDDEN'

    # try to delete invalid role
    variables = {
        'input': {
            'roleId': 'invalid_id',
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
            'Authorization': f'Bearer {user2_auth_token}',
        },
    )

    # if something will go wrong there will be response body output
    print(await response.text())

    assert response.status == 200

    data = await response.json()
    error = data['errors'][0]['status']
    data = data['data']['role']['roleDeletion']

    assert not data
    assert error == 'ENPROCESSABLE_ENTITY'

    # try to delete another invalid role
    variables = {
        'input': {
            'roleId': to_global_id('RoleType', 9999999),
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
            'Authorization': f'Bearer {user2_auth_token}',
        },
    )

    # if something will go wrong there will be response body output
    print(await response.text())

    assert response.status == 200

    data = await response.json()
    error = data['errors'][0]['status']
    data = data['data']['role']['roleDeletion']

    assert not data
    assert error == 'BAD_REQUEST'

    # delete team member by pm
    variables = {
        'input': {
            'roleId': role2_id,
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
            'Authorization': f'Bearer {user1_auth_token}',
        },
    )

    # if something will go wrong there will be response body output
    print(await response.text())

    assert response.status == 200

    data = await response.json()
    data = data['data']['role']['roleDeletion']['roleDeletionPayload']

    assert data['status'] == 'SUCCESS'

    # try to delete proejc's creator by pm
    variables = {
        'input': {
            'roleId': admin_role_id,
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
            'Authorization': f'Bearer {user2_auth_token}',
        },
    )

    # if something will go wrong there will be response body output
    print(await response.text())

    assert response.status == 200

    data = await response.json()
    error = data['errors'][0]['status']
    data = data['data']['role']['roleDeletion']

    assert not data
    assert error == 'FORBIDDEN'

    # delete pm by project's creator
    variables = {
        'input': {
            'roleId': role1_id,
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
            'Authorization': f'Bearer {admin_auth_token}',
        },
    )

    # if something will go wrong there will be response body output
    print(await response.text())

    assert response.status == 200

    data = await response.json()
    data = data['data']['role']['roleDeletion']['roleDeletionPayload']

    assert data['status'] == 'SUCCESS'
