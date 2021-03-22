import base64

import pytest

from tracker.api.services.auth import generate_password_hash, generate_auth_token
from tracker.db.schema import users_table
from tests.utils import generate_user_data, make_request_coroutines, create_projects_in_db


async def test_user_detail_query(migrated_db_connection, client):
    app = client.server.app

    user = generate_user_data()
    raw_password = user['password']
    user['password'] = generate_password_hash(raw_password)
    db_query = users_table.insert().values(user).returning(users_table.c.id)
    user_id = migrated_db_connection.execute(db_query).fetchone()[0]

    auth_token = generate_auth_token(app['config'], user_id)

    create_projects_in_db(migrated_db_connection, user_id, record_number=5)

    query = '''
        {
            users {
                detail {
                    record {
                        id
                        username
                        projectList(first: 5, last:3) {
                            totalCount
                            edges {
                                cursor
                                node {
                                    title
                                    id
                                }
                            }
                            pageInfo {
                                endCursor
                                startCursor
                                hasNextPage
                                hasPreviousPage
                            }
                        }
                    }
                }
            }
        }
    '''
    request_coroutine_list = make_request_coroutines(
        client=client, query=query, auth_token=auth_token)

    for request_coroutine in request_coroutine_list:
        response = await request_coroutine

        # if something will go wrong there will be response body output
        print(await response.text())

        assert response.status == 200

        data = await response.json()
        data = data['data']['users']['detail']['record']

        id = base64.b64decode(data['id']).decode('utf-8').split(':')[1]
        assert int(id) == user_id
        assert data['username'] == user['username']

        assert data['projectList']
