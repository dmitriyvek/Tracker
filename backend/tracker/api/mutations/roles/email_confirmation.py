import graphene

from ..base import BaseMutationPayload
from tracker.api.services.auth import (
    confirm_email,
    generate_auth_token, create_blacklist_token
)
from tracker.api.services.roles import (
    check_if_user_exists_by_email,
    create_role,
    decode_role_confirmation_token,
)
from tracker.api.status_codes import StatusEnum
from tracker.api.types.user import UserType


class RoleConfirmationStatus(graphene.Enum):
    SUCCESS = StatusEnum.SUCCESS.value
    MOVED_TEMPORARILY = StatusEnum.MOVED_TEMPORARILY.value
    BAD_REQUEST = StatusEnum.BAD_REQUEST.value
    ENPROCESSABLE_ENTITY = StatusEnum.ENPROCESSABLE_ENTITY.value

    @property
    def description(self):
        if self == RoleConfirmationStatus.SUCCESS:
            return 'Successfully confirmed your role'
        elif self == RoleConfirmationStatus.MOVED_TEMPORARILY:
            return 'Go to given url to create your account'
        elif self == RoleConfirmationStatus.BAD_REQUEST:
            return 'Confirmation failed: bad request'
        elif self == RoleConfirmationStatus.ENPROCESSABLE_ENTITY:
            return 'Confirmation failed: invalid input'


class RoleConfirmationInput(graphene.InputObjectType):
    token = graphene.String(required=True)


class RoleConfirmationPayload(graphene.ObjectType):
    auth_token = graphene.String(required=False)
    record = graphene.Field(UserType, required=False)
    record_id = graphene.Int(required=False)
    status = graphene.Field(RoleConfirmationStatus, required=True)
    next_url = graphene.String(
        required=False,
        description='Go to this url to create your account',
    )


class RoleConfirmation(BaseMutationPayload, graphene.Mutation):
    '''
    Confirm user\'s role creation by given token.
    If user does not have an account returns registration url.
    '''

    class Arguments:
        input = RoleConfirmationInput(required=True)

    role_confirmation_payload = graphene.Field(
        RoleConfirmationPayload, required=True
    )

    @staticmethod
    async def mutate(parent, info, input: RoleConfirmationInput):
        app = info.context['request'].app
        token = input['token']

        token_payload = await decode_role_confirmation_token(
            db=app['db'],
            config=app['config'],
            token=token,
        )

        user = await check_if_user_exists_by_email(
            db=app['db'], email=token_payload.email
        )

        if user:
            auth_token = generate_auth_token(
                config=app['config'], user_id=user['id'],
            )

            async with app['db'].transaction() as conn:
                if not user['is_confirmed']:
                    await confirm_email(
                        db=conn, email=token_payload.email, returning=False
                    )

                await create_role(
                    db=conn, data=token_payload, user_id=user['id']
                )
                await create_blacklist_token(db=conn, token=token)

            return RoleConfirmation(
                role_confirmation_payload=RoleConfirmationPayload(
                    auth_token=auth_token,
                    record=user,
                    record_id=user['id'],
                    status=RoleConfirmationStatus.SUCCESS,
                )
            )

        domain = app['config']['to_smtp_domain']
        next_url = f'{domain}/role/confirmation/register/{token}'

        return RoleConfirmation(
            role_confirmation_payload=RoleConfirmationPayload(
                status=RoleConfirmationStatus.MOVED_TEMPORARILY,
                next_url=next_url
            )
        )
