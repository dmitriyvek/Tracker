from datetime import datetime
from typing import Union

import jwt
from asyncpgsa import PG
from sqlalchemy.sql import select

from tracker.db.schema import blacklist_tokens_table


def generate_auth_token(
    config: dict,
    user_id: int = None,
    email: str = None
) -> bytes:
    '''
    Generates the Auth Token with the given user_id.
    Generates the Account Confirmation Token with the given email.
    You can pass only user_id or email.
    '''
    if user_id and email:
        raise ValueError('You can pass only user_id or email.')
    if not (user_id or email):
        raise ValueError('You must pass user_id or email.')

    payload = {
        'exp': datetime.utcnow() + config.get('token_expiration_time'),
        'iat': datetime.utcnow(),
    }

    if user_id:
        payload['sub'] = user_id
    else:
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


async def decode_token(
    db: PG,
    config: dict,
    token: str,
    is_auth: bool = True
) -> Union[dict, None]:
    '''
    Decodes given token and return payload or None if token is invalid.
    '''

    try:
        payload = jwt.decode(token, config.get(
            'secret_key'), algorithms=['HS256'])
        await check_if_token_is_blacklisted(db, token)

        # if acoount confirmation token is used
        if (is_auth and payload.get('email')) or \
                (not is_auth and not payload.get('email')):
            raise jwt.InvalidTokenError('Email confirmation token is used')
            # raise APIException('Invalid auth token is used.',
            #                    status=StatusEnum.UNAUTHORIZED.name)

        return payload

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as error:
        return None
        #     message = 'Signature expired.' if error is jwt.ExpiredSignatureError else 'Invalid token.'
        #     raise APIException(message, status=StatusEnum.UNAUTHORIZED.name)
