import graphene

from .create import RoleListCreation
from .email_confirmation import RoleConfirmation


class RoleRootMutation(graphene.ObjectType):
    role_creation = RoleListCreation.Field()
    role_confirmation = RoleConfirmation.Field()
