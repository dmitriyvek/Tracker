from typing import List, Dict

from asyncpgsa import PG
from graphene.types import ResolveInfo
from sqlalchemy import and_, func

from .base import PROJECTS_REQUIRED_FIELDS, format_project_type
from tracker.api.connections import modify_query_by_connection_params
from tracker.api.services.roles import ROLES_REQUIRED_FIELDS
from tracker.db.schema import roles_table, projects_table


def check_fields_requested_in_list(
    info: ResolveInfo,
    field_list: List[str]
) -> bool:
    '''Parses info field asts and checks if given fields is requested'''
    result = {field: False for field in field_list}

    for field in info.field_asts[0].selection_set.selections:
        if field.name.value == 'edges':
            for edge in field.selection_set.selections:
                if edge.name.value == 'node':
                    for type_field in edge.selection_set.selections:
                        if type_field.name.value in field_list:
                            result[type_field.name.value] = True

    return result


async def get_total_count_of_user_projects(db: PG, user_id: int) -> int:
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
    requested_fields = check_fields_requested_in_list(
        info,
        ['myRole']
    )
    my_role = requested_fields['myRole']

    if my_role:
        roles_fields = ROLES_REQUIRED_FIELDS.copy()
        roles_fields[0] = roles_fields[0].label('role_id')
        required_columns.extend(roles_fields)

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

    if my_role:
        result = list(map(format_project_type, result))
    else:
        result = list(map(lambda record: dict(record), result))

    return result
