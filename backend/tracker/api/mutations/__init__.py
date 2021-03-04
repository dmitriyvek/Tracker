import graphene

from .auth import AuthRootMutation


class Mutation(graphene.ObjectType):
    auth = graphene.Field(AuthRootMutation, required=True)

    def resolve_auth(parent, info):
        return {}
