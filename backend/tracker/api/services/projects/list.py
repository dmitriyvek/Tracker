from typing import List, Dict, Union

from asyncpgsa import PG
from graphene.types import ResolveInfo
from sqlalchemy import and_, func

from .base import PROJECTS_REQUIRED_FIELDS, format_project_type
from tracker.api.errors import APIException
from tracker.api.connections import modify_query_by_connection_params
from tracker.api.services.roles import ROLES_REQUIRED_FIELDS
from tracker.api.status_codes import StatusEnum
from tracker.db.schema import roles_table, projects_table


def check_role_requested_in_list(info: ResolveInfo) -> bool:
    '''Parses project list query asts and checks if current user role is requested'''

    for field in info.field_asts[0].selection_set.selections:
        if field.name.value == 'myRole':
            return True

    return False


async def get_total_count_of_user_projects(db: PG, user_id: int):
    '''Getting the total number of projects in which the user participates'''
    query = projects_table.\
        join(
            roles_table,
            roles_table.c.project_id == projects_table.c.id
        ).\
        select().\
        with_only_columns([
            func.count(projects_table.c.id).label('total_count')
        ]).\
        where(and_(
            roles_table.c.user_id == user_id,
            roles_table.c.is_deleted.is_(False),
            projects_table.c.is_deleted.is_(False)
        ))

    result = await db.fetchval(query)
    return result


async def get_user_project_list(
    db: PG,
    info: ResolveInfo,
    user_id: int,
    params: Dict[str, str]
) -> List[Dict]:
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

    query = modify_query_by_connection_params(query, projects_table, params)

    result = await db.query(query)

    if role_in_request:
        result = list(map(format_project_type, result))
    else:
        result = list(map(lambda record: dict(record), result))

    return result
