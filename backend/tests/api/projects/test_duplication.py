import json


async def test_project_title_duplication_query(
    client,
    setup_project_list_test_retrun_auth_token
):
    auth_token = setup_project_list_test_retrun_auth_token

    query = '''
       query {
            projects {
                duplicationCheck {
                    existent: title(title: "test_title")
                    nonexistent: title(title: "random_titeleadf")
                }
            }
        }
    '''

    response = await client.post(
        '/graphql',
        data=json.dumps({
            'query': query,
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

    data = data['data']['projects']['duplicationCheck']
    assert data['nonexistent'] is False
    assert data['existent'] is True
