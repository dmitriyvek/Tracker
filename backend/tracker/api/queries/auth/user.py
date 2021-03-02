import graphene
from graphql import ResolveInfo

from tracker.api.types import UserType
from tracker.db.schema import User as UserTable


class UserQuery(graphene.ObjectType):
    user_list = graphene.List(
        UserType,
        description='All registered users.',
        required=True
    )

    async def resolve_user_list(parent, info: ResolveInfo):
        app = info.context['request'].app
        query = UserTable.select().with_only_columns(
            [UserTable.c.id, UserTable.c.username,
             UserTable.c.email, UserTable.c.registered_at
             ])
        result = await app['db'].query(query)
        result = list(map(dict, result))
        return result
