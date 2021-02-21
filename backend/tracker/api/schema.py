from marshmallow import Schema, ValidationError, validates, validates_schema
from marshmallow.fields import Dict, Int, List, Nested, Str
from marshmallow.validate import Length, OneOf, Range, Email


class UserRegistrationSchema(Schema):
    username = Str(required=True, validate=Length(min=4, max=64))
    password = Str(required=True, validate=Length(min=6, max=64))
    email = Str(required=True, validate=Email(
        error='Not a valid email address'))
