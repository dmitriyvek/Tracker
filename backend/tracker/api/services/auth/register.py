import base64

import bcrypt
from asyncpgsa import PG
from sqlalchemy import select, and_, or_

from tracker.api.errors import APIException
from tracker.api.status_codes import StatusEnum
from tracker.db.schema import users_table


def generate_password_hash(password: str, salt_rounds: int = 12) -> str:
    password_bin = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bin, bcrypt.gensalt(salt_rounds))
    encoded = base64.b64encode(hashed)
    return encoded.decode('utf-8')


async def check_if_user_exists(db: PG, data: dict) -> None:
    '''Checks if user with given username or email is already exist if yes raises 400 error'''
    query = select([users_table.c.id]).where(or_(
        and_(
            users_table.c.username == data['username'],
            users_table.c.is_deleted.is_(False)
        ),
        and_(
            users_table.c.email == data['email'],
            users_table.c.is_deleted.is_(False)
        )
    ))
    result = await db.fetchrow(query)
    if result:
        raise APIException(
            'User with given username or email is already exist.', status=StatusEnum.BAD_REQUEST.name)


async def create_user(db: PG, data: dict) -> dict:
    '''Creates and returns new user'''
    data['password'] = generate_password_hash(data['password'])
    query = users_table.insert().\
        returning(users_table.c.id, users_table.c.username, users_table.c.email).\
        values(data)
    user = dict(await db.fetchrow(query))

    return user
