import graphene

from .create import RoleListCreation


class RoleRootMutation(graphene.ObjectType):
    role_creation = RoleListCreation.Field()
