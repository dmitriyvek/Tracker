from asyncpgsa import PG
from sqlalchemy import and_, exists, select, literal_column

from tracker.db.schema import projects_table


async def check_title_duplication(db: PG, user_id: int, title: str) -> bool:
    '''
    Checks if project with given title is already created by given user
    return True if it does
    '''
    query = projects_table.\
        select().\
        with_only_columns([literal_column('1')]).\
        where(and_(
            projects_table.c.title == title,
            projects_table.c.created_by == user_id
        ))
    query = select([exists(query)])

    result = await db.fetchval(query)
    return result
