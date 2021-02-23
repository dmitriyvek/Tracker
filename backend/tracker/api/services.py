import base64
import json
from datetime import datetime

import bcrypt
import jwt
from asyncpgsa import PG
from sqlalchemy.sql import select, or_
from aiohttp.web import HTTPBadRequest, HTTPUnprocessableEntity, HTTPUnauthorized
from marshmallow.exceptions import ValidationError

from tracker.db.schema import BlacklistToken, User


def generate_auth_token(config: dict, user_id: int, email: str = '') -> bytes:
    '''Generates the Auth Token with the given user_id. If the email was also given then adds it to the payload (the token will be used for account confirmation).'''
    try:
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
    except Exception as e:
        return e


async def check_if_token_is_blacklisted(db: PG, token: str) -> None:
    '''Check if token is in the BlacklistToken table'''
    query = select([BlacklistToken.c.id]).where(
        BlacklistToken.c.token == token)
    result = await db.fetchrow(query)
    if result:
        error_message = {
            'status': 'fail',
            'message': 'Token is expired.'
        }
        raise HTTPUnauthorized(reason=error_message,
                               content_type='application/json')


async def decode_token(db: PG, config: dict, token: str, is_auth: bool = True) -> dict:
    '''Decodes given token and return payload or raise 401 error if token is invalid.'''
    try:
        payload = jwt.decode(token, config.get(
            'secret_key'), algorithms=['HS256'])
        await check_if_token_is_blacklisted(db, token)

        # if acoount confirmation token is used
        if (is_auth and payload.get('email')) or (not is_auth and not payload.get('email')):
            error_message = {
                'status': 'fail',
                'message': 'Invalid auth token is used.'
            }
            raise HTTPUnauthorized(reason=error_message,
                                   content_type='application/json')

        return payload

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as error:
        error_message = {
            'status': 'fail',
            'message': 'Signature expired.' if error is jwt.ExpiredSignatureError else 'Invalid token.'
        }
        raise HTTPUnauthorized(reason=error_message,
                               content_type='application/json')


async def create_blacklist_token(db: PG, auth_token: str) -> None:
    '''Creates blacklist token'''
    await db.fetchval(BlacklistToken.insert().values({'token': auth_token}))


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
    query = select([User.c.id]).where(or_(
        User.c.username == data['username'],
        User.c.email == data['email']
    ))
    result = await db.fetchrow(query)
    if result:
        error_message = {
            'status': 'fail',
            'message': 'User with given username or email is already exist.'
        }
        raise HTTPBadRequest(reason=error_message,
                             content_type='application/json')


async def create_user(db: PG, data: dict) -> dict:
    '''Creates and returns new user'''
    data['password'] = generate_password_hash(data['password'])
    query = User.insert().\
        returning(User.c.id, User.c.username, User.c.email).\
        values(data)
    user = dict(await db.fetchrow(query))

    return user


async def get_user(db: PG, data: dict) -> dict:
    '''Check if user with given credentials exist; if it does then returns this user else raise 401 error'''
    query = select([User.c.id, User.c.password]).where(
        User.c.username == data.get('username'))
    user = await db.fetchrow(query)

    if not (user and check_password_hash(
        user['password'], data.get('password')
    )):
        error_message = {
            'status': 'fail',
            'message': 'User with given credentials does not exist.'
        }
        raise HTTPUnauthorized(reason=error_message,
                               content_type='application/json')

    return dict(user)


def validate_input(data: dict, schema) -> dict:
    '''Validate given data with given Schema. If data is not valid abort 422 Response or 400 if no data provided.'''
    if not data:
        error_message = {
            'status': 'fail',
            'message': 'No data provided.'
        }
        raise HTTPBadRequest(reason=error_message,
                             content_type='application/json')

    try:
        data = json.loads(data)
        validate_data = schema().load(data)
    except ValidationError as error:
        error_message = {
            'status': 'fail',
            'message': error.messages
        }
        raise HTTPUnprocessableEntity(reason=error_message,
                                      content_type='application/json')

    return validate_data
