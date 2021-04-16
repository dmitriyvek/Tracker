import json

from graphql_relay import to_global_id

from tracker.api.services.auth import (
    generate_auth_token,
)
from tracker.api.status_codes import StatusEnum


async def test_role_duplication_query(
    client,
    setup_project_list_test_retrun_auth_token
):
    pm_auth_token = setup_project_list_test_retrun_auth_token

    app = client.server.app
    auth_token = generate_auth_token(app['config'], 2)

    query = '''
        query RoleDuplicationCheckQuery(
            $nonexistent_input: RoleDuplicationChecksInput!,
            $existent_input: RoleDuplicationChecksInput!
        ) {
            roles{
                duplicationCheck{
                    nonexistent: role(input: $nonexistent_input)
                    existent: role(input: $existent_input)
                }
            }
        }
    '''
    variables = {
        'nonexistent_input': {
            "projectId": to_global_id('ProjectType', 1),
            "userId": to_global_id('UserType', 3)
        },
        'existent_input': {
            "projectId": to_global_id('ProjectType', 1),
            "userId": to_global_id('UserType', 2)
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
    data = data['data']['roles']['duplicationCheck']
    assert data['nonexistent'] is False
    assert data['existent'] is True
