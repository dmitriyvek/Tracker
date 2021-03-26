import pytest
from base64 import b64decode, b64encode

from .conftest import NUMBER_OF_PROJECTS, NUMBER_OF_ROLES
from tests.utils import make_request_coroutines


PROJ_NUM = 3

base_query = '''
    {{
        projects {{
            list(first: {proj_num}) {{
                totalCount
                edges {{
                    cursor
                    node {{
                        id
                        title
                        myRole {{
                            role
                        }}
                        roleList{params} {{
                            edges {{
                                node {{
                                    userId
                                    role
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
                pageInfo {{
                    startCursor
                    endCursor
                    hasNextPage
                    hasPreviousPage
                }}
            }}
        }}
    }}
    '''


async def test_project_list_with_nested_connections_first_only(
    client,
    setup_project_list_test_retrun_auth_token
):
    auth_token = setup_project_list_test_retrun_auth_token

    max_fetch_number = client.server.app['config']['max_fetch_number']

    query = base_query.format(proj_num=PROJ_NUM, params='(first: 3)')
    request_coroutine_list = make_request_coroutines(
        client=client, query=query, auth_token=auth_token)

    for request_coroutine in request_coroutine_list:
        response = await request_coroutine

        # if something will go wrong there will be response body output
        print(await response.text())

        assert response.status == 200

        data = await response.json()
        data = data['data']['projects']['list']['edges']
        first_role = data[0]['node']['roleList']
        pageinfo = first_role['pageInfo']

        assert len(first_role['edges']) == 3
        assert pageinfo['hasNextPage']
        assert not pageinfo['hasPreviousPage']

        decoded_cursor = b64decode(pageinfo['startCursor']).decode()
        assert decoded_cursor == 'RoleType:1'
        decoded_cursor = b64decode(pageinfo['endCursor']).decode()
        assert decoded_cursor == 'RoleType:3'


async def test_project_list_with_nested_connections_last_only(
    client,
    setup_project_list_test_retrun_auth_token
):
    auth_token = setup_project_list_test_retrun_auth_token

    max_fetch_number = client.server.app['config']['max_fetch_number']

    query = base_query.format(proj_num=PROJ_NUM, params='(last: 5)')
    request_coroutine_list = make_request_coroutines(
        client=client, query=query, auth_token=auth_token)

    for request_coroutine in request_coroutine_list:
        response = await request_coroutine

        # if something will go wrong there will be response body output
        print(await response.text())

        assert response.status == 200

        data = await response.json()
        data = data['data']['projects']['list']['edges']
        first_role = data[0]['node']['roleList']
        pageinfo = first_role['pageInfo']

        assert len(first_role['edges']) == 5
        assert not pageinfo['hasNextPage']
        assert pageinfo['hasPreviousPage']

        decoded_cursor = b64decode(pageinfo['startCursor']).decode()
        assert decoded_cursor == f'RoleType:{NUMBER_OF_ROLES - 4}'
        decoded_cursor = b64decode(pageinfo['endCursor']).decode()
        assert decoded_cursor == f'RoleType:{NUMBER_OF_ROLES}'


async def test_project_list_with_nested_connections_first_and_last(
    client,
    setup_project_list_test_retrun_auth_token
):
    auth_token = setup_project_list_test_retrun_auth_token

    max_fetch_number = client.server.app['config']['max_fetch_number']

    query = base_query.format(
        proj_num=PROJ_NUM, params='(first: 7, last: 4)'
    )
    request_coroutine_list = make_request_coroutines(
        client=client, query=query, auth_token=auth_token)

    for request_coroutine in request_coroutine_list:
        response = await request_coroutine

        # if something will go wrong there will be response body output
        print(await response.text())

        assert response.status == 200

        data = await response.json()
        data = data['data']['projects']['list']['edges']
        first_role = data[0]['node']['roleList']
        pageinfo = first_role['pageInfo']

        assert len(first_role['edges']) == 4
        assert not pageinfo['hasNextPage']
        assert pageinfo['hasPreviousPage']

        decoded_cursor = b64decode(pageinfo['startCursor']).decode()
        assert decoded_cursor == 'RoleType:4'
        decoded_cursor = b64decode(pageinfo['endCursor']).decode()
        assert decoded_cursor == 'RoleType:7'


async def test_project_list_with_nested_connections_after_only(
    client,
    setup_project_list_test_retrun_auth_token
):
    auth_token = setup_project_list_test_retrun_auth_token

    max_fetch_number = client.server.app['config']['max_fetch_number']

    query = base_query.format(
        proj_num=PROJ_NUM, params='(after: "test_fail")'
    )
    request_coroutine_list = make_request_coroutines(
        client=client, query=query, auth_token=auth_token)

    for request_coroutine in request_coroutine_list:
        response = await request_coroutine

        # if something will go wrong there will be response body output
        print(await response.text())

        assert response.status == 200

        data = await response.json()
        assert 'errors' in data
        assert data['errors'][0]['status'] == 'BAD_REQUEST'
