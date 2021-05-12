import json

from sqlalchemy import and_

from tracker.api.services.auth import (
    generate_auth_token, generate_password_hash
)
from tests.services import generate_user_data
from tracker.db.schema import (
    UserRoleEnum, projects_table, roles_table, users_table
)


async def test_project_creation_mutation(migrated_db_connection, client):
    app = client.server.app

    user = generate_user_data()
    raw_password = user['password']
    user['password'] = generate_password_hash(raw_password)
    db_query = users_table.insert().values(user).returning(users_table.c.id)
    user_id = migrated_db_connection.execute(db_query).fetchone()[0]

    auth_token = generate_auth_token(app['config'], user_id=user_id)

    query = '''
        mutation projectCreation($input: ProjectCreationInput!) {
            project {
                projectCreation(input: $input) {
                    projectCreationPayload {
                        recordId
                        record {
                            id
                            title
                            description
                            myRole {
                                projectId
                                userId
                                role
                            }
                        }
                        status
                    }
                }
            }
        }
    '''
    variables = {
        'input': {
            'title': 'test_project',
            'description': 'test_description'
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
            'Authorization': f'Bearer {auth_token}'
        },
    )

    # if something will go wrong there will be response body output
    print(await response.text())

    assert response.status == 200

    data = await response.json()
    data = data['data']['project']['projectCreation']['projectCreationPayload']
    app = client.server.app

    assert all([key in data for key in (
        'status', 'recordId', 'record')])
    assert data['status'] == 'SUCCESS'

    record = data['record']
    assert record['title'] == variables['input']['title']

    role = record['myRole']
    assert role['projectId'] == data['recordId']
    assert role['userId'] == user_id
    assert role['role'] == UserRoleEnum.project_manager.name

    db_query = projects_table.\
        join(
            roles_table,
            roles_table.c.project_id == projects_table.c.id
        ).\
        select().\
        where(and_(
            projects_table.c.id == data['recordId'],
            roles_table.c.project_id == data['recordId']
        ))
    db_record = migrated_db_connection.execute(db_query).fetchone()

    assert db_record
