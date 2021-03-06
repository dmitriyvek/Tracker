from graphql_relay import from_global_id
from marshmallow import Schema, validates
from marshmallow.fields import Str, List
from marshmallow.validate import OneOf, Email, Length

from tracker.api.errors import APIException
from tracker.api.status_codes import StatusEnum
from tracker.db.schema import UserRoleEnum
from tracker.utils.settings import MAIN_CONFIG


class RoleBaseSchema(Schema):
    # min project_id lenght = len(to_global_id('ProjectType', 1))
    project_id = Str(required=True, validate=Length(min=20))

    @validates('project_id')
    def validate_project_id(self, value: str):
        try:
            values = from_global_id(value)
            if values[0] != 'ProjectType' or int(values[1]) <= 0:
                raise ValueError
        except ValueError:
            raise APIException('Invalid project id provided',
                               status=StatusEnum.ENPROCESSABLE_ENTITY.name)


class RoleCreationSchema(RoleBaseSchema):
    role = Str(required=True, validate=OneOf(
        list(UserRoleEnum.__members__.keys())))
    email_list = List(
        Str(
            required=True,
            validate=Email(
                error='not a valid email'
            )
        ),
        required=True,
        validate=Length(max=MAIN_CONFIG['mail_max_letters_number'])
    )


class RoleDuplicationCheckSchema(RoleBaseSchema):
    user_id = Str(required=True)

    @validates('user_id')
    def validate_user_id(self, value: str):
        try:
            values = from_global_id(value)
            if values[0] != 'UserType' or int(values[1]) <= 0:
                raise ValueError
        except ValueError:
            raise APIException('Invalid user id provided',
                               status=StatusEnum.ENPROCESSABLE_ENTITY.name)


class RoleDeletionSchema(Schema):
    role_id = Str(required=True)

    @validates('role_id')
    def validate_role_id(self, value: str):
        try:
            values = from_global_id(value)
            if values[0] != 'RoleType' or int(values[1]) <= 0:
                raise ValueError
        except ValueError:
            raise APIException('Invalid role id provided',
                               status=StatusEnum.ENPROCESSABLE_ENTITY.name)
