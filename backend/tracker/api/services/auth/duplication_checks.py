from asyncpgsa import PG
from sqlalchemy.sql.expression import select, exists, literal_column

from tracker.db.schema import users_table


async def check_credentials_duplication(
    db: PG, 
    username: str = '', 
    email: str = ''
) -> bool:
    '''
    Checks if user with given email or username if already exists
    (takes only username or only email)
    '''
    
    if username and email:
        raise ValueError('This function takes only username or only email')
    if not (username or email):
        raise ValueError('This function must takes username or email')

    query = users_table.\
        select().\
        with_only_columns([literal_column('1')])
    
    if username:
        query = query.where(users_table.c.username == username)
    else:
        query = query.where(users_table.c.email == email)

    query = select([exists(query)])

    result = await db.fetchval(query)
    return result

