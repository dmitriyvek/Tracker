from typing import List, Dict, Union

from asyncpg import Record
from asyncpgsa import PG
from graphene.types import ResolveInfo
from sqlalchemy import and_

from tracker.api.errors import APIException
from tracker.api.status_codes import StatusEnum
from tracker.db.schema import projects_table, roles_table


PROJECTS_REQUIRED_FIELDS = [
    projects_table.c.id,
    projects_table.c.title,
    projects_table.c.description,
    projects_table.c.created_at,
]

ROLES_REQUIRED_FIELDS = [
    roles_table.c.role,
    roles_table.c.user_id,
    roles_table.c.project_id,
    roles_table.c.assign_by,
    roles_table.c.assign_at,
]


def project_record_to_dict(record: Union[Record, Dict]) -> dict:
    '''Format project record'''
    return {
        'id': record['id'],
        'title': record['title'],
        'description': record['description'],
        'created_at': record['created_at'],
        'my_role': {
            'user_id': record['user_id'],
            'role': record['role'],
            'project_id': record['project_id'],
            'assign_by': record['assign_by'],
            'assign_at': record['assign_at'],
        }
    }


# TODO: may be universal
def check_role_requested_in_node(info: ResolveInfo) -> bool:
    '''Parses projectType node\'s field_asts and check if current user role is requested'''

    # TODO: assumed concrete field_asts structure, is it always the same?
    for inline_fragment in info.field_asts[0].selection_set.selections:
        if inline_fragment.type_condition.name.value == 'ProjectType':

            for field in inline_fragment.selection_set.selections:
                if field.name.value == 'myRole':
                    return True

            return False


def check_role_requested_in_list(info: ResolveInfo) -> bool:
    '''Parses project list query asts and checks if current user role is requested'''

    for field in info.field_asts[0].selection_set.selections:
        if field.name.value == 'myRole':
            return True

    return False


async def get_user_project_list(db: PG, info: ResolveInfo, user_id: int) -> List[Dict]:
    '''Get a list of all projects in which the user participates'''
    required_columns = [*PROJECTS_REQUIRED_FIELDS]
    role_in_request = check_role_requested_in_list(info)

    if role_in_request:
        required_columns.extend(ROLES_REQUIRED_FIELDS)

    query = projects_table.\
        join(
            roles_table,
            roles_table.c.project_id == projects_table.c.id
        ).\
        select().\
        with_only_columns(required_columns).\
        where(and_(
            roles_table.c.user_id == user_id,
            roles_table.c.is_deleted.is_(False),
            projects_table.c.is_deleted.is_(False)
        ))
    result = await db.query(query)

    if role_in_request:
        result = list(map(project_record_to_dict, result))
    else:
        result = list(map(lambda record: dict(record), result))

    return result


async def get_user_project_role(db: PG, project_id: int, user_id: int) -> Record:
    '''Get role with given user id and project id if not raise 403'''
    query = roles_table.\
        select().\
        with_only_columns([
            *ROLES_REQUIRED_FIELDS,
        ]).\
        where(and_(
            roles_table.c.user_id == user_id,
            roles_table.c.project_id == project_id,
            roles_table.c.is_deleted.is_(False)
        ))
    record = await db.fetchrow(query)

    if not record:
        raise APIException(
            'You are not a member of this project.',
            status=StatusEnum.FORBIDDEN.name
        )

    return record


async def get_user_project(db: PG, info: ResolveInfo, project_id: int, user_id: int) -> Union[Dict, None]:
    '''Get a project with given id. Raise 403 if user is not member of this project'''
    query = projects_table.\
        select().\
        with_only_columns([
            *PROJECTS_REQUIRED_FIELDS,
        ]).\
        where(and_(
            projects_table.c.id == project_id,
            projects_table.c.is_deleted.is_(False)
        ))
    project = await db.fetchrow(query)

    if not project:
        return None

    if not check_role_requested_in_node(info):
        return dict(project)

    role = await get_user_project_role(db, project_id, user_id)
    result = project_record_to_dict({**project, **role})

    return result


async def check_if_project_exists(db: PG, data: dict) -> None:
    '''Checks if project with given title is already exist if yes raises 400 error'''
    query = projects_table.\
        select().\
        with_only_columns([projects_table.c.id]).\
        where(projects_table.c.title == data['title'])

    result = await db.fetchrow(query)
    if result:
        raise APIException(
            'Project with given title is already exist.',
            status=StatusEnum.BAD_REQUEST.name
        )


async def create_project(db: PG, data: dict) -> dict:
    '''Creates and returns new project'''
    query = projects_table.insert().\
        returning(
            *PROJECTS_REQUIRED_FIELDS
    ).\
        values(data)

    project = dict(await db.fetchrow(query))
    return project


# query = union(projects_table.select().with_only_columns([literal_column('1').label('num'), projects_table.c.id]).where(projects_table.c.id == 2), roles_table.select(
# ).with_only_columns([literal_column('2').label('num'), roles_table.c.user_id]).where(roles_table.c.project_id == 2)).order_by('num')
