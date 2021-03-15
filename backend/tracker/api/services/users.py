from asyncpgsa import PG
from sqlalchemy import and_

from tracker.db.schema import users_table


async def get_user_by_id(db: PG, user_id: int) -> dict:
    '''Get user with given id'''
    query = users_table.\
        select().\
        with_only_columns([
            users_table.c.id,
            users_table.c.username,
            users_table.c.email,
            users_table.c.registered_at
        ]).\
        where(and_(
            users_table.c.id == user_id,
            users_table.c.is_deleted.is_(False)
        ))

    result = await db.fetchrow(query)
    return dict(result)
