import json

from graphql_relay import to_global_id

from tracker.api.services.auth import (
    generate_auth_token,
)
from tracker.api.status_codes import StatusEnum


async def test_create_role_mutation(
    client,
    setup_project_list_test_retrun_auth_token
):
    pm_auth_token = setup_project_list_test_retrun_auth_token

    app = client.server.app
    auth_token = generate_auth_token(app['config'], user_id=2)

    query = '''
        mutation RoleCreationMutation($input: RoleCreationInput!) {
            role {
                roleCreation(input: $input) {
                    roleCreationPayload {
                        recordId
                        record {
                            assignBy
                            assignAt
                            role
                            userId
                            projectId
                        }
                        status
                    }
                }
            }
        }
    '''
    variables = {
        'input': {
            "projectId": to_global_id('ProjectType', 1),
            "role": "team_member",
            "userId": to_global_id('UserType', 3)
        }
    }

    # with no pm token
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
    assert data['errors'][0]['status'] == StatusEnum.FORBIDDEN._name_

    # with pm token
    response = await client.post(
        '/graphql',
        data=json.dumps({
            'query': query,
            'variables': json.dumps(variables),
        }),
        headers={
            'content-type': 'application/json',
            'Authorization': f'Bearer {pm_auth_token}'
        },
    )

    # if something will go wrong there will be response body output
    print(await response.text())

    assert response.status == 200

    data = await response.json()
    assert data['data']['role']['roleCreation'][
        'roleCreationPayload']['status'] == 'SUCCESS'
    assert data['data']['role']['roleCreation'][
        'roleCreationPayload']['recordId']

    # with pm token add already existed user
    response = await client.post(
        '/graphql',
        data=json.dumps({
            'query': query,
            'variables': json.dumps(variables),
        }),
        headers={
            'content-type': 'application/json',
            'Authorization': f'Bearer {pm_auth_token}'
        },
    )

    # if something will go wrong there will be response body output
    print(await response.text())

    assert response.status == 200

    data = await response.json()
    assert data['errors'][0]['status'] == StatusEnum.BAD_REQUEST._name_

    # with invalid user id
    variables = {
        'input': {
            "projectId": to_global_id('ProjectType', 1),
            "role": "team_member",
            "userId": to_global_id('UserType', 30000000)
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
            'Authorization': f'Bearer {pm_auth_token}'
        },
    )

    # if something will go wrong there will be response body output
    print(await response.text())

    assert response.status == 200

    data = await response.json()
    assert data['errors'][0]['status'] == StatusEnum.BAD_REQUEST._name_
