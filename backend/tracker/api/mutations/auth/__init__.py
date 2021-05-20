import graphene

from .email_confirmation import RegisterEmailConfirmation
from .registration import Registration
from .register_by_role_token import RegisterByRoleToken
from .login import Login
from .logout import Logout


class AuthRootMutation(graphene.ObjectType):
    email_confirmation = RegisterEmailConfirmation.Field()
    register = Registration.Field()
    register_by_role_token = RegisterByRoleToken.Field()
    login = Login.Field()
    logout = Logout.Field()
