from base64 import b64encode

from tests.services import make_request_coroutines


async def test_role_node_query(
    client,
    setup_project_list_test_retrun_auth_token
):
    auth_token = setup_project_list_test_retrun_auth_token

    s = 'RoleType:1'
    role_id = b64encode(s.encode('utf-8')).decode('utf-8')

    query = f'''
        {{
            node(id: "{role_id}") {{
                ... on RoleType {{
                    id
                    role
                    userId
                    projectId
                    assignBy
                    assignAt
                    user {{
                        id
                        username
                        email
                        registeredAt
                    }}
                }}
            }}
        }}
    '''
    request_coroutine_list = make_request_coroutines(
        client=client, query=query, auth_token=auth_token)

    for request_coroutine in request_coroutine_list:
        response = await request_coroutine

        # if something will go wrong there will be response body output
        print(await response.text())

        assert response.status == 200

        data = await response.json()
        data = data['data']['node']

        assert data['id'] == role_id
        assert data['user']['id']
