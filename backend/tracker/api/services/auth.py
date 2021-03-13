import base64
import json
from datetime import datetime
from typing import Union

import bcrypt
import jwt
from asyncpgsa import PG
from sqlalchemy.sql import select, or_, and_

from tracker.api.errors import APIException
from tracker.api.status_codes import StatusEnum
from tracker.db.schema import blacklist_tokens_table, users_table


def generate_auth_token(config: dict, user_id: int, email: str = '') -> bytes:
    '''Generates the Auth Token with the given user_id. If the email was also given then adds it to the payload (the token will be used for account confirmation).'''
    payload = {
        'exp': datetime.utcnow() + config.get('token_expiration_time'),
        'iat': datetime.utcnow(),
        'sub': user_id,
    }
    if email:
        payload['email'] = email
    return jwt.encode(
        payload,
        config['secret_key'],
        algorithm='HS256'
    )


async def check_if_token_is_blacklisted(db: PG, token: str) -> None:
    '''Check if token is in the blacklist_tokens_table table'''
    query = select([blacklist_tokens_table.c.id]).where(
        blacklist_tokens_table.c.token == token)
    result = await db.fetchrow(query)
    if result:
        raise jwt.ExpiredSignatureError('Signature is expired.')
        # raise APIException('Token is expired.',
        #                    status=StatusEnum.UNAUTHORIZED.name)


async def decode_token(db: PG, config: dict, token: str, is_auth: bool = True) -> Union[dict, None]:
    '''Decodes given token and return payload or None if token is invalid.'''
    try:
        payload = jwt.decode(token, config.get(
            'secret_key'), algorithms=['HS256'])
        await check_if_token_is_blacklisted(db, token)

        # if acoount confirmation token is used
        if (is_auth and payload.get('email')) or (not is_auth and not payload.get('email')):
            raise jwt.InvalidTokenError('Email confirmation token is used')
            # raise APIException('Invalid auth token is used.',
            #                    status=StatusEnum.UNAUTHORIZED.name)

        return payload

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as error:
        return None
        #     message = 'Signature expired.' if error is jwt.ExpiredSignatureError else 'Invalid token.'
        #     raise APIException(message, status=StatusEnum.UNAUTHORIZED.name)


async def create_blacklist_token(db: PG, auth_token: str) -> None:
    '''Creates blacklist token'''
    await db.fetchval(blacklist_tokens_table.insert().values({'token': auth_token}))


def generate_password_hash(password: str, salt_rounds: int = 12) -> str:
    password_bin = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bin, bcrypt.gensalt(salt_rounds))
    encoded = base64.b64encode(hashed)
    return encoded.decode('utf-8')


def check_password_hash(encoded: str, password: str) -> bool:
    password = password.encode('utf-8')
    encoded = encoded.encode('utf-8')

    hashed = base64.b64decode(encoded)
    is_correct = bcrypt.hashpw(password, hashed) == hashed
    return is_correct


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


async def check_user_credentials(db: PG, data: dict) -> dict:
    '''Check if user with given credentials exist; if it does then returns this user else raise 401 error'''
    query = select([users_table.c.id, users_table.c.username, users_table.c.email, users_table.c.password]).\
        where(and_(
            users_table.c.username == data.get('username'),
            users_table.c.is_deleted.is_(False)
        ))
    user = await db.fetchrow(query)

    if not (user and check_password_hash(
        user['password'], data.get('password')
    )):
        raise APIException('User with given credentials does not exist.',
                           status=StatusEnum.UNAUTHORIZED.name)

    return dict(user)
