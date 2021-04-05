import graphene
from graphene.types import ResolveInfo

from tracker.api.services import validate_input
from tracker.api.services.auth import check_credentials_duplication
from tracker.api.scalars.auth import Username, Email
from tracker.api.schemas.auth import (
    EmailDuplicationCheckSchema, UsernameDuplicationCheckSchema
)


class DuplicationChecksType(graphene.ObjectType):
    username = graphene.Boolean(
        required=True,
        description='Does user with given username exists',
        username=Username(required=True)
    )
    email = graphene.Boolean(
        required=True,
        description='Does user with given email exists',
        email=Email(required=True)
    )

    async def resolve_username(parent, info: ResolveInfo, username):
        db = info.context['request'].app['db']
        data = {'username': username}
        validate_input(data, UsernameDuplicationCheckSchema)

        is_existed = await check_credentials_duplication(db, username=username)
        return is_existed

    async def resolve_email(parent, info: ResolveInfo, email):
        db = info.context['request'].app['db']
        data = {'email': email}
        validate_input(data, EmailDuplicationCheckSchema)

        is_existed = await check_credentials_duplication(db, email=email)
        return is_existed
