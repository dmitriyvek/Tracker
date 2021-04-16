from graphql_relay import from_global_id
from marshmallow import Schema, validates
from marshmallow.fields import Str, Int
from marshmallow.validate import OneOf

from tracker.api.errors import APIException
from tracker.api.status_codes import StatusEnum
from tracker.db.schema import UserRoleEnum


def validate_user_id(user_id: str):
    try:
        values = from_global_id(user_id)
        if values[0] != 'UserType' or int(values[1]) <= 0:
            raise
    except:
        raise APIException('Invalid user id provided',
                           status=StatusEnum.ENPROCESSABLE_ENTITY.name)


def validate_project_id(project_id: str):
    try:
        values = from_global_id(project_id)
        if values[0] != 'ProjectType' or int(values[1]) <= 0:
            raise
    except:
        raise APIException('Invalid project id provided',
                           status=StatusEnum.ENPROCESSABLE_ENTITY.name)


class RoleBaseSchemaSchema(Schema):
    user_id = Str(required=True)
    project_id = Str(required=True)

    @validates('user_id')
    def validate_user_id(self, value: str):
        validate_user_id(value)

    @validates('project_id')
    def validate_project_id(self, value: str):
        validate_project_id(value)


class RoleCreationSchema(RoleBaseSchemaSchema):
    role = Str(required=True, validate=OneOf(
        list(UserRoleEnum.__members__.keys())))


class RoleDuplicationCheckSchema(RoleBaseSchemaSchema):
    pass
