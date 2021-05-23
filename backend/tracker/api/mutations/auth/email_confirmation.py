import graphene
from graphene.types import ResolveInfo

from ..base import BaseMutationPayload
from tracker.api.services.auth import (
    confirm_email, decode_email_confirmation_token,
    generate_auth_token, create_blacklist_token
)
from tracker.api.status_codes import StatusEnum
from tracker.api.types import UserType


class RegisterEmailConfirmationStatus(graphene.Enum):
    SUCCESS = StatusEnum.SUCCESS.value
    BAD_REQUEST = StatusEnum.BAD_REQUEST.value
    ENPROCESSABLE_ENTITY = StatusEnum.ENPROCESSABLE_ENTITY.value

    @property
    def description(self):
        if self == RegisterEmailConfirmationStatus.SUCCESS:
            return 'Successfully confirmed your email'
        elif self == RegisterEmailConfirmationStatus.BAD_REQUEST:
            return 'Confirmation failed: bad request'
        elif self == RegisterEmailConfirmationStatus.ENPROCESSABLE_ENTITY:
            return 'Confirmation failed: invalid input'


class RegisterEmailConfirmationInput(graphene.InputObjectType):
    token = graphene.String(required=True)


class RegisterEmailConfirmationPayload(graphene.ObjectType):
    auth_token = graphene.String(required=True)
    record = graphene.Field(UserType, required=True)
    record_id = graphene.Int(required=True)
    status = graphene.Field(RegisterEmailConfirmationStatus, required=True)


class RegisterEmailConfirmation(BaseMutationPayload, graphene.Mutation):
    '''Confirm user\'s email by given token'''

    class Arguments:
        input = RegisterEmailConfirmationInput(required=True)

    register_email_confirmation_payload = graphene.Field(
        RegisterEmailConfirmationPayload, required=True
    )

    @staticmethod
    async def mutate(
        parent, info: ResolveInfo, input: RegisterEmailConfirmationInput
    ):
        app = info.context['request'].app

        email = await decode_email_confirmation_token(
            db=app['db'],
            config=app['config'],
            token=input['token'],
        )
        user = await confirm_email(db=app['db'], email=email)

        auth_token = generate_auth_token(
            config=app['config'],
            user_id=user['id'],
        )

        await create_blacklist_token(db=app['db'], token=input['token'])

        return RegisterEmailConfirmation(
            register_email_confirmation_payload=RegisterEmailConfirmationPayload(  # noqa: E501
                auth_token=auth_token,
                record=user,
                record_id=user['id'],
                status=RegisterEmailConfirmationStatus.SUCCESS,
            )
        )
