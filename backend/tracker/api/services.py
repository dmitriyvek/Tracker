import base64
import json

import bcrypt
from aiohttp.web import HTTPBadRequest, HTTPUnprocessableEntity
from marshmallow.exceptions import ValidationError


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
