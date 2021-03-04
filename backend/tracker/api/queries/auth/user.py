import graphene
from graphql import ResolveInfo

from tracker.api.types import UserType
from tracker.db.schema import User as UserTable
from tracker.api.wrappers import login_required
from tracker.api.services import get_user_by_id


class UserDetailQuery(graphene.ObjectType):
    user = graphene.Field(
        UserType,
        description='Current auth user detail.',
        required=True
    )

    @login_required
    async def resolve_user(parent, info: ResolveInfo):
        db = info.context['request'].app['db']
        user_id = info.context['request'].get('user_id')

        user = await get_user_by_id(db, user_id)
        return user
