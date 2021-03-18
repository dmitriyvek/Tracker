from typing import List, Dict

from asyncpgsa import PG
from graphene.types import ResolveInfo
from sqlalchemy import and_

from .base import PROJECTS_REQUIRED_FIELDS, format_project_type
from tracker.api.services.roles import ROLES_REQUIRED_FIELDS
from tracker.db.schema import roles_table, projects_table


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
        result = list(map(format_project_type, result))
    else:
        result = list(map(lambda record: dict(record), result))

    return result
