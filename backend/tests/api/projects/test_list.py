from base64 import b64decode, b64encode

from .conftest import NUMBER_OF_PROJECTS
from tests.utils import make_request_coroutines


base_query = '''
    {{
        projects {{
            list{params} {{
                edges {{
                    cursor
                    node {{
                        id
                        title
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


async def test_projects_list_query_with_no_params(
    client,
    setup_project_list_test_retrun_auth_token
):
    auth_token = setup_project_list_test_retrun_auth_token

    max_fetch_number = client.server.app['config']['max_fetch_number']

    query = base_query.format(params='')
    request_coroutine_list = make_request_coroutines(
        client=client, query=query, auth_token=auth_token)

    for request_coroutine in request_coroutine_list:
        response = await request_coroutine

        # if something will go wrong there will be response body output
        print(await response.text())

        assert response.status == 200

        data = await response.json()
        data = data['data']['projects']['list']
        pageinfo = data['pageInfo']

        assert len(data['edges']) == max_fetch_number
        assert pageinfo['hasNextPage']
        assert not pageinfo['hasPreviousPage']

        decoded_cursor = b64decode(pageinfo['startCursor']).decode()
        assert decoded_cursor == 'ProjectType:1'
        decoded_cursor = b64decode(pageinfo['endCursor']).decode()
        assert decoded_cursor == f'ProjectType:{max_fetch_number}'


async def test_projects_list_query_with_first_only(
    client,
    setup_project_list_test_retrun_auth_token
):
    auth_token = setup_project_list_test_retrun_auth_token

    query = base_query.format(params='(first: 5)')
    request_coroutine_list = make_request_coroutines(
        client=client, query=query, auth_token=auth_token)

    for request_coroutine in request_coroutine_list:
        response = await request_coroutine

        # if something will go wrong there will be response body output
        print(await response.text())

        assert response.status == 200

        data = await response.json()
        data = data['data']['projects']['list']
        pageinfo = data['pageInfo']

        assert len(data['edges']) == 5
        assert pageinfo['hasNextPage']
        assert not pageinfo['hasPreviousPage']

        decoded_cursor = b64decode(pageinfo['startCursor']).decode()
        assert decoded_cursor == 'ProjectType:1'
        decoded_cursor = b64decode(pageinfo['endCursor']).decode()
        assert decoded_cursor == 'ProjectType:5'

    # query with first greater then max_fetch_number
    max_fetch_number = client.server.app['config']['max_fetch_number']

    query = base_query.format(params=f'(first: {max_fetch_number + 10})')
    request_coroutine_list = make_request_coroutines(
        client=client, query=query, auth_token=auth_token)

    for request_coroutine in request_coroutine_list:
        response = await request_coroutine

        # if something will go wrong there will be response body output
        print(await response.text())

        assert response.status == 200

        data = await response.json()
        data = data['data']['projects']['list']
        pageinfo = data['pageInfo']

        assert len(data['edges']) == max_fetch_number
        assert pageinfo['hasNextPage']
        assert not pageinfo['hasPreviousPage']

        decoded_cursor = b64decode(pageinfo['startCursor']).decode()
        assert decoded_cursor == 'ProjectType:1'
        decoded_cursor = b64decode(pageinfo['endCursor']).decode()
        assert decoded_cursor == 'ProjectType:10'


async def test_projects_list_query_with_first_and_last(
    client,
    setup_project_list_test_retrun_auth_token
):
    auth_token = setup_project_list_test_retrun_auth_token

    query = base_query.format(params='(first: 10, last: 5)')
    request_coroutine_list = make_request_coroutines(
        client=client, query=query, auth_token=auth_token)

    for request_coroutine in request_coroutine_list:
        response = await request_coroutine

        # if something will go wrong there will be response body output
        print(await response.text())

        assert response.status == 200

        data = await response.json()
        data = data['data']['projects']['list']
        pageinfo = data['pageInfo']

        assert len(data['edges']) == 5
        assert not pageinfo['hasNextPage']
        assert pageinfo['hasPreviousPage']

        decoded_cursor = b64decode(pageinfo['startCursor']).decode()
        assert decoded_cursor == 'ProjectType:6'
        decoded_cursor = b64decode(pageinfo['endCursor']).decode()
        assert decoded_cursor == 'ProjectType:10'


async def test_projects_list_query_with_last_only(
    client,
    setup_project_list_test_retrun_auth_token
):
    auth_token = setup_project_list_test_retrun_auth_token

    query = base_query.format(params='(last: 5)')
    request_coroutine_list = make_request_coroutines(
        client=client, query=query, auth_token=auth_token)

    for request_coroutine in request_coroutine_list:
        response = await request_coroutine

        # if something will go wrong there will be response body output
        print(await response.text())

        assert response.status == 200

        data = await response.json()
        data = data['data']['projects']['list']
        pageinfo = data['pageInfo']

        assert len(data['edges']) == 5
        assert not pageinfo['hasNextPage']
        assert pageinfo['hasPreviousPage']

        decoded_cursor = b64decode(pageinfo['startCursor']).decode()
        assert decoded_cursor == f'ProjectType:{NUMBER_OF_PROJECTS - 4}'
        decoded_cursor = b64decode(pageinfo['endCursor']).decode()
        assert decoded_cursor == f'ProjectType:{NUMBER_OF_PROJECTS}'

    # query with last greater then max_fetch_number
    max_fetch_number = client.server.app['config']['max_fetch_number']

    query = base_query.format(params=f'(last: {max_fetch_number + 10})')
    request_coroutine_list = make_request_coroutines(
        client=client, query=query, auth_token=auth_token)

    for request_coroutine in request_coroutine_list:
        response = await request_coroutine

        # if something will go wrong there will be response body output
        print(await response.text())

        assert response.status == 200

        data = await response.json()
        data = data['data']['projects']['list']
        pageinfo = data['pageInfo']

        assert len(data['edges']) == max_fetch_number
        assert not pageinfo['hasNextPage']
        assert pageinfo['hasPreviousPage']

        decoded_cursor = b64decode(pageinfo['startCursor']).decode()
        assert decoded_cursor == \
            f'ProjectType:{NUMBER_OF_PROJECTS - max_fetch_number + 1}'
        decoded_cursor = b64decode(pageinfo['endCursor']).decode()
        assert decoded_cursor == f'ProjectType:{NUMBER_OF_PROJECTS}'


async def test_projects_list_query_with_after_only(
    client,
    setup_project_list_test_retrun_auth_token
):
    auth_token = setup_project_list_test_retrun_auth_token

    max_fetch_number = client.server.app['config']['max_fetch_number']
    s = 'ProjectType:3'
    cursor = b64encode(s.encode('utf-8')).decode('utf-8')

    query = base_query.format(params=f'(after: "{cursor}")')
    request_coroutine_list = make_request_coroutines(
        client=client, query=query, auth_token=auth_token)

    for request_coroutine in request_coroutine_list:
        response = await request_coroutine

        # if something will go wrong there will be response body output
        print(await response.text())

        assert response.status == 200

        data = await response.json()
        data = data['data']['projects']['list']
        pageinfo = data['pageInfo']

        assert len(data['edges']) == max_fetch_number
        assert pageinfo['hasNextPage']
        assert pageinfo['hasPreviousPage']

        decoded_cursor = b64decode(pageinfo['startCursor']).decode()
        assert decoded_cursor == 'ProjectType:4'
        decoded_cursor = b64decode(pageinfo['endCursor']).decode()
        assert decoded_cursor == f'ProjectType:{max_fetch_number + 3}'


async def test_projects_list_query_with_before_only(
    client,
    setup_project_list_test_retrun_auth_token
):
    auth_token = setup_project_list_test_retrun_auth_token

    s = 'ProjectType:5'
    cursor = b64encode(s.encode('utf-8')).decode('utf-8')

    query = base_query.format(params=f'(before: "{cursor}")')
    request_coroutine_list = make_request_coroutines(
        client=client, query=query, auth_token=auth_token)

    for request_coroutine in request_coroutine_list:
        response = await request_coroutine

        # if something will go wrong there will be response body output
        print(await response.text())

        assert response.status == 200

        data = await response.json()
        data = data['data']['projects']['list']
        pageinfo = data['pageInfo']

        assert len(data['edges']) == 4
        assert pageinfo['hasNextPage']
        assert not pageinfo['hasPreviousPage']

        decoded_cursor = b64decode(pageinfo['startCursor']).decode()
        assert decoded_cursor == 'ProjectType:1'
        decoded_cursor = b64decode(pageinfo['endCursor']).decode()
        assert decoded_cursor == 'ProjectType:4'
