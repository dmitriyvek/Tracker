import graphene

from .create import RoleListCreation
from .delete import RoleDeletion
from .email_confirmation import RoleConfirmation


class RoleRootMutation(graphene.ObjectType):
    role_confirmation = RoleConfirmation.Field()
    role_creation = RoleListCreation.Field()
    role_deletion = RoleDeletion.Field()
