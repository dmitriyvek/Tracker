import graphene

from .detail import UserDetailQuery


class UsersQuery(graphene.ObjectType):
    detail = graphene.Field(UserDetailQuery)

    def resolve_detail(parent, info):
        return {}
