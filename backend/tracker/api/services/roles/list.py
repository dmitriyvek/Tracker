from typing import List, Dict

from asyncpgsa import PG
from graphene.types import ResolveInfo
from sqlalchemy import func, and_

from tracker.api.connections import modify_query_by_connection_params
from tracker.api.services.roles import ROLES_REQUIRED_FIELDS
from tracker.db.schema import roles_table


async def get_total_count_of_roles_in_project(db: PG, project_id: int) -> int:
    '''Getting the total number of roles in given project'''
    query = roles_table.\
        select().\
        with_only_columns([
            func.count(roles_table.c.id).label('total_count')
        ]).\
        where(and_(
            roles_table.c.project_id == project_id,
            roles_table.c.is_deleted.is_(False)
        ))

    result = await db.fetchval(query)
    return result


async def get_projects_role_list(
    db: PG,
    info: ResolveInfo,
    project_id: int,
    params: Dict[str, str]
) -> List[Dict]:
    '''Get a list of all roles in given project'''

    query = roles_table.\
        select().\
        with_only_columns(ROLES_REQUIRED_FIELDS).\
        where(and_(
            roles_table.c.project_id == project_id,
            roles_table.c.is_deleted.is_(False),
        ))

    query = modify_query_by_connection_params(query, roles_table, params)

    result = await db.query(query)

    result = list(map(lambda record: dict(record), result))
    return result
