import datetime
import json
from typing import Optional, List
from types import CoroutineType
from urllib.parse import urlencode

from faker import Faker


fake = Faker()
# Faker.seed(4321)


def generate_user(
    id: Optional[int] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    email: Optional[str] = None,
    registered_at: Optional[datetime.datetime] = None,
    is_admin: Optional[bool] = None,
    is_deleted: Optional[bool] = None,
) -> dict:
    record = {}
    if id:
        record['id'] = id
    if registered_at:
        record['registered_at'] = registered_at
    if is_admin:
        record['is_admin'] = is_admin
    if is_deleted:
        record['is_deleted'] = is_deleted

    record['username'] = username if username else fake.first_name()
    record['password'] = password if password else fake.password(length=9)
    record['email'] = email if email else fake.email(domain=None)

    return record


def url_string(**url_params):
    base_url = '/graphql'

    if url_params:
        return f'{base_url}?{urlencode(url_params)}'

    return base_url


def make_request_coroutines(
    client,
    query: str,
    variables: Optional[dict] = None,
    auth_token: Optional[str] = None
) -> List[CoroutineType]:
    '''Returns list of get and post request coroutines'''

    get_headers = {}
    if auth_token:
        get_headers['Authorization'] = f'Bearer {auth_token}'

    get_request = client.get(
        url_string(query=query),
        headers=get_headers,
    )

    post_headers = get_headers.copy()
    post_headers['content-type'] = 'application/json'

    post_data = {
        'query': query,
    }
    if variables:
        post_data['variables'] = json.dumps(variables)

    post_request = client.post(
        '/graphql',
        data=json.dumps(post_data),
        headers=post_headers,
    )

    return [get_request, post_request]
