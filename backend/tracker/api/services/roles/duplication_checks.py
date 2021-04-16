from asyncpgsa import PG
from sqlalchemy import and_, exists, select, literal_column

from tracker.db.schema import roles_table


async def check_user_role_duplication(
    db: PG, user_id: int, project_id: int
) -> bool:
    '''
    Checks if user already has a role in given project
    return True if it does
    '''
    query = roles_table.\
        select().\
        with_only_columns([literal_column('1')]).\
        where(and_(
            roles_table.c.user_id == user_id,
            roles_table.c.project_id == project_id,
            roles_table.c.is_deleted.is_(False)
        ))
    query = select([exists(query)])

    result = await db.fetchval(query)
    return result
