import graphene

from ..base import BaseMutationPayload
from tracker.api.services import validate_input
from tracker.api.services.auth import (
    check_if_user_exists, create_user, generate_auth_token
)
from tracker.api.scalars.auth import Email, Password, Username
from tracker.api.schemas.auth import RegistrationSchema
from tracker.api.status_codes import StatusEnum
from tracker.api.types import UserType


class RegisterStatus(graphene.Enum):
    SUCCESS = StatusEnum.SUCCESS.value
    BAD_REQUEST = StatusEnum.BAD_REQUEST.value
    ENPROCESSABLE_ENTITY = StatusEnum.ENPROCESSABLE_ENTITY.value

    @property
    def description(self):
        if self == RegisterStatus.SUCCESS:
            return 'Successfully registered new user'
        elif self == RegisterStatus.BAD_REQUEST:
            return 'Registration failed: bad request'
        elif self == RegisterStatus.ENPROCESSABLE_ENTITY:
            return 'Registration failed: invalid input'


class RegisterInput(graphene.InputObjectType):
    username = Username(required=True)
    email = Email(required=True)
    password = Password(required=True)


class RegisterPayload(graphene.ObjectType):
    auth_token = graphene.String(required=True)
    record = graphene.Field(UserType, required=True)
    record_id = graphene.Int(required=True)
    status = graphene.Field(RegisterStatus, required=True)


class Registration(BaseMutationPayload, graphene.Mutation):
    '''Register new user'''

    class Arguments:
        input = RegisterInput(required=True)

    register_payload = graphene.Field(RegisterPayload, required=True)

    async def mutate(parent, info, input):
        app = info.context['request'].app
        data = validate_input(input, RegistrationSchema)
        await check_if_user_exists(app['db'], data)

        user = await create_user(app['db'], data)
        auth_token = generate_auth_token(app['config'], user['id'])

        return Registration(
            register_payload=RegisterPayload(
                record=user,
                record_id=user['id'],
                auth_token=auth_token,
                status=RegisterStatus.SUCCESS,
            )
        )
