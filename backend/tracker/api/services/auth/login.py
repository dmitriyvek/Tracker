import base64

import bcrypt
from asyncpgsa import PG
from sqlalchemy import select, and_

from tracker.api.errors import APIException
from tracker.api.status_codes import StatusEnum
from tracker.db.schema import users_table


def check_password_hash(encoded: str, password: str) -> bool:
    password = password.encode('utf-8')
    encoded = encoded.encode('utf-8')

    hashed = base64.b64decode(encoded)
    is_correct = bcrypt.hashpw(password, hashed) == hashed
    return is_correct


async def check_user_credentials(db: PG, data: dict) -> dict:
    '''
    Check if user with given credentials exist;
    if it does then returns this user else raise 401 error
    '''

    query = select([
        users_table.c.id,
        users_table.c.username,
        users_table.c.email,
        users_table.c.password,
        users_table.c.is_confirmed
    ]).\
        where(and_(
            users_table.c.username == data.get('username'),
            users_table.c.is_deleted.is_(False)
        ))
    user = await db.fetchrow(query)

    if not user['is_confirmed']:
        raise APIException('Your account is not confirmed yet. '
                           'Please, check verification letter on your email.',
                           status=StatusEnum.UNAUTHORIZED.name)

    if not (user and check_password_hash(
        user['password'], data.get('password')
    )):
        raise APIException('User with given credentials does not exist.',
                           status=StatusEnum.UNAUTHORIZED.name)

    return dict(user)
