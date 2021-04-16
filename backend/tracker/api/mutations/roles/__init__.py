import graphene

from .create import RoleCreation


class RoleRootMutation(graphene.ObjectType):
    role_creation = RoleCreation.Field()
