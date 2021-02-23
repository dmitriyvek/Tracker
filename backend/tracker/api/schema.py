from aiohttp.web import HTTPUnauthorized
from marshmallow import Schema, ValidationError, validates, validates_schema
from marshmallow.fields import Dict, Int, List, Nested, Str
from marshmallow.validate import Length, OneOf, Range, Email


class UserRegistrationSchema(Schema):
    username = Str(required=True, validate=Length(min=4, max=64))
    password = Str(required=True, validate=Length(min=6, max=64))
    email = Str(required=True, validate=Email(
        error='Not a valid email address'))


class UserLoginSchema(Schema):
    username = Str(required=True)
    password = Str(required=True)

    @validates('username')
    def validate_username(self, value: str):
        if not 4 <= len(value) <= 64:
            error_message = {
                'status': 'fail',
                'message': 'No user with given credentials'
            }
            raise HTTPUnauthorized(reason=error_message,
                                   content_type='application/json')

    @validates('password')
    def validate_password(self, value: str):
        if not 6 <= len(value) <= 64:
            error_message = {
                'status': 'fail',
                'message': 'No user with given credentials'
            }
            raise HTTPUnauthorized(reason=error_message,
                                   content_type='application/json')
