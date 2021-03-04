import graphene

from .user import UserDetailQuery


class AuthQuery(graphene.ObjectType):
    detail = graphene.Field(UserDetailQuery)

    def resolve_detail(parent, info):
        return {}
