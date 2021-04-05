from marshmallow import Schema, validates
from marshmallow.fields import Dict, Int, List, Nested, Str
from marshmallow.validate import Length, OneOf, Range, Email

from tracker.api.errors import APIException
from tracker.api.status_codes import StatusEnum


class RegistrationSchema(Schema):
    username = Str(required=True, validate=Length(min=4, max=64))
    password = Str(required=True, validate=Length(min=6, max=64))
    email = Str(required=True, validate=Email(
        error='Not a valid email address'))


class EmailDuplicationCheckSchema(Schema):
    email = Str(required=True, validate=Email(
        error='Not a valid email address'))
        

class UsernameDuplicationCheckSchema(Schema):
    username = Str(required=True, validate=Length(min=4, max=64))


class LoginSchema(Schema):
    username = Str(required=True)
    password = Str(required=True)

    @validates('username')
    def validate_username(self, value: str):
        if not 4 <= len(value) <= 64:
            raise APIException('No user with given credentials.',
                               status=StatusEnum.UNAUTHORIZED.name)

    @validates('password')
    def validate_password(self, value: str):
        if not 6 <= len(value) <= 64:
            raise APIException('No user with given credentials.',
                               status=StatusEnum.UNAUTHORIZED.name)
