from datetime import datetime
from typing import Union

import jwt
from asyncpgsa import PG
from sqlalchemy.sql import select

from tracker.db.schema import blacklist_tokens_table


def generate_auth_token(
    config: dict,
    user_id: int,
) -> bytes:
    '''
    Generates the Auth Token with the given user_id.
    '''
    payload = {
        'exp': datetime.utcnow() + config.get('auth_token_expiration_time'),
        'iat': datetime.utcnow(),
        'sub': user_id
    }

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


async def decode_auth_token(
    db: PG,
    config: dict,
    token: str,
) -> Union[dict, None]:
    '''
    Decodes given token and return payload or None if token is invalid.
    '''
    try:
        payload = jwt.decode(
            token,
            config.get('secret_key'),
            algorithms=['HS256'],
            options={
                'require_exp': True,
                'require_iat': True,
                'verify_exp': True,
                'verify_iat': True,
                'verify_signature': True,
            }
        )
        if not payload.get('sub'):
            raise jwt.InvalidTokenError('Invalid auth token.')

        await check_if_token_is_blacklisted(db, token)

        return payload

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
