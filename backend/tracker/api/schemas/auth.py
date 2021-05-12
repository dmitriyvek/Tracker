from marshmallow import Schema, validates
from marshmallow.fields import Str
from marshmallow.validate import Length, Email

from tracker.api.errors import APIException
from tracker.api.status_codes import StatusEnum


class RegistrationSchema(Schema):
    username = Str(required=True, validate=Length(min=4, max=32))
    password = Str(required=True, validate=Length(min=8, max=32))
    email = Str(required=True, validate=Email(
        error='Not a valid email address'))


class EmailDuplicationCheckSchema(Schema):
    email = Str(required=True, validate=Email(
        error='Not a valid email address'))


class UsernameDuplicationCheckSchema(Schema):
    username = Str(required=True, validate=Length(min=4, max=32))


class LoginSchema(Schema):
    username = Str(required=True)
    password = Str(required=True)

    @validates('username')
    def validate_username(self, value: str):
        if not 4 <= len(value) <= 32:
            raise APIException('No user with given credentials.',
                               status=StatusEnum.UNAUTHORIZED.name)

    @validates('password')
    def validate_password(self, value: str):
        if not 8 <= len(value) <= 32:
            raise APIException('No user with given credentials.',
                               status=StatusEnum.UNAUTHORIZED.name)
