import graphene
from graphene.types import ResolveInfo

from ..base import BaseMutationPayload
from tracker.api.services import send_email_factory, validate_input
from tracker.api.services.auth import (
    check_if_user_exists, create_user,
    send_auth_confirmation_email
)
from tracker.api.scalars.auth import Email, Password, Username
from tracker.api.schemas.auth import RegistrationSchema
from tracker.api.status_codes import StatusEnum


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
    status = graphene.Field(RegisterStatus, required=True)


class Registration(BaseMutationPayload, graphene.Mutation):
    '''Register new user'''

    class Arguments:
        input = RegisterInput(required=True)

    register_payload = graphene.Field(RegisterPayload, required=True)

    @staticmethod
    async def mutate(parent, info: ResolveInfo, input):
        app = info.context['request'].app
        data = validate_input(input, RegistrationSchema)
        await check_if_user_exists(app['db'], data)

        send_conf_email = \
            send_email_factory(app=app)(send_auth_confirmation_email)
        await send_conf_email(app=app, data=data)

        await create_user(app['db'], data)

        return Registration(
            register_payload=RegisterPayload(
                status=RegisterStatus.SUCCESS,
            )
        )
