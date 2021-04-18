import graphene

from ..base import BaseMutationPayload
from tracker.api.services.auth import (
    confirm_email, decode_email_confirmation_token,
    generate_auth_token, create_blacklist_token
)
from tracker.api.status_codes import StatusEnum
from tracker.api.types import UserType


class EmailConfirmationStatus(graphene.Enum):
    SUCCESS = StatusEnum.SUCCESS.value
    BAD_REQUEST = StatusEnum.BAD_REQUEST.value
    ENPROCESSABLE_ENTITY = StatusEnum.ENPROCESSABLE_ENTITY.value

    @property
    def description(self):
        if self == EmailConfirmationStatus.SUCCESS:
            return 'Successfully confirmed your email'
        elif self == EmailConfirmationStatus.BAD_REQUEST:
            return 'Confirmation failed: bad request'
        elif self == EmailConfirmationStatus.ENPROCESSABLE_ENTITY:
            return 'Confirmation failed: invalid input'


class EmailConfirmationInput(graphene.InputObjectType):
    token = graphene.String(required=True)


class EmailConfirmationPayload(graphene.ObjectType):
    auth_token = graphene.String(required=True)
    record = graphene.Field(UserType, required=True)
    record_id = graphene.Int(required=True)
    status = graphene.Field(EmailConfirmationStatus, required=True)


class EmailConfirmation(BaseMutationPayload, graphene.Mutation):
    '''Confirm user\'s emain by given token'''

    class Arguments:
        input = EmailConfirmationInput(required=True)

    email_confirmation_payload = graphene.Field(
        EmailConfirmationPayload, required=True
    )

    @staticmethod
    async def mutate(parent, info, input: EmailConfirmationInput):
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

        await create_blacklist_token(db=app['db'], auth_token=input['token'])

        return EmailConfirmation(
            email_confirmation_payload=EmailConfirmationPayload(
                auth_token=auth_token,
                record=user,
                record_id=user['id'],
                status=EmailConfirmationStatus.SUCCESS,
            )
        )
