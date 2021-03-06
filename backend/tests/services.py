import datetime
import json
from random import randint
from typing import Optional, List
from types import CoroutineType
from urllib.parse import urlencode

from faker import Faker
from sqlalchemy.engine import Connection

from tracker.db.schema import (
    UserRoleEnum, projects_table, roles_table, users_table
)


fake = Faker()
# Faker.seed(4321)


def generate_project_data(
    created_by: int,

    id: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    created_at: Optional[datetime.datetime] = None,
    is_deleted: Optional[bool] = None,
) -> dict:
    record = {}

    if id:
        record['id'] = id
    if created_at:
        record['created_at'] = created_at
    if is_deleted:
        record['is_deleted'] = is_deleted

    record['created_by'] = created_by
    record['title'] = title if title else fake.unique.word()
    record['description'] = description if description else fake.paragraph(
        nb_sentences=2)

    return record


def generate_user_data(
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

    record['username'] = username if username else fake.unique.first_name()
    record['password'] = password if password else fake.password(length=9)
    record['email'] = email if email else fake.unique.email(domain=None)

    return record


def url_string(**url_params):
    base_url = '/graphql'

    if url_params:
        return f'{base_url}?{urlencode(url_params)}'

    return base_url


def make_request_coroutines(
    client,
    query: str,
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

    post_request = client.post(
        '/graphql',
        data=json.dumps({
            'query': query,
        }),
        headers=post_headers,
    )

    return [get_request, post_request]


def create_projects_in_db(
    db_conn: Connection,
    user_id: int,
    project_number: int = 5,
    role_number: int = 5,
) -> dict:
    '''
    Creates several projects with several associated roles in database
    '''
    # create users for roles
    user_list = [
        generate_user_data()
        for _ in range(role_number - 1)
    ]

    query = users_table.insert().values(
        user_list).returning(users_table.c.id)
    result = db_conn.execute(query)

    users_id_list = []
    for user in result.fetchall():
        users_id_list.append(user['id'])

    # create projects
    project_list = [
        generate_project_data(created_by=user_id)
        for _ in range(project_number - 1)
    ]
    project_list.append(
        generate_project_data(created_by=user_id, title='test_title')
    )

    query = projects_table.insert().values(
        project_list).returning(projects_table.c.id)
    result = db_conn.execute(query)

    projects_id_list = []
    for project in result.fetchall():
        projects_id_list.append(project['id'])

    # create roles
    # role_pool = [key.name for key in UserRoleEnum]
    role_pool = ['team_member', 'viewer']
    role_pool_len = len(role_pool)

    role_list = []
    for project_id in projects_id_list:
        role_list.append({
            'role': UserRoleEnum.project_manager,
            'user_id': user_id,
            'assign_by': user_id,
            'project_id': project_id
        })
        for i in range(role_number - 1):
            if users_id_list[i] != 3:
                role_list.append({
                    'role': role_pool[randint(0, role_pool_len - 1)],
                    'user_id': users_id_list[i],
                    'assign_by': user_id,
                    'project_id': project_id
                })

    query = roles_table.insert().values(
        role_list).returning(roles_table.c.id)
    result = db_conn.execute(query)

    return {
        'project_list': project_list,
        'role_list': role_list
    }
