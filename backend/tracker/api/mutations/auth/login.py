import graphene

from ..base import BaseMutationPayload
from tracker.api.services import validate_input
from tracker.api.services.auth import (
    check_user_credentials, generate_auth_token
)
from tracker.api.scalars.auth import Username, Password
from tracker.api.schemas.auth import LoginSchema
from tracker.api.status_codes import StatusEnum
from tracker.api.types import UserType


class LoginStatus(graphene.Enum):
    SUCCESS = StatusEnum.SUCCESS.value
    BAD_REQUEST = StatusEnum.BAD_REQUEST.value
    UNAUTHORIZED = StatusEnum.UNAUTHORIZED.value
    ENPROCESSABLE_ENTITY = StatusEnum.ENPROCESSABLE_ENTITY.value

    @property
    def description(self):
        if self == LoginStatus.SUCCESS:
            return 'Successfully logged in'
        elif self == LoginStatus.UNAUTHORIZED:
            return 'Login faild: no user with given credentials'
        elif self == LoginStatus.BAD_REQUEST:
            return 'Login failed: bad request'
        elif self == LoginStatus.ENPROCESSABLE_ENTITY:
            return 'Login failed: invalid input'


class LoginInput(graphene.InputObjectType):
    username = Username(required=True)
    password = Password(required=True)


class LoginPayload(graphene.ObjectType):
    auth_token = graphene.String(required=True)
    record = graphene.Field(UserType, required=True)
    record_id = graphene.Int(required=True)
    status = graphene.Field(LoginStatus, required=True)


class Login(BaseMutationPayload, graphene.Mutation):
    '''Register new user'''

    class Arguments:
        input = LoginInput(required=True)

    login_payload = graphene.Field(LoginPayload, required=True)

    async def mutate(parent, info, input):
        app = info.context['request'].app
        data = validate_input(input, LoginSchema)

        user = await check_user_credentials(app['db'], data)
        auth_token = generate_auth_token(app['config'], user_id=user['id'])

        return Login(
            login_payload=LoginPayload(
                record=user,
                record_id=user['id'],
                auth_token=auth_token,
                status=LoginStatus.SUCCESS,
            )
        )
