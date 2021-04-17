from base64 import b64decode, b64encode

from tests.utils import make_request_coroutines


async def test_user_detail_query(
    client,
    setup_project_list_test_retrun_auth_token
):
    auth_token = setup_project_list_test_retrun_auth_token

    max_fetch_number = client.server.app['config']['max_fetch_number']

    s = 'ProjectType:1'
    project_id = b64encode(s.encode('utf-8')).decode('utf-8')

    query = f'''
        {{
            node(id: "{project_id}") {{
                id
                ... on ProjectType {{
                    title
                    myRole {{
                        role
                    }}
                    createdBy {{
                        id
                        username
                        email
                    }}
                    roleList(first: 5) {{
                        totalCount
                        edges {{
                            cursor
                            node {{
                                userId
                                projectId
                                assignAt
                                assignBy
                                role
                                user {{
                                    id
                                    username
                                    email
                                }}
                            }}
                        }}
                        pageInfo {{
                            hasNextPage
                            hasPreviousPage
                            startCursor
                            endCursor
                        }}
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
        role_list = data['roleList']

        assert len(role_list['edges']) == 5
        assert role_list['edges'][0]['node']['user']['username']

        assert data['myRole']['role']
        assert data['createdBy']['username']
