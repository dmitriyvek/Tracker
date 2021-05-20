import graphene

from ..base import BaseMutationPayload
from tracker.api.services import validate_input
from tracker.api.services.auth import (
    RegisterByRoleTokenData,
    check_if_user_exists,
    create_user_and_role_by_role_token,
    generate_auth_token
)
from tracker.api.services.roles import (
    decode_role_confirmation_token,
)
from tracker.api.scalars.auth import Password, Username
from tracker.api.schemas.auth import RegisterByRoleTokenSchema
from tracker.api.status_codes import StatusEnum
from tracker.api.types.user import UserType


class RegisterByRoleTokenStatus(graphene.Enum):
    SUCCESS = StatusEnum.SUCCESS.value
    BAD_REQUEST = StatusEnum.BAD_REQUEST.value
    ENPROCESSABLE_ENTITY = StatusEnum.ENPROCESSABLE_ENTITY.value

    @property
    def description(self):
        if self == RegisterByRoleTokenStatus.SUCCESS:
            return 'Successfully registered new user and add him in project'
        elif self == RegisterByRoleTokenStatus.BAD_REQUEST:
            return 'Registration failed: bad request'
        elif self == RegisterByRoleTokenStatus.ENPROCESSABLE_ENTITY:
            return 'Registration failed: invalid input'


class RegisterByRoleTokenInput(graphene.InputObjectType):
    token = graphene.String(required=True)
    username = Username(required=True)
    password = Password(required=True)


class RegisterByRoleTokenPayload(graphene.ObjectType):
    auth_token = graphene.String(required=True)
    record = graphene.Field(UserType, required=True)
    record_id = graphene.Int(required=True)
    status = graphene.Field(RegisterByRoleTokenStatus, required=True)


class RegisterByRoleToken(BaseMutationPayload, graphene.Mutation):
    '''Register new user by role creation token.'''

    class Arguments:
        input = RegisterByRoleTokenInput(required=True)

    register_by_role_token_payload = graphene.Field(
        RegisterByRoleTokenPayload, required=True
    )

    @staticmethod
    async def mutate(parent, info, input):
        app = info.context['request'].app
        data = validate_input(input, RegisterByRoleTokenSchema)
        token_payload = await decode_role_confirmation_token(
            db=app['db'],
            config=app['config'],
            token=input['token']
        )

        await check_if_user_exists(
            app['db'], data={
                'username': input['username'],
                'email': token_payload.email
            }
        )

        data = RegisterByRoleTokenData(
            email=token_payload.email,
            project_id=token_payload.project_id,
            role=token_payload.role,
            assign_by=token_payload.assign_by,
            username=input['username'],
            password=input['password'],
        )

        user = await create_user_and_role_by_role_token(app['db'], data)
        auth_token = generate_auth_token(
            config=app['config'], user_id=user['id']
        )

        return RegisterByRoleToken(
            register_by_role_token_payload=RegisterByRoleTokenPayload(
                auth_token=auth_token,
                record=user,
                record_id=user['id'],
                status=RegisterByRoleTokenStatus.SUCCESS,
            )
        )
